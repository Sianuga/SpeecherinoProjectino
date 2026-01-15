import threading
import wave
import tempfile
from pathlib import Path
from typing import Callable, Optional
from datetime import datetime

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False


class AudioRecorder:
    """
    Klasa odpowiedzialna za nagrywanie audio z mikrofonu.
    Zapisuje nagrania w formacie WAV.
    """

    def __init__(self):
        self.is_recording = False
        self.frames = []
        self.audio = None
        self.stream = None
        self.record_thread = None

        # Parametry nagrywania - optymalne dla STT
        self.sample_rate = 16000  # 16kHz - standard dla STT
        self.channels = 1  # Mono
        self.chunk_size = 1024
        self.format = pyaudio.paInt16 if PYAUDIO_AVAILABLE else None

        # Katalog na nagrania tymczasowe
        self.temp_dir = Path(tempfile.gettempdir()) / "rubber_duck" / "recordings"
        self.temp_dir.mkdir(parents=True, exist_ok=True)

    def start_recording(self, on_error: Optional[Callable[[str], None]] = None) -> bool:
        """
        Rozpoczyna nagrywanie audio.

        Args:
            on_error: Callback wywoływany w przypadku błędu

        Returns:
            True jeśli nagrywanie rozpoczęte pomyślnie
        """
        if not PYAUDIO_AVAILABLE:
            if on_error:
                on_error("PyAudio nie jest zainstalowane")
            return False

        if self.is_recording:
            return False

        try:
            self.audio = pyaudio.PyAudio()

            # Znajdź domyślne urządzenie wejściowe
            default_input = self.audio.get_default_input_device_info()
            print(f"[AudioRecorder] Używam urządzenia: {default_input['name']}")

            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size,
                input_device_index=int(default_input['index'])
            )

            self.is_recording = True
            self.frames = []

            # Uruchom wątek nagrywania
            self.record_thread = threading.Thread(target=self._record_loop)
            self.record_thread.daemon = True
            self.record_thread.start()

            print("[AudioRecorder] Nagrywanie rozpoczęte")
            return True

        except Exception as e:
            error_msg = f"Błąd inicjalizacji nagrywania: {e}"
            print(f"[AudioRecorder] {error_msg}")
            if on_error:
                on_error(error_msg)
            self._cleanup()
            return False

    def _record_loop(self):
        """Pętla nagrywania w osobnym wątku."""
        while self.is_recording:
            try:
                data = self.stream.read(self.chunk_size, exception_on_overflow=False)
                self.frames.append(data)
            except Exception as e:
                print(f"[AudioRecorder] Błąd podczas nagrywania: {e}")
                break

    def stop_recording(self) -> Optional[str]:
        """
        Zatrzymuje nagrywanie i zapisuje plik audio.

        Returns:
            Ścieżka do zapisanego pliku WAV lub None jeśli błąd
        """
        if not self.is_recording:
            return None

        self.is_recording = False

        # Poczekaj na zakończenie wątku nagrywania
        if self.record_thread:
            self.record_thread.join(timeout=1.0)

        audio_path = None

        if self.frames:
            # Generuj unikalną nazwę pliku
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            audio_path = str(self.temp_dir / f"recording_{timestamp}.wav")

            try:
                with wave.open(audio_path, 'wb') as wf:
                    wf.setnchannels(self.channels)
                    wf.setsampwidth(self.audio.get_sample_size(self.format))
                    wf.setframerate(self.sample_rate)
                    wf.writeframes(b''.join(self.frames))

                # Oblicz czas trwania
                duration = len(self.frames) * self.chunk_size / self.sample_rate
                print(f"[AudioRecorder] Nagranie zapisane: {audio_path} ({duration:.1f}s)")

            except Exception as e:
                print(f"[AudioRecorder] Błąd zapisu audio: {e}")
                audio_path = None
        else:
            print("[AudioRecorder] Brak danych audio do zapisania")

        self._cleanup()
        return audio_path

    def _cleanup(self):
        """Zwalnia zasoby audio."""
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None

        if self.audio:
            try:
                self.audio.terminate()
            except Exception:
                pass
            self.audio = None

        self.frames = []

    def is_available(self) -> bool:
        """
        Sprawdza czy nagrywanie audio jest dostępne.
        """
        if not PYAUDIO_AVAILABLE:
            return False

        try:
            audio = pyaudio.PyAudio()
            device_count = audio.get_device_count()

            has_input = False
            for i in range(device_count):
                info = audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    has_input = True
                    break

            audio.terminate()
            return has_input
        except Exception:
            return False

    def cleanup_old_recordings(self, max_age_hours: int = 24):
        """
        Usuwa stare nagrania z katalogu tymczasowego.
        """
        import time

        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        for file_path in self.temp_dir.glob("recording_*.wav"):
            try:
                file_age = current_time - file_path.stat().st_mtime
                if file_age > max_age_seconds:
                    file_path.unlink()
                    print(f"[AudioRecorder] Usunięto stare nagranie: {file_path.name}")
            except Exception:
                pass