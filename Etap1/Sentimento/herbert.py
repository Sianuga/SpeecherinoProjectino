import pandas as pd
from transformers import pipeline
import sys
import os

# ==========================================
# KONFIGURACJA / CONFIGURATION
# ==========================================
MODE = 'file'  # Opcje: 'single' (test tekstu) lub 'file' (analiza pliku CSV)
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
# Tekst do testów (gdy MODE = 'single')
TEST_TEXT = "Ten system działa naprawdę świetnie, jestem pod wrażeniem!"

# Pliki wejściowe i wyjściowe (gdy MODE = 'file')
INPUT_FILE = "opinie-oczywiste.csv"  # Plik z danymi
TEXT_COLUMN = "tresc"            # Nazwa kolumny z tekstem
OUTPUT_FILE = "wyniki_herbert-o.csv" # Plik wynikowy (inna nazwa niż poprzednio)

# --- MODEL SELECTION ---
# Using the specific Polish model requested:
MODEL_NAME = "Voicelab/herbert-base-cased-sentiment"

# ==========================================
# CORE FUNCTIONS
# ==========================================

def load_sentiment_pipeline():
    """
    Initializes the Hugging Face pipeline with the HerBERT model.
    """
    print(f"--> Loading model: {MODEL_NAME}...")
    print("--> To może chwilę potrwać (model jest pobierany przy pierwszym użyciu)...")
    try:
        # Pipeline automatically handles tokenizer and model loading
        classifier = pipeline(
            "sentiment-analysis",
            model=MODEL_NAME,
            tokenizer=MODEL_NAME
        )
        return classifier
    except Exception as e:
        print(f"Critical Error loading model: {e}")
        print("Tip: Ensure you have internet access to download the model.")
        sys.exit(1)


def analyze_single_text(classifier, text):
    """
    Runs analysis on a single string using HerBERT.
    """
    print(f"\n--- SINGLE TEXT ANALYSIS (HerBERT) ---")
    print(f"Input: \"{text}\"")

    try:
        # Pipeline returns list of dicts: [{'label': 'positive', 'score': 0.99}]
        result = classifier(text)[0]
        label = result['label']
        score = result['score']

        # HerBERT usually uses standard labels, but sometimes they differ slightly.
        # We print them exactly as the model returns them.
        print(f"Sentiment: {label}")
        print(f"Confidence: {score:.4f}")
        print("--------------------------------------\n")
    except Exception as e:
        print(f"Error processing text: {e}")


def process_csv_file(classifier, input_path, output_path, col_name):
    """
    Reads a CSV, analyzes the specified column, and saves the output.
    """
    print(f"--> Reading file: {input_path}")

    if not os.path.exists(input_path):
        print(f"Error: File '{input_path}' not found. Make sure 'opinie-oczywiste.csv' exists.")
        return

    try:
        df = pd.read_csv(input_path)
    except Exception as e:
        print(f"Error reading CSV: {e}")
        return

    if col_name not in df.columns:
        print(f"Error: Column '{col_name}' not found.")
        print(f"Available columns: {list(df.columns)}")
        return

    print(f"--> Analyzing {len(df)} rows with HerBERT. Please wait...")

    results_label = []
    results_score = []

    # Iteration with manual progress indication
    total_rows = len(df)
    for i, text in enumerate(df[col_name]):
        # Handle empty/NaN values
        if pd.isna(text) or str(text).strip() == "":
            results_label.append("n/a")
            results_score.append(0.0)
            continue

        # Truncate text. HerBERT (BERT-based) has a strict 512 token limit.
        # We cut characters to ~512 to be safe, though token count != char count.
        # A rough safe estimate for Polish is ~2000 characters, but 512 chars is super safe.
        clean_text = str(text)[:512]

        try:
            res = classifier(clean_text)[0]
            results_label.append(res['label'])
            results_score.append(res['score'])
        except Exception as e:
            # Sometimes texts are too long even after char truncation due to tokenization
            print(f"\nWarning: Error at row {i}: {e}")
            results_label.append("error")
            results_score.append(0.0)

        # Progress Bar
        if i % 5 == 0 or i == total_rows - 1:
            sys.stdout.write(f"\rProgress: {i+1}/{total_rows}")
            sys.stdout.flush()

    print(f"\n--> Analysis Complete!")

    # Append results
    df['herbert_label'] = results_label
    df['herbert_confidence'] = results_score

    # Save
    try:
        df.to_csv(output_path, index=False)
        print(f"--> Success! Results saved to: {output_path}")
    except Exception as e:
        print(f"Error saving file: {e}")


# ==========================================
# MAIN EXECUTION
# ==========================================
if __name__ == "__main__":
    # 1. Load Model
    herbert_model = load_sentiment_pipeline()

    # 2. Execute based on MODE
    if MODE == 'single':
        analyze_single_text(herbert_model, TEST_TEXT)
    elif MODE == 'file':
        process_csv_file(herbert_model, INPUT_FILE, OUTPUT_FILE, TEXT_COLUMN)
    else:
        print("Invalid MODE selected in configuration.")