from .config_manager import ConfigManager
from .duck_widget import DuckWidget
from .main_window import MainWindow
from .audio_recorder import AudioRecorder
from .hotkey_manager import HotkeyManager
from .app_controller import AppController
from .dialogs import ProjectDialog, SettingsDialog

# Nowe moduły AI
from .stt_module import (
    STTManager, 
    STTProvider, 
    WhisperSTT, 
    GoogleSTT, 
    LocalWhisperSTT,
    TranscriptionResult
)
from .tts_module import (
    TTSManager, 
    TTSProvider, 
    ElevenLabsTTS, 
    GoogleTTS, 
    LocalTTS,
    VoiceConfig,
    SynthesisResult
)
from .llm_module import (
    LLMManager, 
    LLMProvider, 
    ClaudeLLM, 
    GeminiLLM,
    Message,
    MessageRole,
    ProjectContext,
    LLMResponse
)
from .sentiment_analyzer import (
    SentimentManager,
    SentimentAnalyzer,
    KeywordSentimentAnalyzer,
    HerBERTSentimentAnalyzer,
    Sentiment,
    SentimentResult
)

__all__ = [
    # Core
    'ConfigManager',
    'DuckWidget', 
    'MainWindow',
    'AudioRecorder',
    'HotkeyManager',
    'AppController',
    'ProjectDialog',
    'SettingsDialog',
    
    # STT
    'STTManager',
    'STTProvider',
    'WhisperSTT',
    'GoogleSTT',
    'LocalWhisperSTT',
    'TranscriptionResult',
    
    # TTS
    'TTSManager',
    'TTSProvider',
    'ElevenLabsTTS',
    'GoogleTTS',
    'LocalTTS',
    'VoiceConfig',
    'SynthesisResult',
    
    # LLM
    'LLMManager',
    'LLMProvider',
    'ClaudeLLM',
    'GeminiLLM',
    'Message',
    'MessageRole',
    'ProjectContext',
    'LLMResponse',
    
    # Sentiment
    'SentimentManager',
    'SentimentAnalyzer',
    'KeywordSentimentAnalyzer',
    'HerBERTSentimentAnalyzer',
    'Sentiment',
    'SentimentResult',
]
