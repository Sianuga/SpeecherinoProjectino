"""
Główny kontroler aplikacji.
Integruje: nagrywanie -> STT -> sentyment -> LLM -> TTS -> zapis
"""

from PyQt6.QtCore import QObject, pyqtSignal, QThread
from typing import Optional

from .config_manager import ConfigManager
from .audio_recorder import AudioRecorder
from .hotkey_manager import HotkeyManager
from .duck_widget import DuckWidget
from .main_window import MainWindow
from .stt_module import ElevenLabsSTT
from .sentiment_analyzer import HerBERTSentimentAnalyzer
from .conversation_store import ConversationStore
from .llm_module import GeminiLLM
from .tts_module import ElevenLabsTTS


class ProcessingWorker(QThread):
    """Worker do przetwarzania audio w tle"""

    transcription_ready = pyqtSignal(str)
    sentiment_ready = pyqtSignal(str, float)
    response_ready = pyqtSignal(str)
    speaking_started = pyqtSignal()
    speaking_finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(
        self,
        audio_path: str,
        stt: ElevenLabsSTT,
        sentiment_analyzer: HerBERTSentimentAnalyzer,
        llm: GeminiLLM,
        tts: ElevenLabsTTS,
        conversation_store: ConversationStore,
        config_manager: ConfigManager
    ):
        super().__init__()
        self.audio_path = audio_path
        self.stt = stt
        self.sentiment_analyzer = sentiment_analyzer
        self.llm = llm
        self.tts = tts
        self.conversation_store = conversation_store
        self.config_manager = config_manager

    def run(self):
        try:
            # === ETAP 1: Transkrypcja STT (ElevenLabs) ===
            if not self.audio_path:
                self.error.emit("Brak nagrania audio")
                return

            stt_result = self.stt.transcribe(self.audio_path)

            if not stt_result.success:
                self.error.emit(f"STT: {stt_result.error_message}")
                return

            user_text = stt_result.text
            self.transcription_ready.emit(user_text)
            print(f"[Worker] Transkrypcja: {user_text}")

            # === ETAP 2: Analiza sentymentu (HerBERT) ===
            sentiment_result = self.sentiment_analyzer.analyze(user_text)
            sentiment = sentiment_result.sentiment.value
            confidence = sentiment_result.confidence

            self.sentiment_ready.emit(sentiment, confidence)
            print(f"[Worker] Sentyment: {sentiment} ({confidence:.2f})")

            # === ETAP 3: Zapisz wiadomość użytkownika ===
            self.conversation_store.add_user_message(
                content=user_text,
                audio_path=self.audio_path,
                sentiment=sentiment,
                sentiment_confidence=confidence
            )

            # === ETAP 4: Przygotuj kontekst dla LLM ===
            project = self.config_manager.get_active_project()
            if project:
                self.llm.set_project(project)

            # Historia (bez bieżącej wiadomości)
            history = self.conversation_store.get_history_for_prompt(max_messages=10)
            if history:
                history = history[:-1]  # Usuń ostatnią (właśnie dodaną)
            self.llm.set_history(history)

            # Sentyment
            self.llm.set_sentiment(sentiment, confidence)

            # === ETAP 5: Generuj odpowiedź (Gemini) ===
            llm_response = self.llm.generate_response(user_text)

            if not llm_response.success:
                self.error.emit(f"LLM: {llm_response.error_message}")
                return

            response_text = llm_response.content

            # === ETAP 6: Zapisz odpowiedź asystenta ===
            self.conversation_store.add_assistant_message(response_text)

            self.response_ready.emit(response_text)
            print(f"[Worker] Odpowiedź zapisana")

            # === ETAP 7: Text-to-Speech (ElevenLabs) ===
            if self.tts.is_available() and self.config_manager.config.get("tts_enabled", True):
                self.speaking_started.emit()
                print(f"[Worker] Rozpoczynam TTS...")

                tts_result = self.tts.speak(response_text, use_streaming=True)

                if not tts_result.success:
                    print(f"[Worker] TTS błąd: {tts_result.error_message}")

                self.speaking_finished.emit()
                print(f"[Worker] TTS zakończony")
            else:
                print(f"[Worker] TTS wyłączony lub niedostępny")
                self.speaking_finished.emit()

        except Exception as e:
            import traceback
            traceback.print_exc()
            self.error.emit(f"Błąd: {str(e)}")


