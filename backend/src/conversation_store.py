"""
Moduł przechowywania konwersacji.
Zarządza nagraniami, transkrypcjami i historią rozmów z podziałem na projekty i sesje.
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass, field, asdict
from enum import Enum


class MessageRole(Enum):
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Pojedyncza wiadomość w konwersacji"""
    role: MessageRole
    content: str
    timestamp: str = ""
    audio_path: Optional[str] = None
    sentiment: Optional[str] = None
    sentiment_confidence: Optional[float] = None

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> dict:
        return {
            "role": self.role.value,
            "content": self.content,
            "timestamp": self.timestamp,
            "audio_path": self.audio_path,
            "sentiment": self.sentiment,
            "sentiment_confidence": self.sentiment_confidence
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Message":
        return cls(
            role=MessageRole(data["role"]),
            content=data["content"],
            timestamp=data.get("timestamp", ""),
            audio_path=data.get("audio_path"),
            sentiment=data.get("sentiment"),
            sentiment_confidence=data.get("sentiment_confidence")
        )


@dataclass
class Session:
    """Sesja użytkowania aplikacji"""
    session_id: str
    project_name: str
    started_at: str
    messages: List[Message] = field(default_factory=list)
    ended_at: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "project_name": self.project_name,
            "started_at": self.started_at,
            "ended_at": self.ended_at,
            "messages": [m.to_dict() for m in self.messages]
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Session":
        return cls(
            session_id=data["session_id"],
            project_name=data["project_name"],
            started_at=data["started_at"],
            ended_at=data.get("ended_at"),
            messages=[Message.from_dict(m) for m in data.get("messages", [])]
        )


class ConversationStore:
    """
    Przechowuje i zarządza historią konwersacji.

    Struktura katalogów:
    ~/.rubber_duck/
        conversations/
            {project_name}/
                sessions/
                    {session_id}.json
                audio/
                    {timestamp}.wav
    """

    def __init__(self, base_dir: Optional[Path] = None):
        self.base_dir = base_dir or Path.home() / ".rubber_duck" / "conversations"
        self.base_dir.mkdir(parents=True, exist_ok=True)

        self.current_session: Optional[Session] = None
        self.current_project: Optional[str] = None

    def _get_project_dir(self, project_name: str) -> Path:
        """Zwraca katalog projektu"""
        # Sanitize nazwy projektu
        safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in project_name)
        return self.base_dir / safe_name

    def _get_sessions_dir(self, project_name: str) -> Path:
        """Zwraca katalog sesji projektu"""
        path = self._get_project_dir(project_name) / "sessions"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _get_audio_dir(self, project_name: str) -> Path:
        """Zwraca katalog audio projektu"""
        path = self._get_project_dir(project_name) / "audio"
        path.mkdir(parents=True, exist_ok=True)
        return path

    def start_session(self, project_name: str) -> Session:
        """
        Rozpoczyna nową sesję dla projektu.

        Args:
            project_name: Nazwa projektu

        Returns:
            Nowa sesja
        """
        # Zakończ poprzednią sesję jeśli istnieje
        if self.current_session:
            self.end_session()

        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")

        self.current_session = Session(
            session_id=session_id,
            project_name=project_name,
            started_at=datetime.now().isoformat()
        )
        self.current_project = project_name

        print(f"[Store] Rozpoczęto sesję {session_id} dla projektu '{project_name}'")

        return self.current_session

    def end_session(self):
        """Kończy bieżącą sesję i zapisuje ją"""
        if not self.current_session:
            return

        self.current_session.ended_at = datetime.now().isoformat()
        self._save_session(self.current_session)

        print(f"[Store] Zakończono sesję {self.current_session.session_id}")

        self.current_session = None

    def _save_session(self, session: Session):
        """Zapisuje sesję do pliku JSON"""
        sessions_dir = self._get_sessions_dir(session.project_name)
        file_path = sessions_dir / f"{session.session_id}.json"

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(session.to_dict(), f, ensure_ascii=False, indent=2)

        print(f"[Store] Zapisano sesję: {file_path}")

    def add_user_message(
            self,
            content: str,
            audio_path: Optional[str] = None,
            sentiment: Optional[str] = None,
            sentiment_confidence: Optional[float] = None
    ) -> Message:
        """
        Dodaje wiadomość użytkownika do bieżącej sesji.

        Args:
            content: Transkrypcja tekstu
            audio_path: Ścieżka do pliku audio (opcjonalne)
            sentiment: Wykryty sentyment
            sentiment_confidence: Pewność sentymentu

        Returns:
            Utworzona wiadomość
        """
        if not self.current_session:
            raise RuntimeError("Brak aktywnej sesji. Wywołaj start_session() najpierw.")

        # Skopiuj audio do katalogu projektu jeśli podano
        stored_audio_path = None
        if audio_path and Path(audio_path).exists():
            stored_audio_path = self._store_audio(audio_path)

        message = Message(
            role=MessageRole.USER,
            content=content,
            audio_path=stored_audio_path,
            sentiment=sentiment,
            sentiment_confidence=sentiment_confidence
        )

        self.current_session.messages.append(message)

        # Auto-save po każdej wiadomości
        self._save_session(self.current_session)

        return message

    def add_assistant_message(self, content: str) -> Message:
        """
        Dodaje odpowiedź asystenta do bieżącej sesji.

        Args:
            content: Treść odpowiedzi

        Returns:
            Utworzona wiadomość
        """
        if not self.current_session:
            raise RuntimeError("Brak aktywnej sesji. Wywołaj start_session() najpierw.")

        message = Message(
            role=MessageRole.ASSISTANT,
            content=content
        )

        self.current_session.messages.append(message)
        self._save_session(self.current_session)

        return message

    def _store_audio(self, source_path: str) -> str:
        """
        Kopiuje plik audio do katalogu projektu.

        Args:
            source_path: Ścieżka źródłowa

        Returns:
            Nowa ścieżka w katalogu projektu
        """
        if not self.current_project:
            return source_path

        audio_dir = self._get_audio_dir(self.current_project)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        dest_path = audio_dir / f"{timestamp}.wav"

        shutil.copy2(source_path, dest_path)

        return str(dest_path)

    def get_session_history(self, max_messages: int = 20) -> List[Message]:
        """
        Zwraca historię wiadomości z bieżącej sesji.

        Args:
            max_messages: Maksymalna liczba wiadomości

        Returns:
            Lista wiadomości (najnowsze na końcu)
        """
        if not self.current_session:
            return []

        return self.current_session.messages[-max_messages:]

    def get_history_for_prompt(self, max_messages: int = 10) -> List[dict]:
        """
        Zwraca historię w formacie do promptu LLM.

        Args:
            max_messages: Maksymalna liczba wiadomości

        Returns:
            Lista słowników z role i content
        """
        messages = self.get_session_history(max_messages)
        return [
            {"role": m.role.value, "content": m.content}
            for m in messages
        ]

    def load_session(self, project_name: str, session_id: str) -> Optional[Session]:
        """Ładuje zapisaną sesję"""
        sessions_dir = self._get_sessions_dir(project_name)
        file_path = sessions_dir / f"{session_id}.json"

        if not file_path.exists():
            return None

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        return Session.from_dict(data)

    def list_sessions(self, project_name: str) -> List[str]:
        """Zwraca listę ID sesji dla projektu"""
        sessions_dir = self._get_sessions_dir(project_name)

        sessions = []
        for file_path in sessions_dir.glob("*.json"):
            sessions.append(file_path.stem)

        return sorted(sessions, reverse=True)

    def get_project_stats(self, project_name: str) -> dict:
        """Zwraca statystyki projektu"""
        sessions = self.list_sessions(project_name)

        total_messages = 0
        total_audio_files = 0

        for session_id in sessions:
            session = self.load_session(project_name, session_id)
            if session:
                total_messages += len(session.messages)

        audio_dir = self._get_audio_dir(project_name)
        total_audio_files = len(list(audio_dir.glob("*.wav")))

        return {
            "project_name": project_name,
            "total_sessions": len(sessions),
            "total_messages": total_messages,
            "total_audio_files": total_audio_files
        }