"""
Whisper Audio Transcription Tool

Usage:
    python transcribe.py <audio_file> [options]

Examples:
    python transcribe.py audio.mp3
    python transcribe.py audio.mp3 --model medium --language en
    python transcribe.py audio.mp3 -m large -l auto -o output.txt
"""

import whisper
import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path
from datetime import datetime


def find_ffmpeg():
    """Automatically find ffmpeg in system."""
    # Check if ffmpeg is already in PATH
    ffmpeg_path = shutil.which("ffmpeg")
    if ffmpeg_path:
        return os.path.dirname(ffmpeg_path)

    # Try to find using 'where' command on Windows
    if sys.platform == "win32":
        try:
            result = subprocess.run(
                ["where", "ffmpeg"],
                capture_output=True,
                text=True,
                check=True
            )
            ffmpeg_location = result.stdout.strip().split('\n')[0]
            return os.path.dirname(ffmpeg_location)
        except (subprocess.CalledProcessError, FileNotFoundError):
            pass

    # Common installation paths
    common_paths = [
        r"C:\ProgramData\chocolatey\bin",
        r"C:\ffmpeg\bin",
        r"C:\Program Files\ffmpeg\bin",
        r"C:\Program Files (x86)\ffmpeg\bin"
    ]

    for path in common_paths:
        if os.path.exists(os.path.join(path, "ffmpeg.exe")):
            return path

    return None


# Setup ffmpeg
ffmpeg_dir = find_ffmpeg()
if ffmpeg_dir:
    os.environ["PATH"] = ffmpeg_dir + os.pathsep + os.environ["PATH"]
else:
    print("Warning: ffmpeg not found")
    print("Install with: choco install ffmpeg")
    print("Or download from: https://www.gyan.dev/ffmpeg/builds/")
    print()


def validate_audio_file(file_path):
    """Validate audio file existence and format."""
    supported_formats = {'.mp3', '.mp4', '.m4a', '.wav', '.flac', '.ogg', '.opus', '.webm'}

    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    file_ext = Path(file_path).suffix.lower()
    if file_ext not in supported_formats:
        print(f"Error: Unsupported format: {file_ext}")
        print(f"Supported formats: {', '.join(supported_formats)}")
        return False

    return True


def transcribe_audio(audio_path, model_size="base", language="pl", verbose=True):
    """
    Transcribe audio file using Whisper.

    Args:
        audio_path: Path to audio file
        model_size: Model size (tiny, base, small, medium, large)
        language: Language code or 'auto' for auto-detection
        verbose: Show detailed progress

    Returns:
        Transcribed text or None on error
    """
    try:
        if verbose:
            print(f"Loading Whisper model '{model_size}'...")

        model = whisper.load_model(model_size)

        if verbose:
            print(f"Transcribing: {Path(audio_path).name}")

        transcribe_options = {
            "verbose": False,
            "fp16": False
        }

        if language and language.lower() != "auto":
            transcribe_options["language"] = language

        start_time = datetime.now()
        result = model.transcribe(audio_path, **transcribe_options)
        end_time = datetime.now()

        duration = (end_time - start_time).total_seconds()

        if verbose:
            print(f"Completed in {duration:.2f} seconds")

        return result["text"].strip()

    except Exception as e:
        print(f"Error during transcription: {str(e)}")
        return None


def save_transcription(text, audio_path, output_path=None):
    """Save transcription to file."""
    if output_path is None:
        # Create transcriptions directory if it doesn't exist
        transcriptions_dir = Path("transcriptions")
        transcriptions_dir.mkdir(exist_ok=True)

        # Generate output filename
        filename = Path(audio_path).stem + '_whisper.txt'
        output_path = transcriptions_dir / filename

    try:
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)

        print(f"Saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error saving file: {str(e)}")
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Transcribe audio files using Whisper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s audio.mp3
  %(prog)s audio.mp3 --model medium --language en
  %(prog)s audio.mp3 -m large -l auto -o output.txt
  
Model sizes:
  tiny   - Fastest, least accurate (~1GB RAM)
  base   - Balanced (default) (~1GB RAM)
  small  - Good quality (~2GB RAM)
  medium - Very good quality (~5GB RAM)
  large  - Best quality (~10GB RAM)
        """
    )

    parser.add_argument(
        'audio_file',
        type=str,
        help='Path to audio file'
    )

    parser.add_argument(
        '-m', '--model',
        type=str,
        default='base',
        choices=['tiny', 'base', 'small', 'medium', 'large'],
        help='Whisper model size (default: base)'
    )

    parser.add_argument(
        '-l', '--language',
        type=str,
        default='pl',
        help='Language code (e.g. pl, en, de) or "auto" (default: pl)'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file path (default: filename_transcript.txt)'
    )

    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help='Quiet mode - output only the result'
    )

    return parser.parse_args()


def main():
    """Main program function."""
    args = parse_arguments()

    if not validate_audio_file(args.audio_file):
        sys.exit(1)

    if not args.quiet:
        print(f"File: {args.audio_file}")
        print(f"Model: {args.model}")
        print(f"Language: {args.language}")
        print()

    text = transcribe_audio(
        args.audio_file,
        model_size=args.model,
        language=args.language,
        verbose=not args.quiet
    )

    if text is None:
        sys.exit(1)

    if not args.quiet:
        print("\nTranscription:")
        print("-" * 70)

    print(text)

    if not args.quiet:
        print("-" * 70)
        print()

    save_transcription(text, args.audio_file, args.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)