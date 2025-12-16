"""
Moduł Speech-to-Text (STT)
Odpowiedzialny za transkrypcję mowy na tekst.

Planowane implementacje:
- Whisper (OpenAI)
- Google Speech-to-Text
- Lokalne modele (faster-whisper)
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass


@dataclass
class TranscriptionResult:
    """Wynik transkrypcji"""
    text: str
    language: str = "pl"
    confidence: float = 0.0
    duration_seconds: float = 0.0


class STTProvider(ABC):
    """Bazowa klasa dla dostawców STT"""
    
    @abstractmethod
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """
        Transkrybuje plik audio na tekst.
        
        Args:
            audio_path: Ścieżka do pliku audio (WAV)
            
        Returns:
            TranscriptionResult z transkrypcją
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdza czy dostawca jest dostępny"""
        pass


class WhisperSTT(STTProvider):
    """Implementacja STT używająca Whisper (OpenAI)"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "whisper-1"):
        self.api_key = api_key
        self.model = model
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        # TODO: Implementacja API OpenAI Whisper
        raise NotImplementedError("Whisper STT nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class GoogleSTT(STTProvider):
    """Implementacja STT używająca Google Speech-to-Text"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        # TODO: Implementacja Google Speech-to-Text API
        raise NotImplementedError("Google STT nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class LocalWhisperSTT(STTProvider):
    """Implementacja STT używająca lokalnego modelu Whisper (faster-whisper)"""
    
    def __init__(self, model_size: str = "base"):
        self.model_size = model_size
        self.model = None
    
    def transcribe(self, audio_path: str) -> TranscriptionResult:
        # TODO: Implementacja faster-whisper
        raise NotImplementedError("Local Whisper STT nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        try:
            import faster_whisper
            return True
        except ImportError:
            return False


class STTManager:
    """
    Manager STT - zarządza dostawcami i wybiera najlepszego.
    """
    
    def __init__(self):
        self.providers: dict[str, STTProvider] = {}
        self.active_provider: Optional[str] = None
    
    def register_provider(self, name: str, provider: STTProvider):
        """Rejestruje dostawcę STT"""
        self.providers[name] = provider
    
    def set_active_provider(self, name: str) -> bool:
        """Ustawia aktywnego dostawcę"""
        if name in self.providers and self.providers[name].is_available():
            self.active_provider = name
            return True
        return False
    
    def transcribe(self, audio_path: str) -> Optional[TranscriptionResult]:
        """
        Transkrybuje audio używając aktywnego dostawcy.
        
        Args:
            audio_path: Ścieżka do pliku audio
            
        Returns:
            TranscriptionResult lub None jeśli błąd
        """
        if not self.active_provider:
            # Próbuj znaleźć dostępnego dostawcę
            for name, provider in self.providers.items():
                if provider.is_available():
                    self.active_provider = name
                    break
        
        if not self.active_provider:
            return None
        
        provider = self.providers.get(self.active_provider)
        if provider:
            return provider.transcribe(audio_path)
        return None
    
    def get_available_providers(self) -> list[str]:
        """Zwraca listę dostępnych dostawców"""
        return [name for name, p in self.providers.items() if p.is_available()]
