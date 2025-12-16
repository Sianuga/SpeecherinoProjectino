"""
Moduł Text-to-Speech (TTS)
Odpowiedzialny za syntezę mowy z tekstu.

Planowane implementacje:
- ElevenLabs
- Google Text-to-Speech
- Lokalne modele (pyttsx3, edge-tts)
"""

from abc import ABC, abstractmethod
from typing import Optional, Callable
from dataclasses import dataclass
from enum import Enum
import tempfile
from pathlib import Path


class VoiceGender(Enum):
    MALE = "male"
    FEMALE = "female"
    NEUTRAL = "neutral"


@dataclass
class VoiceConfig:
    """Konfiguracja głosu"""
    voice_id: str
    name: str = ""
    gender: VoiceGender = VoiceGender.NEUTRAL
    language: str = "pl"
    speed: float = 1.0
    pitch: float = 1.0


@dataclass
class SynthesisResult:
    """Wynik syntezy mowy"""
    audio_path: str
    duration_seconds: float = 0.0
    success: bool = True
    error_message: str = ""


class TTSProvider(ABC):
    """Bazowa klasa dla dostawców TTS"""
    
    @abstractmethod
    def synthesize(self, text: str, voice_config: Optional[VoiceConfig] = None) -> SynthesisResult:
        """
        Syntezuje mowę z tekstu.
        
        Args:
            text: Tekst do syntezy
            voice_config: Opcjonalna konfiguracja głosu
            
        Returns:
            SynthesisResult ze ścieżką do pliku audio
        """
        pass
    
    @abstractmethod
    def get_available_voices(self) -> list[VoiceConfig]:
        """Zwraca listę dostępnych głosów"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdza czy dostawca jest dostępny"""
        pass


class ElevenLabsTTS(TTSProvider):
    """Implementacja TTS używająca ElevenLabs"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.base_url = "https://api.elevenlabs.io/v1"
        self.temp_dir = Path(tempfile.gettempdir()) / "rubber_duck" / "tts"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self, text: str, voice_config: Optional[VoiceConfig] = None) -> SynthesisResult:
        # TODO: Implementacja ElevenLabs API
        raise NotImplementedError("ElevenLabs TTS nie jest jeszcze zaimplementowany")
    
    def get_available_voices(self) -> list[VoiceConfig]:
        # TODO: Pobierz listę głosów z API
        return []
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class GoogleTTS(TTSProvider):
    """Implementacja TTS używająca Google Text-to-Speech"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key
        self.temp_dir = Path(tempfile.gettempdir()) / "rubber_duck" / "tts"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self, text: str, voice_config: Optional[VoiceConfig] = None) -> SynthesisResult:
        # TODO: Implementacja Google TTS API
        raise NotImplementedError("Google TTS nie jest jeszcze zaimplementowany")
    
    def get_available_voices(self) -> list[VoiceConfig]:
        return []
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class LocalTTS(TTSProvider):
    """Implementacja TTS używająca lokalnych silników (pyttsx3, edge-tts)"""
    
    def __init__(self):
        self.engine = None
        self.temp_dir = Path(tempfile.gettempdir()) / "rubber_duck" / "tts"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
    
    def synthesize(self, text: str, voice_config: Optional[VoiceConfig] = None) -> SynthesisResult:
        # TODO: Implementacja pyttsx3 lub edge-tts
        raise NotImplementedError("Local TTS nie jest jeszcze zaimplementowany")
    
    def get_available_voices(self) -> list[VoiceConfig]:
        return []
    
    def is_available(self) -> bool:
        try:
            import pyttsx3
            return True
        except ImportError:
            pass
        
        try:
            import edge_tts
            return True
        except ImportError:
            pass
        
        return False


class TTSManager:
    """
    Manager TTS - zarządza dostawcami i odtwarzaniem audio.
    """
    
    def __init__(self):
        self.providers: dict[str, TTSProvider] = {}
        self.active_provider: Optional[str] = None
        self.is_speaking = False
        self.on_speaking_start: Optional[Callable] = None
        self.on_speaking_end: Optional[Callable] = None
    
    def register_provider(self, name: str, provider: TTSProvider):
        """Rejestruje dostawcę TTS"""
        self.providers[name] = provider
    
    def set_active_provider(self, name: str) -> bool:
        """Ustawia aktywnego dostawcę"""
        if name in self.providers and self.providers[name].is_available():
            self.active_provider = name
            return True
        return False
    
    def speak(self, text: str, voice_config: Optional[VoiceConfig] = None) -> bool:
        """
        Syntezuje i odtwarza tekst jako mowę.
        
        Args:
            text: Tekst do wypowiedzenia
            voice_config: Opcjonalna konfiguracja głosu
            
        Returns:
            True jeśli sukces
        """
        if not self.active_provider:
            for name, provider in self.providers.items():
                if provider.is_available():
                    self.active_provider = name
                    break
        
        if not self.active_provider:
            return False
        
        provider = self.providers.get(self.active_provider)
        if not provider:
            return False
        
        try:
            self.is_speaking = True
            if self.on_speaking_start:
                self.on_speaking_start()
            
            result = provider.synthesize(text, voice_config)
            
            if result.success:
                # TODO: Odtwórz audio
                self._play_audio(result.audio_path)
            
            return result.success
            
        finally:
            self.is_speaking = False
            if self.on_speaking_end:
                self.on_speaking_end()
    
    def _play_audio(self, audio_path: str):
        """Odtwarza plik audio"""
        # TODO: Implementacja odtwarzania audio
        pass
    
    def stop(self):
        """Zatrzymuje odtwarzanie"""
        self.is_speaking = False
    
    def get_available_providers(self) -> list[str]:
        """Zwraca listę dostępnych dostawców"""
        return [name for name, p in self.providers.items() if p.is_available()]
    
    def get_voices(self) -> list[VoiceConfig]:
        """Zwraca dostępne głosy aktywnego dostawcy"""
        if self.active_provider:
            provider = self.providers.get(self.active_provider)
            if provider:
                return provider.get_available_voices()
        return []
