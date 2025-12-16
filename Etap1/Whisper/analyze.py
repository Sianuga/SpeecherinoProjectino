"""
Whisper Transcription Analysis Tool

Usage:
    python analyze.py <reference_file> <hypothesis_file> [options]

Examples:
    python analyze.py original.txt transcription_whisper.txt
    python analyze.py original.txt transcription_whisper.txt -o custom_results.txt
"""

import sys
import argparse
from pathlib import Path
from jiwer import wer, cer
from datetime import datetime


def read_text_file(file_path):
    """Read text file content."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read().strip()
    except Exception as e:
        print(f"Error reading file {file_path}: {str(e)}")
        return None


def calculate_wer(reference, hypothesis):
    """Calculate Word Error Rate."""
    return wer(reference, hypothesis) * 100


def calculate_cer(reference, hypothesis):
    """Calculate Character Error Rate."""
    return cer(reference, hypothesis) * 100


def calculate_ser(reference, hypothesis):
    """Calculate Sentence Error Rate."""
    ref_sentences = [s.strip() for s in reference.split('.') if s.strip()]
    hyp_sentences = [s.strip() for s in hypothesis.split('.') if s.strip()]

    errors = sum(1 for r, h in zip(ref_sentences, hyp_sentences) if r != h)
    errors += abs(len(ref_sentences) - len(hyp_sentences))

    total = max(len(ref_sentences), 1)
    return (errors / total) * 100


def analyze_transcription(reference, hypothesis):
    """Perform complete analysis of transcription."""
    results = {
        'wer': calculate_wer(reference, hypothesis),
        'cer': calculate_cer(reference, hypothesis),
        'ser': calculate_ser(reference, hypothesis),
        'ref_words': len(reference.split()),
        'hyp_words': len(hypothesis.split()),
        'ref_chars': len(reference),
        'hyp_chars': len(hypothesis)
    }

    return results


def format_results(results, ref_file, hyp_file):
    """Format analysis results as text."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    output = []
    output.append("=" * 70)
    output.append("WHISPER TRANSCRIPTION ANALYSIS RESULTS")
    output.append("=" * 70)
    output.append(f"\nAnalysis Date: {timestamp}")
    output.append(f"Reference File: {ref_file}")
    output.append(f"Hypothesis File: {hyp_file}")
    output.append("\n" + "-" * 70)
    output.append("ERROR METRICS")
    output.append("-" * 70)
    output.append(f"Word Error Rate (WER):      {results['wer']:.2f}%")
    output.append(f"Character Error Rate (CER): {results['cer']:.2f}%")
    output.append(f"Sentence Error Rate (SER):  {results['ser']:.2f}%")
    output.append("\n" + "-" * 70)
    output.append("STATISTICS")
    output.append("-" * 70)
    output.append(f"Reference - Words: {results['ref_words']}, Characters: {results['ref_chars']}")
    output.append(f"Hypothesis - Words: {results['hyp_words']}, Characters: {results['hyp_chars']}")
    output.append("=" * 70)

    return "\n".join(output)


def save_results(content, output_path):
    """Save results to file."""
    try:
        # Create results directory if it doesn't exist
        results_dir = Path("results")
        results_dir.mkdir(exist_ok=True)

        if output_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = results_dir / f"analysis_{timestamp}.txt"
        else:
            output_path = results_dir / Path(output_path).name

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"\nResults saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"Error saving results: {str(e)}")
        return None


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Analyze Whisper transcription quality',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s original.txt transcription_whisper.txt
  %(prog)s original.txt transcription_whisper.txt -o my_results.txt

Metrics:
  WER - Word Error Rate: Percentage of word-level errors
  CER - Character Error Rate: Percentage of character-level errors
  SER - Sentence Error Rate: Percentage of sentence-level errors
        """
    )

    parser.add_argument(
        'reference',
        type=str,
        help='Path to reference (original) text file'
    )

    parser.add_argument(
        'hypothesis',
        type=str,
        help='Path to hypothesis (Whisper transcription) text file'
    )

    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Output file name (saved in results/ directory)'
    )

    return parser.parse_args()


def main():
    """Main program function."""
    args = parse_arguments()

    print("Reading files...")
    reference = read_text_file(args.reference)
    hypothesis = read_text_file(args.hypothesis)

    if reference is None or hypothesis is None:
        sys.exit(1)

    print("Analyzing transcription...")
    results = analyze_transcription(reference, hypothesis)

    formatted_results = format_results(
        results,
        args.reference,
        args.hypothesis
    )

    print("\n" + formatted_results)

    save_results(formatted_results, args.output)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error: {str(e)}")
        sys.exit(1)