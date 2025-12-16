from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QApplication
from typing import Optional
import time

from .config_manager import ConfigManager
from .audio_recorder import AudioRecorder
from .hotkey_manager import HotkeyManager
from .duck_widget import DuckWidget
from .main_window import MainWindow

# Nowe moduły (placeholdery)
from .stt_module import STTManager, WhisperSTT, GoogleSTT
from .tts_module import TTSManager, ElevenLabsTTS, GoogleTTS
from .llm_module import LLMManager, ClaudeLLM, GeminiLLM, ProjectContext
from .sentiment_analyzer import SentimentManager


class ProcessingWorker(QThread):
    """Worker do przetwarzania audio w tle"""
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, audio_path: str, config_manager: ConfigManager,
                 stt_manager: STTManager, llm_manager: LLMManager,
                 sentiment_manager: SentimentManager):
        super().__init__()
        self.audio_path = audio_path
        self.config_manager = config_manager
        self.stt_manager = stt_manager
        self.llm_manager = llm_manager
        self.sentiment_manager = sentiment_manager
    
    def run(self):
        try:
            # TODO: Pełna implementacja pipeline'u
            # 1. STT - transkrypcja audio
            # 2. Analiza sentymentu
            # 3. LLM - generowanie odpowiedzi
            
            # Na razie symulacja
            time.sleep(1)
            
            project = self.config_manager.get_active_project()
            if project:
                response = f"Rozumiem twój problem w projekcie '{project['name']}'. "
                response += "To ciekawe zagadnienie. Czy możesz mi powiedzieć więcej?"
            else:
                response = "Nie masz aktywnego projektu. Dodaj projekt w ustawieniach."
            
            self.finished.emit(response)
            
        except Exception as e:
            self.error.emit(str(e))


