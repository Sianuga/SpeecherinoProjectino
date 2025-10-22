import pandas as pd
import os
from pathlib import Path
from jiwer import wer, cer

# =============================
# Pomocnicze funkcje
# =============================

def read_text_file(path):
    """Czyta zawartość pliku tekstowego."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception:
        return None

def calculate_ser(reference, hypothesis):
    """Oblicza Sentence Error Rate (SER)."""
    ref_sentences = [s.strip() for s in reference.split('.') if s.strip()]
    hyp_sentences = [s.strip() for s in hypothesis.split('.') if s.strip()]

    errors = sum(1 for r, h in zip(ref_sentences, hyp_sentences) if r != h)
    errors += abs(len(ref_sentences) - len(hyp_sentences))
    total = max(len(ref_sentences), 1)
    return (errors / total) * 100

def get_text_filename(audio_name):
    """
    Na podstawie nazwy audio (np. Audio_1.m4a, Audio_1_1.m4a)
    zwraca nazwę pliku tekstowego (np. Text_1.txt).
    """
    base = os.path.basename(audio_name)
    num = base.replace("Audio_", "").replace(".m4a", "")
    num = num.split("_")[0]  # Audio_1_1 -> 1
    return f"Text_{num}.txt"

# =============================
# Główna logika programu
# =============================

def main():
    csv_path = "results.csv"
    text_dir = Path("../Data/Text")

    # Wczytaj dane
    df = pd.read_csv(csv_path, sep=';')

    original_texts = []
    wers, cers, sers = [], [], []

    for idx, row in df.iterrows():
        audio_file = row["File"]
        transcription = str(row["Transcription"]).strip()

        text_file = text_dir / get_text_filename(audio_file)
        reference = read_text_file(text_file)

        if reference is None:
            original_texts.append("")
            wers.append(None)
            cers.append(None)
            sers.append(None)
            continue

        wer_score = wer(reference, transcription) * 100
        cer_score = cer(reference, transcription) * 100
        ser_score = calculate_ser(reference, transcription)

        original_texts.append(reference)
        wers.append(round(wer_score, 2))
        cers.append(round(cer_score, 2))
        sers.append(round(ser_score, 2))

    # Dodaj kolumny
    df["Original"] = original_texts
    df["WER"] = wers
    df["CER"] = cers
    df["SER"] = sers

    # Zapisz do nowego pliku
    output_path = "results_with_metrics.csv"
    df.to_csv(output_path, sep=';', index=False, encoding='utf-8-sig')
    print(f"✅ Zapisano wynik do pliku: {output_path}")

if __name__ == "__main__":
    main()
