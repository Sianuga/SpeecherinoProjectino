import os
import sys
import csv
import time
import re
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
from jiwer import wer, cer

# =============================
# KONFIGURACJA
# =============================

ELEVEN_API_KEY =
if not ELEVEN_API_KEY:
    print("❌ Error: Please set the environment variable ELEVENLABS_API_KEY")
    sys.exit(1)

ELEVEN_ENDPOINT = "https://api.elevenlabs.io/v1/speech-to-text"
MODEL_ID = "scribe_v1"
TEXT_DIR = Path("../Data/Text")

SUPPORTED_FORMATS = {".mp3", ".mp4", ".m4a", ".wav", ".flac", ".ogg", ".opus", ".webm"}


# =============================
# FUNKCJE POMOCNICZE
# =============================

def read_text_file(path):
    """Czyta zawartość pliku tekstowego."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None


def get_text_filename(audio_name):
    """Dopasowuje nazwę pliku tekstowego do pliku audio."""
    base = os.path.basename(audio_name)
    num = base.replace("Audio_", "").replace(".m4a", "")
    num = num.split("_")[0]
    return f"Text_{num}.txt"


def calculate_ser(reference, hypothesis):
    """Oblicza Sentence Error Rate (SER)."""
    ref_sentences = [s.strip() for s in re.split(r"[.!?]", reference) if s.strip()]
    hyp_sentences = [s.strip() for s in re.split(r"[.!?]", hypothesis) if s.strip()]

    errors = sum(1 for r, h in zip(ref_sentences, hyp_sentences) if r != h)
    errors += abs(len(ref_sentences) - len(hyp_sentences))
    total = max(len(ref_sentences), 1)
    return (errors / total) * 100


def transcribe_with_elevenlabs(audio_path, language=None):
    """Wysyła plik audio do ElevenLabs STT API i zwraca transkrypcję."""
    headers = {"xi-api-key": ELEVEN_API_KEY}

    data = {
        "model_id": MODEL_ID
    }
    if language:
        data["language_code"] = language

    with open(audio_path, "rb") as f:
        files = {"file": (audio_path.name, f, "application/octet-stream")}

        start = time.time()
        resp = requests.post(ELEVEN_ENDPOINT, headers=headers, data=data, files=files)
        duration = time.time() - start

    if resp.status_code != 200:
        raise Exception(f"API Error {resp.status_code}: {resp.text}")

    resp_json = resp.json()
    text = resp_json.get("text", "").strip()
    detected_lang = resp_json.get("detected_language", language or "auto")
    return text, detected_lang, duration


# =============================
# GŁÓWNY PROGRAM
# =============================

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Batch transcribe audio files using ElevenLabs STT and compute WER/CER/SER."
    )
    parser.add_argument("input_folder", type=str, help="Folder z plikami audio")
    parser.add_argument("output_file", type=str, help="Ścieżka do pliku wynikowego CSV")
    parser.add_argument("-l", "--language", type=str, default=None, help="Kod języka (np. pl, en)")
    args = parser.parse_args()

    input_path = Path(args.input_folder)
    output_csv_path = Path(args.output_file)

    if not input_path.is_dir():
        print(f"❌ Error: Folder nie istnieje: {args.input_folder}")
        sys.exit(1)

    audio_files = [p for p in input_path.iterdir() if p.suffix.lower() in SUPPORTED_FORMATS]
    if not audio_files:
        print(f"❌ Brak obsługiwanych plików audio w {args.input_folder}")
        sys.exit(0)

    print(f"🎧 Znaleziono {len(audio_files)} plików audio.")
    print(f"📦 Wyniki zostaną zapisane do: {output_csv_path}")
    print("-" * 70)

    records = []

    for audio_path in audio_files:
        print(f"🔊 Transkrypcja: {audio_path.name} ...")
        try:
            transcription, detected_lang, duration = transcribe_with_elevenlabs(audio_path, args.language)
            print(f"✅ Zakończono w {duration:.2f}s")

            text_file = TEXT_DIR / get_text_filename(audio_path.name)
            reference = read_text_file(text_file)

            if not reference:
                print(f"⚠️ Brak pliku oryginalnego: {text_file.name}")
                wer_score = cer_score = ser_score = None
            else:
                wer_score = round(wer(reference, transcription) * 100, 2)
                cer_score = round(cer(reference, transcription) * 100, 2)
                ser_score = round(calculate_ser(reference, transcription), 2)

            records.append({
                "Model": MODEL_ID,
                "File": audio_path.name,
                "Language": detected_lang,
                "Time (s)": f"{duration:.2f}",
                "Transcription": transcription,
                "Original": reference or "",
                "WER": wer_score,
                "CER": cer_score,
                "SER": ser_score
            })

        except Exception as e:
            print(f"❌ Błąd podczas transkrypcji: {e}")
            records.append({
                "Model": MODEL_ID,
                "File": audio_path.name,
                "Language": args.language or "auto",
                "Time (s)": "ERROR",
                "Transcription": str(e),
                "Original": "",
                "WER": None,
                "CER": None,
                "SER": None
            })

    # Zapisz wyniki
    df = pd.DataFrame(records)
    df.to_csv(output_csv_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"\n✅ Wyniki zapisane do pliku: {output_csv_path}")


if __name__ == "__main__":
    main()
