"""
Moduł Speech-to-Text (STT)
Transkrypcja mowy na tekst za pomocą ElevenLabs Python SDK.
"""

import os
from typing import Optional
from dataclasses import dataclass, field
from pathlib import Path

from elevenlabs.client import ElevenLabs


@dataclass
class TranscriptionResult:
    """Wynik transkrypcji"""
    text: str
    language: str = "pl"
    confidence: float = 0.0
    duration_seconds: float = 0.0
    words: list = field(default_factory=list)
    success: bool = True
    error_message: str = ""


class ElevenLabsSTT:
    """
    Implementacja STT używająca ElevenLabs Python SDK.

    Dokumentacja: https://elevenlabs.io/docs/developers/guides/cookbooks/speech-to-text/quickstart
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicjalizuje klienta ElevenLabs STT.

        Args:
            api_key: Klucz API ElevenLabs
        """
        self.api_key = api_key or os.getenv("ELEVENLABS_API_KEY", "")
        self.client = None

        if self.is_available():
            self.client = ElevenLabs(api_key=self.api_key)

    def transcribe(self, audio_path: str) -> TranscriptionResult:
        """
        Transkrybuje plik audio używając ElevenLabs SDK.

        Args:
            audio_path: Ścieżka do pliku audio (WAV)

        Returns:
            TranscriptionResult z transkrypcją
        """
        if not self.is_available():
            return TranscriptionResult(
                text="",
                success=False,
                error_message="Brak klucza API ElevenLabs"
            )

        # Sprawdź czy plik istnieje
        path = Path(audio_path)
        if not path.exists():
            return TranscriptionResult(
                text="",
                success=False,
                error_message=f"Plik audio nie istnieje: {audio_path}"
            )

        try:
            print(f"[STT] Wysyłam do ElevenLabs: {audio_path}")

            # Otwórz plik i wyślij do API
            with open(audio_path, "rb") as audio_file:
                result = self.client.speech_to_text.convert(
                    file=audio_file,
                    model_id="scribe_v1",
                    language_code="pl",
                    tag_audio_events=False,
                    diarize=False
                )

            # Wyciągnij tekst z odpowiedzi
            text = result.text if hasattr(result, 'text') else str(result)
            language = result.language_code if hasattr(result, 'language_code') else "pl"
            confidence = result.language_probability if hasattr(result, 'language_probability') else 0.0
            words = result.words if hasattr(result, 'words') else []

            # Oblicz czas trwania
            duration = 0.0
            if words:
                last_word = words[-1]
                duration = last_word.end if hasattr(last_word, 'end') else 0.0

            print(f"[STT] Transkrypcja: {text}")

            return TranscriptionResult(
                text=text,
                language=language,
                confidence=confidence,
                duration_seconds=duration,
                words=words,
                success=True
            )

        except Exception as e:
            error_msg = f"Błąd ElevenLabs STT: {str(e)}"
            print(f"[STT] {error_msg}")

            return TranscriptionResult(
                text="",
                success=False,
                error_message=error_msg
            )

    def is_available(self) -> bool:
        """Sprawdza czy API key jest ustawiony"""
        return bool(self.api_key and len(self.api_key) > 10)