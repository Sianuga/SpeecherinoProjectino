"""
Whisper Batch Audio Transcription Tool

Usage:
    python batch_transcribe.py <input_folder> <output_csv_file> [options]

Example:
    python batch_transcribe.py ./audio_files results.csv -m base medium -l pl
"""

import whisper
import os
import sys
import argparse
import shutil
import subprocess
from pathlib import Path
from datetime import datetime
import torch
import csv

# Sprawdzenie dostępności CUDA
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
print(f"Using device: {DEVICE}")
if DEVICE == "cpu":
    print("Warning: CUDA not available. Transcription will be much slower.")


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
                check=True,
                encoding='utf-8',
                errors='ignore'
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
    print(f"Found ffmpeg in: {ffmpeg_dir}")
else:
    print("Warning: ffmpeg not found.")
    print("Please install ffmpeg and ensure it's in your system's PATH.")
    print("Install with (Windows): choco install ffmpeg")
    print("Or download from: https://www.gyan.dev/ffmpeg/builds/")
    print()


def parse_arguments():
    """Parse command line arguments for batch processing."""
    parser = argparse.ArgumentParser(
        description='Batch transcribe audio files from a folder using Whisper',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s ./my_audio results.csv
  %(prog)s C:\\Audio\\Samples report.csv -l pl -m base medium
  %(prog)s ./audio_files results.csv --models tiny base small medium large

Model sizes:
  tiny   - Fastest, least accurate (~1GB VRAM)
  base   - Balanced (~1GB VRAM)
  small  - Good quality (~2GB VRAM)
  medium - Very good quality (~5GB VRAM)
  large  - Best quality (~10GB VRAM)
        """
    )

    parser.add_argument(
        'input_folder',
        type=str,
        help='Path to the folder containing audio files'
    )

    parser.add_argument(
        'output_file',
        type=str,
        help='Path to the output CSV file (e.g., results.csv)'
    )

    parser.add_argument(
        '-m', '--models',
        nargs='+',  
        default=['base', 'medium', 'large'],
        choices=['tiny', 'base', 'small', 'medium', 'large', 'large-v1', 'large-v2', 'large-v3'],
        help='List of Whisper model sizes to test (default: base medium large)'
    )

    parser.add_argument(
        '-l', '--language',
        type=str,
        default='pl',
        help='Language code (e.g. pl, en, de) or "auto" (default: pl)'
    )

    return parser.parse_args()


def main():
    """Main program function for batch transcription."""
    args = parse_arguments()

    input_path = Path(args.input_folder)
    output_csv_path = Path(args.output_file)

    if not input_path.is_dir():
        print(f"Error: Input folder not found: {args.input_folder}")
        sys.exit(1)

    # Znajdź pliki audio
    supported_formats = {'.mp3', '.mp4', '.m4a', '.wav', '.flac', '.ogg', '.opus', '.webm'}
    audio_files = []
    for file_path in input_path.glob("*"):
        if file_path.suffix.lower() in supported_formats:
            audio_files.append(file_path)

    if not audio_files:
        print(f"No supported audio files found in {args.input_folder}")
        sys.exit(0)

    print(f"Found {len(audio_files)} audio file(s) to process.")
    print(f"Models to run: {', '.join(args.models)}")
    print(f"Results will be saved to: {output_csv_path}")
    print("-" * 70)

    # Przygotuj plik CSV
    try:
        with open(output_csv_path, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            # Zapisz nagłówek
            writer.writerow(["Model", "File", "Language", "Time (s)", "Transcription"])
    except IOError as e:
        print(f"Error: Could not write to output file: {e}")
        sys.exit(1)

    # Główna pętla
    for model_size in args.models:
        print(f"Loading Whisper model '{model_size}'...")
        try:
            model_load_start = datetime.now()
            model = whisper.load_model(model_size, device=DEVICE)
            model_load_end = datetime.now()
            load_duration = (model_load_end - model_load_start).total_seconds()
            print(f"Model '{model_size}' loaded in {load_duration:.2f}s")
        except Exception as e:
            print(f"Error loading model {model_size}: {e}")

            with open(output_csv_path, 'a', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerow([model_size, "N/A", args.language, "ERROR", f"Failed to load model: {e}"])
            continue  
        
        for i in range(3):

            for audio_path in audio_files:
                print(f"  Transcribing: {audio_path.name} (with {model_size})...")
                
                transcribe_options = {
                    "verbose": False,
                    "fp16": False if DEVICE == "cpu" else True
                }

                if args.language and args.language.lower() != "auto":
                    transcribe_options["language"] = args.language

                try:
                    start_time = datetime.now()
                    result = model.transcribe(str(audio_path), **transcribe_options)
                    end_time = datetime.now()

                    duration = (end_time - start_time).total_seconds()
                    transcription_text = result["text"].strip()
                    detected_language = result.get("language", args.language)

                    print(f"    ...done in {duration:.2f}s")

                    # Zapisz wynik do CSV
                    with open(output_csv_path, 'a', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f, delimiter=';')
                        writer.writerow([model_size, audio_path.name, detected_language, f"{duration:.2f}", transcription_text])

                except Exception as e:
                    print(f"    ...Error during transcription: {e}")
                    # Zapisz błąd do CSV
                    with open(output_csv_path, 'a', encoding='utf-8', newline='') as f:
                        writer = csv.writer(f, delimiter=';')
                        writer.writerow([model_size, audio_path.name, args.language, "ERROR", str(e)])

        
        
        print(f"Finished all files for model '{model_size}'.")
        print("-" * 70)

    print("Batch transcription complete.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"An unexpected error occurred: {str(e)}")
        sys.exit(1)