class AppController(QObject):
    """Główny kontroler łączący wszystkie komponenty"""
    
    listening_started = pyqtSignal()
    listening_stopped = pyqtSignal()
    response_ready = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        
        # Podstawowe komponenty
        self.config_manager = ConfigManager()
        self.audio_recorder = AudioRecorder()
        self.hotkey_manager = HotkeyManager()
        
        # Nowe moduły AI
        self.stt_manager = STTManager()
        self.tts_manager = TTSManager()
        self.llm_manager = LLMManager()
        self.sentiment_manager = SentimentManager()
        
        # UI
        self.duck_widget: Optional[DuckWidget] = None
        self.main_window: Optional[MainWindow] = None
        self.processing_worker: Optional[ProcessingWorker] = None
        
        self.is_listening = False
        
        # Inicjalizacja modułów AI
        self._setup_ai_modules()
    
    def _setup_ai_modules(self):
        """Konfiguruje moduły AI na podstawie konfiguracji"""
        api_keys = self.config_manager.config.get("api_keys", {})
        
        # STT
        self.stt_manager.register_provider(
            "whisper", 
            WhisperSTT(api_key=api_keys.get("openai", ""))
        )
        self.stt_manager.register_provider(
            "google",
            GoogleSTT(api_key=api_keys.get("google", ""))
        )
        
        # TTS
        self.tts_manager.register_provider(
            "elevenlabs",
            ElevenLabsTTS(api_key=api_keys.get("elevenlabs", ""))
        )
        self.tts_manager.register_provider(
            "google",
            GoogleTTS(api_key=api_keys.get("google", ""))
        )
        
        # LLM
        self.llm_manager.register_provider(
            "claude",
            ClaudeLLM(api_key=api_keys.get("anthropic", ""))
        )
        self.llm_manager.register_provider(
            "gemini",
            GeminiLLM(api_key=api_keys.get("google", ""))
        )
        
        # Ustaw aktywnych dostawców na podstawie konfiguracji
        llm_provider = self.config_manager.config.get("llm_provider", "claude")
        self.llm_manager.set_active_provider(llm_provider)
    
    def initialize(self):
        """Inicjalizuje wszystkie komponenty UI"""
        duck_size = self.config_manager.config.get("duck_size", 120)
        self.duck_widget = DuckWidget(size=duck_size)
        self.duck_widget.clicked.connect(self.toggle_listening)
        
        self.main_window = MainWindow(self.config_manager)
        
        hotkey = self.config_manager.config.get("push_to_talk_key", "ctrl+shift+d")
        self.hotkey_manager.start(
            hotkey,
            on_activate=self._on_hotkey_press,
            on_deactivate=self._on_hotkey_release
        )
        
        self.listening_started.connect(self._on_listening_started)
        self.listening_stopped.connect(self._on_listening_stopped)
        self.response_ready.connect(self._on_response_ready)
        
        # Callbacks dla TTS
        self.tts_manager.on_speaking_start = lambda: self.duck_widget.set_speaking(True)
        self.tts_manager.on_speaking_end = lambda: self.duck_widget.set_idle()
    
    def show(self):
        """Pokazuje komponenty UI"""
        self.duck_widget.show()
        self.main_window.show()
    
    def _on_hotkey_press(self):
        """Wywołane gdy skrót jest wciśnięty"""
        if not self.is_listening:
            self.start_listening()
    
    def _on_hotkey_release(self):
        """Wywołane gdy skrót jest puszczony"""
        if self.is_listening:
            self.stop_listening()
    
    def toggle_listening(self):
        """Przełącza stan nasłuchiwania (dla kliknięcia w kaczkę)"""
        if self.is_listening:
            self.stop_listening()
        else:
            self.start_listening()
    
    def start_listening(self):
        """Rozpoczyna nagrywanie"""
        if self.is_listening:
            return
        
        success = self.audio_recorder.start_recording(
            on_error=lambda e: print(f"Audio error: {e}")
        )
        
        if success:
            self.is_listening = True
            self.listening_started.emit()
        else:
            # Nawet bez audio, pokazujemy że "słuchamy" dla demo
            self.is_listening = True
            self.listening_started.emit()
    
    def stop_listening(self):
        """Zatrzymuje nagrywanie i przetwarza"""
        if not self.is_listening:
            return
        
        self.is_listening = False
        self.listening_stopped.emit()
        
        audio_path = self.audio_recorder.stop_recording()
        
        # Przetwarzanie w tle
        self.processing_worker = ProcessingWorker(
            audio_path, 
            self.config_manager,
            self.stt_manager,
            self.llm_manager,
            self.sentiment_manager
        )
        self.processing_worker.finished.connect(self._on_processing_finished)
        self.processing_worker.error.connect(self._on_processing_error)
        self.processing_worker.start()
    
    def _on_listening_started(self):
        """Aktualizuje UI gdy zaczyna nasłuchiwać"""
        if self.duck_widget:
            self.duck_widget.set_listening(True)
    
    def _on_listening_stopped(self):
        """Aktualizuje UI gdy kończy nasłuchiwać"""
        if self.duck_widget:
            self.duck_widget.set_speaking(True)
    
    def _on_processing_finished(self, response: str):
        """Obsługuje odpowiedź z przetwarzania"""
        self.response_ready.emit(response)
        
        # TTS - odtworzenie odpowiedzi głosem (jeśli włączone)
        if self.config_manager.config.get("tts_enabled", True):
            # TODO: self.tts_manager.speak(response)
            pass
        
        # Po "wypowiedzeniu" wracamy do idle
        if self.duck_widget:
            QThread.msleep(2000)
            self.duck_widget.set_idle()
    
    def _on_processing_error(self, error: str):
        """Obsługuje błąd przetwarzania"""
        print(f"Processing error: {error}")
        if self.duck_widget:
            self.duck_widget.set_idle()
    
    def _on_response_ready(self, response: str):
        """Obsługuje gotową odpowiedź"""
        print(f"Duck says: {response}")
    
    def cleanup(self):
        """Sprzątanie przed zamknięciem"""
        self.hotkey_manager.stop()
        if self.audio_recorder.is_recording:
            self.audio_recorder.stop_recording()
