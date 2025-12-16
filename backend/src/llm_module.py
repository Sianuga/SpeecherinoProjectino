"""
Moduł LLM (Large Language Model)
Odpowiedzialny za interakcję z modelami językowymi.

Planowane implementacje:
- Claude (Anthropic)
- Gemini (Google)
"""

from abc import ABC, abstractmethod
from typing import Optional, Generator
from dataclasses import dataclass, field
from enum import Enum


class MessageRole(Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass
class Message:
    """Pojedyncza wiadomość w konwersacji"""
    role: MessageRole
    content: str


@dataclass
class ProjectContext:
    """Kontekst projektu dla LLM"""
    name: str
    description: str = ""
    tech_stack: list[str] = field(default_factory=list)
    business_assumptions: str = ""
    additional_context: str = ""
    
    def to_prompt(self) -> str:
        """Konwertuje kontekst na tekst promptu"""
        parts = [f"Projekt: {self.name}"]
        
        if self.description:
            parts.append(f"Opis: {self.description}")
        
        if self.tech_stack:
            parts.append(f"Stack technologiczny: {', '.join(self.tech_stack)}")
        
        if self.business_assumptions:
            parts.append(f"Założenia biznesowe: {self.business_assumptions}")
        
        if self.additional_context:
            parts.append(f"Dodatkowy kontekst: {self.additional_context}")
        
        return "\n".join(parts)


@dataclass
class LLMResponse:
    """Odpowiedź z modelu LLM"""
    content: str
    model: str = ""
    tokens_used: int = 0
    finish_reason: str = ""
    success: bool = True
    error_message: str = ""


class LLMProvider(ABC):
    """Bazowa klasa dla dostawców LLM"""
    
    @abstractmethod
    def generate(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> LLMResponse:
        """
        Generuje odpowiedź na podstawie wiadomości.
        
        Args:
            messages: Lista wiadomości konwersacji
            project_context: Opcjonalny kontekst projektu
            sentiment: Wykryty sentyment użytkownika
            max_tokens: Maksymalna liczba tokenów odpowiedzi
            temperature: Temperatura generowania
            
        Returns:
            LLMResponse z odpowiedzią
        """
        pass
    
    @abstractmethod
    def generate_stream(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        """Generuje odpowiedź strumieniowo"""
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdza czy dostawca jest dostępny"""
        pass
    
    def build_system_prompt(
        self,
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None
    ) -> str:
        """Buduje prompt systemowy"""
        base_prompt = """Jesteś Rubber Duck Assistant - pomocnym asystentem dla programistów.
Twoja rola to Senior Developer/Mentor który:
- Pomaga w analizie logiki i rozwiązywaniu problemów
- Sugeruje biblioteki i frameworki
- Proponuje alternatywne wzorce projektowe  
- Zadaje pytania naprowadzające, aby użytkownik sam doszedł do rozwiązania
- Wspiera emocjonalnie w momentach frustracji

Odpowiadaj po polsku, zwięźle ale pomocnie."""

        parts = [base_prompt]
        
        if project_context:
            parts.append(f"\n\nKONTEKST PROJEKTU:\n{project_context.to_prompt()}")
        
        if sentiment:
            sentiment_instructions = {
                "negative": "\n\nUżytkownik wydaje się sfrustrowany. Bądź empatyczny, uspokajający. Zasugeruj przerwę jeśli potrzebna.",
                "positive": "\n\nUżytkownik jest pozytywnie nastawiony. Bądź konkretny i techniczny.",
                "neutral": ""
            }
            parts.append(sentiment_instructions.get(sentiment, ""))
        
        return "".join(parts)


class ClaudeLLM(LLMProvider):
    """Implementacja LLM używająca Claude (Anthropic)"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "claude-3-sonnet-20240229"):
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.anthropic.com/v1"
    
    def generate(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> LLMResponse:
        # TODO: Implementacja Claude API
        raise NotImplementedError("Claude LLM nie jest jeszcze zaimplementowany")
    
    def generate_stream(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        # TODO: Implementacja streamingu Claude API
        raise NotImplementedError("Claude LLM streaming nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class GeminiLLM(LLMProvider):
    """Implementacja LLM używająca Gemini (Google)"""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "gemini-pro"):
        self.api_key = api_key
        self.model = model
    
    def generate(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> LLMResponse:
        # TODO: Implementacja Gemini API
        raise NotImplementedError("Gemini LLM nie jest jeszcze zaimplementowany")
    
    def generate_stream(
        self,
        messages: list[Message],
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> Generator[str, None, None]:
        # TODO: Implementacja streamingu Gemini API
        raise NotImplementedError("Gemini LLM streaming nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        return bool(self.api_key)


class LLMManager:
    """
    Manager LLM - zarządza dostawcami i kontekstem konwersacji.
    """
    
    def __init__(self):
        self.providers: dict[str, LLMProvider] = {}
        self.active_provider: Optional[str] = None
        self.conversation_history: list[Message] = []
        self.max_history_length: int = 20
    
    def register_provider(self, name: str, provider: LLMProvider):
        """Rejestruje dostawcę LLM"""
        self.providers[name] = provider
    
    def set_active_provider(self, name: str) -> bool:
        """Ustawia aktywnego dostawcę"""
        if name in self.providers and self.providers[name].is_available():
            self.active_provider = name
            return True
        return False
    
    def chat(
        self,
        user_message: str,
        project_context: Optional[ProjectContext] = None,
        sentiment: Optional[str] = None
    ) -> Optional[LLMResponse]:
        """
        Wysyła wiadomość i otrzymuje odpowiedź.
        
        Args:
            user_message: Wiadomość użytkownika
            project_context: Kontekst projektu
            sentiment: Wykryty sentyment
            
        Returns:
            LLMResponse lub None jeśli błąd
        """
        if not self.active_provider:
            for name, provider in self.providers.items():
                if provider.is_available():
                    self.active_provider = name
                    break
        
        if not self.active_provider:
            return None
        
        provider = self.providers.get(self.active_provider)
        if not provider:
            return None
        
        # Dodaj wiadomość do historii
        self.conversation_history.append(
            Message(role=MessageRole.USER, content=user_message)
        )
        
        # Ogranicz historię
        if len(self.conversation_history) > self.max_history_length:
            self.conversation_history = self.conversation_history[-self.max_history_length:]
        
        # Generuj odpowiedź
        response = provider.generate(
            messages=self.conversation_history,
            project_context=project_context,
            sentiment=sentiment
        )
        
        if response.success:
            self.conversation_history.append(
                Message(role=MessageRole.ASSISTANT, content=response.content)
            )
        
        return response
    
    def clear_history(self):
        """Czyści historię konwersacji"""
        self.conversation_history = []
    
    def get_available_providers(self) -> list[str]:
        """Zwraca listę dostępnych dostawców"""
        return [name for name, p in self.providers.items() if p.is_available()]
