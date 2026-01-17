"""
Moduł Text-to-Speech (TTS)
Synteza mowy z tekstu za pomocą ElevenLabs Python SDK.
"""

import os
import threading
from typing import Optional, Callable
from dataclasses import dataclass

from elevenlabs.client import ElevenLabs
from elevenlabs import stream as elevenlabs_stream
from elevenlabs.play import play as elevenlabs_play


@dataclass
class TTSResult:
    """Wynik syntezy mowy"""
    success: bool = True
    error_message: str = ""
    duration_seconds: float = 0.0


class ElevenLabsTTS:
    """
    Implementacja TTS używająca ElevenLabs Python SDK.

    Dokumentacja: https://github.com/elevenlabs/elevenlabs-python
    """

    # Domyślny głos - George (męski, spokojny)
    # Inne opcje: JBFqnCBsd6RMkjVDRZzb (George), 21m00Tcm4TlvDq8ikWAM (Rachel)
    DEFAULT_VOICE_ID = "JBFqnCBsd6RMkjVDRZzb"

    # Model wspierający wiele języków w tym polski
    MODEL_ID = "eleven_multilingual_v2"

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicjalizuje klienta ElevenLabs TTS.

        Args:
            api_key: Klucz API ElevenLabs
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.client = None
        self.voice_id = self.DEFAULT_VOICE_ID
        self.is_speaking = False

        # Callbacki
        self.on_speaking_start: Optional[Callable] = None
        self.on_speaking_end: Optional[Callable] = None

        if self.is_available():
            self.client = ElevenLabs(api_key=self.api_key)
            print(f"[TTS] ElevenLabs client zainicjalizowany")

    def speak(self, text: str, use_streaming: bool = True) -> TTSResult:
        """
        Syntezuje i odtwarza tekst jako mowę.

        Args:
            text: Tekst do wypowiedzenia (po polsku)
            use_streaming: Czy używać streamingu (niższa latencja)

        Returns:
            TTSResult z informacją o powodzeniu
        """
        if not self.is_available():
            return TTSResult(
                success=False,
                error_message="Brak klucza API ElevenLabs"
            )

        if not self.client:
            return TTSResult(
                success=False,
                error_message="Klient ElevenLabs nie zainicjalizowany"
            )

        if not text or not text.strip():
            return TTSResult(
                success=False,
                error_message="Pusty tekst do syntezy"
            )

        try:
            self.is_speaking = True
            if self.on_speaking_start:
                self.on_speaking_start()

            print(f"[TTS] Syntezuję: {text[:50]}...")

            if use_streaming:
                # Streaming - niższa latencja
                audio_stream = self.client.text_to_speech.stream(
                    text=text,
                    voice_id=self.voice_id,
                    model_id=self.MODEL_ID
                )
                # Odtwórz stream
                elevenlabs_stream(audio_stream)
            else:
                # Standardowa konwersja - cały plik na raz
                audio = self.client.text_to_speech.convert(
                    text=text,
                    voice_id=self.voice_id,
                    model_id=self.MODEL_ID,
                    output_format="mp3_44100_128"
                )
                # Odtwórz audio
                elevenlabs_play(audio)

            print(f"[TTS] Odtwarzanie zakończone")

            return TTSResult(success=True)

        except Exception as e:
            error_msg = f"Błąd ElevenLabs TTS: {str(e)}"
            print(f"[TTS] {error_msg}")

            return TTSResult(
                success=False,
                error_message=error_msg
            )

        finally:
            self.is_speaking = False
            if self.on_speaking_end:
                self.on_speaking_end()

    def speak_async(self, text: str, use_streaming: bool = True) -> None:
        """
        Syntezuje i odtwarza tekst w osobnym wątku (nie blokuje).

        Args:
            text: Tekst do wypowiedzenia
            use_streaming: Czy używać streamingu
        """
        thread = threading.Thread(
            target=self.speak,
            args=(text, use_streaming),
            daemon=True
        )
        thread.start()

    def set_voice(self, voice_id: str):
        """
        Ustawia głos do syntezy.

        Args:
            voice_id: ID głosu z ElevenLabs
        """
        self.voice_id = voice_id
        print(f"[TTS] Ustawiono głos: {voice_id}")

    def list_voices(self) -> list:
        """
        Zwraca listę dostępnych głosów.

        Returns:
            Lista głosów
        """
        if not self.client:
            return []

        try:
            response = self.client.voices.search()
            voices = []
            for voice in response.voices:
                voices.append({
                    "voice_id": voice.voice_id,
                    "name": voice.name,
                    "category": getattr(voice, 'category', 'unknown')
                })
            return voices
        except Exception as e:
            print(f"[TTS] Błąd pobierania głosów: {e}")
            return []

    def stop(self):
        """Zatrzymuje odtwarzanie (jeśli możliwe)"""
        self.is_speaking = False

    def is_available(self) -> bool:
        """Sprawdza czy API key jest ustawiony"""
        return bool(self.api_key and len(self.api_key) > 10)