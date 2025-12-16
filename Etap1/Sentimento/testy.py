import pandas as pd
from transformers import pipeline
import sys
import os
import time

# ==========================================
# KONFIGURACJA / CONFIGURATION
# ==========================================

# Lista plików do przetworzenia
INPUT_FILES = [
    "opinie-oczywiste.csv",
    "opinie-nieoczywiste.csv"
]

TEXT_COLUMN = "tresc"  # Nazwa kolumny z tekstem w plikach CSV

# Lista modeli do użycia
# Format: {"Nazwa_Wlasna": "Nazwa_HuggingFace"}
MODELS_CONFIG = {
    "ROBERTA": "cardiffnlp/twitter-xlm-roberta-base-sentiment",
    "HERBERT": "Voicelab/herbert-base-cased-sentiment"
}


# ==========================================
# FUNKCJE / FUNCTIONS
# ==========================================

def load_models(config):
    """
    Ładuje wszystkie modele zdefiniowane w konfiguracji do słownika.
    """
    loaded_pipelines = {}
    print("\n--> Rozpoczynam ładowanie modeli (to może chwilę potrwać)...")

    for friendly_name, model_path in config.items():
        print(f"    ...ładowanie {friendly_name} ({model_path})...")
        try:
            # Tworzymy pipeline
            pipe = pipeline(
                "sentiment-analysis",
                model=model_path,
                tokenizer=model_path
            )
            loaded_pipelines[friendly_name] = pipe
            print(f"    --> {friendly_name} gotowy.")
        except Exception as e:
            print(f"    !!! Błąd ładowania {friendly_name}: {e}")
            sys.exit(1)

    return loaded_pipelines


def analyze_text_with_timer(pipe, text):
    """
    Analizuje jeden tekst i mierzy czas wykonania.
    Zwraca: (etykieta, pewność, czas_w_sekundach)
    """
    if pd.isna(text) or str(text).strip() == "":
        return "n/a", 0.0, 0.0

    # Przycinanie do 512 znaków dla bezpieczeństwa
    clean_text = str(text)[:512]

    start_time = time.perf_counter()  # Start zegara (precyzyjny)
    try:
        result = pipe(clean_text)[0]
        end_time = time.perf_counter()  # Stop zegara

        duration = end_time - start_time
        return result['label'], result['score'], duration

    except Exception as e:
        end_time = time.perf_counter()
        print(f"Błąd analizy tekstu: {e}")
        return "error", 0.0, (end_time - start_time)


def process_single_file(filepath, pipelines):
    """
    Przetwarza jeden plik CSV wszystkimi dostępnymi modelami.
    """
    print(f"\n--> Przetwarzanie pliku: {filepath}")

    if not os.path.exists(filepath):
        print(f"!!! Plik {filepath} nie istnieje. Pomijam.")
        return

    try:
        df = pd.read_csv(filepath)
    except Exception as e:
        print(f"!!! Błąd odczytu pliku: {e}")
        return

    if TEXT_COLUMN not in df.columns:
        print(f"!!! Brak kolumny '{TEXT_COLUMN}' w pliku {filepath}. Pomijam.")
        return

    total_rows = len(df)
    print(f"    Liczba wierszy: {total_rows}")

    # Dla każdego modelu w słowniku pipelines
    for model_name, pipe in pipelines.items():
        print(f"    -> Analiza modelem: {model_name}...")

        # Listy na wyniki
        labels = []
        scores = []
        times = []

        for i, text in enumerate(df[TEXT_COLUMN]):
            # Analiza
            lbl, scr, dur = analyze_text_with_timer(pipe, text)

            labels.append(lbl)
            scores.append(scr)
            times.append(dur)

            # Pasek postępu co 5 wierszy
            if i % 5 == 0:
                sys.stdout.write(f"\r       Postęp: {i}/{total_rows}")
                sys.stdout.flush()

        print(f"\r       Postęp: {total_rows}/{total_rows} - Zakończono.")

        # Dodajemy kolumny do DataFrame
        # Np. ROBERTA_label, ROBERTA_score, ROBERTA_time_sec
        df[f'{model_name}_label'] = labels
        df[f'{model_name}_score'] = scores
        df[f'{model_name}_time_sec'] = times

    # Zapis wyników
    output_filename = f"wyniki_{filepath}"
    try:
        df.to_csv(output_filename, index=False)
        print(f"--> Sukces! Zapisano wyniki do: {output_filename}")
    except Exception as e:
        print(f"!!! Błąd zapisu pliku: {e}")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Załaduj modele raz (żeby nie ładować ich dla każdego pliku od nowa)
    pipelines = load_models(MODELS_CONFIG)

    # 2. Przeiteruj przez listę plików
    for input_file in INPUT_FILES:
        process_single_file(input_file, pipelines)

    print("\n==========================================")
    print("Wszystkie zadania zakończone.")
    print("==========================================")