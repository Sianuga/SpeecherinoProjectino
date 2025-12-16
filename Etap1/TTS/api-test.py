print(f"📄 Log CSV: {log_path}")
print(f"📁 Wyniki zapisane w folderze: ./Results")
print("\n✅ Wszystkie testy zakończone!")

            ])
                status
                filename,
                round(rtf, 2),
                round(duration, 2),
                speed,
                text[:60] + "...",
                MODEL_NAME,
                datetime.now().isoformat(timespec="seconds"),
            writer.writerow([
            writer = csv.writer(f)
        with open(log_path, "a", newline="", encoding="utf-8") as f:
        # zapis do CSV

            status = f"ERROR: {e}"
            duration = rtf = 0
            print(f"❌ Błąd przy generowaniu: {e}")
        except Exception as e:

            status = "OK ✅"
            print(f" > Processing time: {duration:.2f}s | Real-time factor: {rtf:.2f}")

            rtf = duration / audio_len_s
            audio_len_s = len(wav) / 22050
            # real-time factor (RTF)

            duration = time.time() - start
            sf.write(filename, wav, 22050)
            # zapis ręczny

            )
                speed=speed
                language=LANG,
                speaker_wav=SPEAKER_WAV,
                text=text,
            wav = tts.tts(

            start = time.time()
        try:

        print(f"\n🎙️  Generuję test {idx} — prędkość {speed}...")
        filename = f"Results/test{idx}_speed{speed}_{timestamp}.wav"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    for speed in SPEEDS:
for idx, text in enumerate(TEXTS, start=1):
# === GENEROWANIE AUDIO ===

#     print(f"⚠️  Torch.compile() pominięty: {e}")
# except Exception as e:
#     print("⚙️  Torch.compile() włączony — model zoptymalizowany.")
#     tts.synthesizer.tts_model = torch.compile(tts.synthesizer.tts_model)
# try:

print("> Model załadowany ✅")
tts = TTS(MODEL_NAME)
print(f"\n> Ładuję model {MODEL_NAME}...")
# === ŁADOWANIE MODELU ===

    writer.writerow(["timestamp", "model", "text_snippet", "speed", "duration_s", "rtf", "output_file", "status"])
    writer = csv.writer(f)
with open(log_path, "w", newline="", encoding="utf-8") as f:
# === CSV ===

log_path = os.path.join("Results", "tts_results.csv")
os.makedirs("Results", exist_ok=True)
# === FOLDERY ===

]
    "Pierwszy pociąg PKP odjeżdża o szóstej trzydzieści rano, a drugi o siódmej piętnaście. Na dworcu spotkałem pracownika PKO Banku Polskiego. Powiedział: 'Proszę uważać, dziś może być opóźnienie!'. Na szczęście podróż przebiegła bez problemów."
    "Proszę dodać dziesięć mililitrów H2O i podgrzać roztwór do osiemdziesięciu stopni Celsjusza. Następnie zmieszaj składniki przez około pięć minut. Cały proces opisałem w raporcie dla Sp. z o.o. BioLab. Eksperyment zakończył się pełnym sukcesem.",
    "Spotkanie odbędzie się 12 grudnia 2025 roku o godzinie 14:45. Na sali będzie około trzystu pięćdziesięciu uczestników. To już trzecia edycja tego wydarzenia. W poprzednim roku liczba gości przekroczyła tysiąc osób.",
    "Wczoraj byłem na konferencji AI Future Summit w Warszawie. Prezentację prowadził doktor Smith z firmy OpenAI. Opowiadał o nowych modelach językowych i ich wpływie na edukację. To było naprawdę inspirujące wydarzenie!",
TEXTS = [
# === TEKSTY TESTOWE ===

print(f"🧠 Dostępne rdzenie CPU: {os.cpu_count()}")

os.environ["PYTORCH_JIT"] = "1"
os.environ["COQUI_TTS_PROGRESS_BAR"] = "0"
os.environ["COQUI_TTS_DEBUG"] = "0"
os.environ["COQUI_TTS_LOGGER_LEVEL"] = "ERROR"
os.environ["MKL_NUM_THREADS"] = "5"
os.environ["OMP_NUM_THREADS"] = "5"
torch.set_num_threads(5)
# === OPTYMALIZACJA ŚRODOWISKA ===

SPEEDS = [1.0]
LANG = "pl"
SPEAKER_WAV = r"C:\Users\tomas\Documents\Github\SpeecherinoProjectino\Data\Recordings\Audio_1_1.wav"
MODEL_NAME = "tts_models/multilingual/multi-dataset/xtts_v2"
# === KONFIGURACJA ===

import soundfile as sf
import torch
from TTS.api import TTS
from datetime import datetime
import time
import csv
import os