class AppController(QObject):
    """Główny kontroler aplikacji"""

    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    transcription_ready = pyqtSignal(str)
    sentiment_ready = pyqtSignal(str, float)
    response_ready = pyqtSignal(str)
    speaking_started = pyqtSignal()
    speaking_finished = pyqtSignal()
    error_occurred = pyqtSignal(str)

    def __init__(self):
        super().__init__()

        # Konfiguracja
        self.config_manager = ConfigManager()

        # Audio
        self.audio_recorder = AudioRecorder()
        self.hotkey_manager = HotkeyManager()

        # AI Modules
        api_keys = self.config_manager.config.get("api_keys", {})

        # STT - ElevenLabs
        self.stt = ElevenLabsSTT(api_key=api_keys.get("elevenlabs", ""))

        # Sentiment - HerBERT
        self.sentiment_analyzer = HerBERTSentimentAnalyzer()

        # LLM - Gemini
        self.llm = GeminiLLM(api_key=api_keys.get("google", ""))

        # TTS - ElevenLabs
        self.tts = ElevenLabsTTS(api_key=api_keys.get("elevenlabs", ""))

        # Przechowywanie konwersacji
        self.conversation_store = ConversationStore()

        # UI
        self.duck_widget: Optional[DuckWidget] = None
        self.main_window: Optional[MainWindow] = None
        self.processing_worker: Optional[ProcessingWorker] = None
        self.is_listening = False

        self._print_status()

    def _print_status(self):
        """Wyświetla status modułów"""
        print("\n=== Status modułów ===")
        print(f"STT (ElevenLabs): {'✓' if self.stt.is_available() else '✗'}")
        print(f"Sentiment (HerBERT): {'✓' if self.sentiment_analyzer.is_available() else '✗'}")
        print(f"LLM (Gemini): {'✓' if self.llm.is_available() else '✗'}")
        print(f"TTS (ElevenLabs): {'✓' if self.tts.is_available() else '✗'}")
        print(f"Audio: {'✓' if self.audio_recorder.is_available() else '✗'}")
        print("======================\n")

    def initialize(self):
        """Inicjalizuje komponenty UI"""
        duck_size = self.config_manager.config.get("duck_size", 120)
        self.duck_widget = DuckWidget(size=duck_size)
        self.duck_widget.clicked.connect(self.toggle_listening)
        self.duck_widget.double_clicked.connect(self._show_main_window)

        self.main_window = MainWindow(self.config_manager)

        hotkey = self.config_manager.config.get("push_to_talk_key", "ctrl+shift+d")
        self.hotkey_manager.start(
            hotkey,
            on_activate=self._on_hotkey_press,
            on_deactivate=self._on_hotkey_release
        )

        self.listening_started.connect(self._on_listening_started)
        self.listening_stopped.connect(self._on_listening_stopped)

        # Rozpocznij sesję dla aktywnego projektu
        self._start_session_for_active_project()

    def _start_session_for_active_project(self):
        """Rozpoczyna sesję konwersacji"""
        project = self.config_manager.get_active_project()
        project_name = project["name"] if project else "default"
        self.conversation_store.start_session(project_name)

    def show(self):
        """Pokazuje UI"""
        self.duck_widget.show()
        self.main_window.show()

    def _show_main_window(self):
        if self.main_window:
            self.main_window.show_window()

    def _on_hotkey_press(self):
        if not self.is_listening:
            self.start_listening()

    def _on_hotkey_release(self):
        if self.is_listening:
            self.stop_listening()

    def toggle_listening(self):
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()

    def start_listening(self):
        """Rozpoczyna nagrywanie"""
        if self.is_listening:
            return

        print("\n[App] Rozpoczynam nagrywanie...")

        self.audio_recorder.start_recording(
            on_error=lambda e: print(f"[Audio] Błąd: {e}")
        )

        self.is_listening = True
        self.listening_started.emit()

    def stop_listening(self):
        """Zatrzymuje nagrywanie i uruchamia przetwarzanie"""
        if not self.is_listening:
            return

        print("[App] Zatrzymuję nagrywanie...")

        self.is_listening = False
        self.listening_stopped.emit()

        audio_path = self.audio_recorder.stop_recording()

        if audio_path:
            print(f"[App] Przetwarzam: {audio_path}")

            self.processing_worker = ProcessingWorker(
                audio_path=audio_path,
                stt=self.stt,
                sentiment_analyzer=self.sentiment_analyzer,
                llm=self.llm,
                tts=self.tts,
                conversation_store=self.conversation_store,
                config_manager=self.config_manager
            )
            self.processing_worker.transcription_ready.connect(self._on_transcription_ready)
            self.processing_worker.sentiment_ready.connect(self._on_sentiment_ready)
            self.processing_worker.response_ready.connect(self._on_response_ready)
            self.processing_worker.speaking_started.connect(self._on_speaking_started)
            self.processing_worker.speaking_finished.connect(self._on_speaking_finished)
            self.processing_worker.error.connect(self._on_error)
            self.processing_worker.start()
        else:
            print("[App] Brak nagrania")
            if self.duck_widget:
                self.duck_widget.set_idle()

    def _on_listening_started(self):
        if self.duck_widget:
            self.duck_widget.set_listening(True)

    def _on_listening_stopped(self):
        if self.duck_widget:
            # Ustawiamy "thinking" - przetwarzanie
            self.duck_widget.set_speaking(True)

    def _on_transcription_ready(self, text: str):
        print(f"[App] Transkrypcja gotowa")
        self.transcription_ready.emit(text)

    def _on_sentiment_ready(self, sentiment: str, confidence: float):
        print(f"[App] Sentyment: {sentiment}")
        self.sentiment_ready.emit(sentiment, confidence)

    def _on_response_ready(self, response: str):
        print(f"[App] Odpowiedź LLM gotowa")
        self.response_ready.emit(response)

    def _on_speaking_started(self):
        print(f"[App] TTS rozpoczęty")
        self.speaking_started.emit()
        if self.duck_widget:
            self.duck_widget.set_speaking(True)

    def _on_speaking_finished(self):
        print(f"[App] TTS zakończony")
        self.speaking_finished.emit()
        if self.duck_widget:
            self.duck_widget.set_idle()

    def _on_error(self, error: str):
        print(f"[App] BŁĄD: {error}")
        self.error_occurred.emit(error)

        if self.duck_widget:
            self.duck_widget.set_idle()

    def on_project_changed(self, project_name: str):
        """Wywoływane gdy użytkownik zmienia projekt"""
        self.conversation_store.end_session()
        self.conversation_store.start_session(project_name)
        print(f"[App] Zmieniono projekt: {project_name}")

    def cleanup(self):
        """Sprzątanie przed zamknięciem"""
        print("[App] Zamykanie...")
        self.conversation_store.end_session()
        self.hotkey_manager.stop()

        if self.audio_recorder.is_recording:
            self.audio_recorder.stop_recording()

        self.audio_recorder.cleanup_old_recordings(max_age_hours=1)

    def reload_api_keys(self):
        """Przeładowuje klucze API"""
        api_keys = self.config_manager.config.get("api_keys", {})
        self.stt = ElevenLabsSTT(api_key=api_keys.get("elevenlabs", ""))
        self.llm = GeminiLLM(api_key=api_keys.get("google", ""))
        self.tts = ElevenLabsTTS(api_key=api_keys.get("elevenlabs", ""))
        self._print_status()