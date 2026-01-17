"""
Moduł LLM (Large Language Model)
Integracja z Google Gemini API.
"""

import os
from typing import Optional, List
from dataclasses import dataclass, field

from google import genai
from google.genai import types


@dataclass
class ProjectContext:
    """Kontekst projektu dla LLM"""
    name: str
    description: str = ""
    tech_stack: List[str] = field(default_factory=list)
    business_assumptions: str = ""
    additional_context: str = ""

    def to_prompt_section(self) -> str:
        """Konwertuje kontekst projektu na sekcję promptu"""
        lines = [f"Projekt: {self.name}"]

        if self.description:
            lines.append(f"Opis: {self.description}")

        if self.tech_stack:
            lines.append(f"Stack technologiczny: {', '.join(self.tech_stack)}")

        if self.business_assumptions:
            lines.append(f"Założenia biznesowe: {self.business_assumptions}")

        if self.additional_context:
            lines.append(f"Dodatkowy kontekst: {self.additional_context}")

        return "\n".join(lines)


@dataclass
class LLMResponse:
    """Odpowiedź z modelu LLM"""
    content: str
    success: bool = True
    error_message: str = ""
    model: str = ""


class PromptBuilder:
    """
    Buduje prompt kontekstowy dla LLM.

    Składa się z:
    1. Persona - opis roli i zachowania (Senior Mentor Dev)
    2. Kontekst projektu - informacje o projekcie użytkownika
    3. Historia rozmowy - poprzednie wiadomości z sesji
    4. Informacja o sentymencie - emocjonalny stan użytkownika
    """

    PERSONA = """Jesteś Rubber Duck Assistant - doświadczonym Senior Developerem i Mentorem.

## Twoja rola:
- Pomagasz programistom rozwiązywać problemy metodą "rubber duck debugging"
- Słuchasz opisu problemu i zadajesz pytania naprowadzające
- NIE dajesz od razu gotowych rozwiązań - pomagasz użytkownikowi samemu dojść do odpowiedzi
- Sugerujesz biblioteki, frameworki i wzorce projektowe gdy to pomocne

## Twój styl:
- Odpowiadasz po polsku, zwięźle i rzeczowo
- Jesteś konkretny i na temat
- Jeśli nie jesteś pewny o co chodzi użytkownikowi - ZAWSZE najpierw dopytaj
- Zadajesz jedno pytanie na raz
- Unikasz zbędnego gadania - liczy się treść

## Zasady:
- Jeśli pytanie jest niejasne - zacznij od dopytania "Czy dobrze rozumiem, że...?" lub "Możesz doprecyzować...?"
- Zawsze odnosisz się do kontekstu projektu użytkownika
- Pamiętasz o czym była rozmowa w tej sesji
- Jeśli nie znasz odpowiedzi - mówisz to wprost"""

    SENTIMENT_INSTRUCTIONS = {
        "negative": """
UWAGA: Użytkownik wydaje się sfrustrowany.
- Okaż zrozumienie krótko ("Rozumiem frustrację")
- Bądź szczególnie konkretny i pomocny
- Możesz zasugerować przerwę jeśli problem jest złożony""",

        "positive": """
Użytkownik jest pozytywnie nastawiony - możesz być bardziej bezpośredni.""",

        "neutral": ""
    }

    def __init__(self):
        self.project_context: Optional[ProjectContext] = None
        self.conversation_history: List[dict] = []
        self.current_sentiment: Optional[str] = None
        self.sentiment_confidence: float = 0.0

    def set_project_context(self, project: dict):
        """Ustawia kontekst projektu"""
        self.project_context = ProjectContext(
            name=project.get("name", "Nieznany projekt"),
            description=project.get("description", ""),
            tech_stack=project.get("tech_stack", []),
            business_assumptions=project.get("business_assumptions", ""),
            additional_context=project.get("additional_context", "")
        )

    def set_conversation_history(self, history: List[dict]):
        """Ustawia historię konwersacji"""
        self.conversation_history = history

    def set_sentiment(self, sentiment: str, confidence: float = 0.0):
        """Ustawia wykryty sentyment"""
        self.current_sentiment = sentiment
        self.sentiment_confidence = confidence

    def build_system_prompt(self) -> str:
        """Buduje pełny system prompt"""
        sections = [self.PERSONA]

        # Kontekst projektu
        if self.project_context:
            sections.append(f"\n## Kontekst projektu użytkownika:\n{self.project_context.to_prompt_section()}")

        # Instrukcje sentymentu
        if self.current_sentiment and self.sentiment_confidence > 0.6:
            sentiment_instruction = self.SENTIMENT_INSTRUCTIONS.get(self.current_sentiment, "")
            if sentiment_instruction:
                sections.append(sentiment_instruction)

        return "\n".join(sections)

    def build_contents_for_gemini(self, user_message: str) -> List[types.Content]:
        """
        Buduje listę contents dla Gemini API.

        Historia z conversation_store ma format:
        [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]

        Gemini API wymaga:
        - role: "user" lub "model" (nie "assistant")
        - parts: lista obiektów Part

        Args:
            user_message: Bieżąca wiadomość użytkownika

        Returns:
            Lista types.Content dla API
        """
        contents = []

        # Historia konwersacji
        for msg in self.conversation_history:
            role = msg["role"]
            content = msg["content"]

            # Gemini używa "model" zamiast "assistant"
            gemini_role = "model" if role == "assistant" else "user"

            # Prawidłowy sposób tworzenia Content w google-genai SDK
            contents.append(
                types.Content(
                    role=gemini_role,
                    parts=[types.Part(text=content)]
                )
            )

        # Bieżąca wiadomość użytkownika
        contents.append(
            types.Content(
                role="user",
                parts=[types.Part(text=user_message)]
            )
        )

        return contents

    def get_context_summary(self) -> str:
        """Zwraca podsumowanie kontekstu (do logowania)"""
        lines = ["=== Kontekst Promptu ==="]

        if self.project_context:
            lines.append(f"Projekt: {self.project_context.name}")
            if self.project_context.tech_stack:
                lines.append(f"Stack: {', '.join(self.project_context.tech_stack[:3])}")
        else:
            lines.append("Projekt: Brak")

        lines.append(f"Historia: {len(self.conversation_history)} wiadomości")
        lines.append(f"Sentyment: {self.current_sentiment} ({self.sentiment_confidence:.2f})")

        return "\n".join(lines)


class GeminiLLM:
    """
    Integracja z Google Gemini API.

    Używa google-genai SDK.
    """

    MODEL = "gemini-2.5-flash-lite"

    def __init__(self, api_key: Optional[str] = None):
        """
        Inicjalizuje klienta Gemini.

        Args:
            api_key: Klucz API Google (GEMINI_API_KEY)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "") or os.getenv("GOOGLE_API_KEY", "")
        self.client = None
        self.prompt_builder = PromptBuilder()

        if self.is_available():
            self.client = genai.Client(api_key=self.api_key)
            print(f"[LLM] Gemini client zainicjalizowany (model: {self.MODEL})")

    def set_project(self, project: dict):
        """Ustawia kontekst projektu"""
        self.prompt_builder.set_project_context(project)

    def set_history(self, history: List[dict]):
        """Ustawia historię konwersacji"""
        self.prompt_builder.set_conversation_history(history)

    def set_sentiment(self, sentiment: str, confidence: float):
        """Ustawia sentyment"""
        self.prompt_builder.set_sentiment(sentiment, confidence)

    def generate_response(self, user_message: str) -> LLMResponse:
        """
        Generuje odpowiedź na wiadomość użytkownika.

        Args:
            user_message: Wiadomość użytkownika (transkrypcja)

        Returns:
            LLMResponse z odpowiedzią
        """
        if not self.is_available():
            return LLMResponse(
                content="",
                success=False,
                error_message="Brak klucza API Gemini"
            )

        if not self.client:
            return LLMResponse(
                content="",
                success=False,
                error_message="Klient Gemini nie zainicjalizowany"
            )

        try:
            # Zbuduj system prompt
            system_prompt = self.prompt_builder.build_system_prompt()

            # Zbuduj contents z historią (używa istniejącej metody)
            contents = self.prompt_builder.build_contents_for_gemini(user_message)

            # Debug
            print(f"\n{self.prompt_builder.get_context_summary()}")
            print(f"Wiadomość użytkownika: {user_message[:100]}...")

            # Wywołaj API
            response = self.client.models.generate_content(
                model=self.MODEL,
                contents=contents,
                config=types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    temperature=0.7,
                    max_output_tokens=1024,
                )
            )

            # Wyciągnij tekst odpowiedzi
            response_text = response.text if response.text else ""

            print(f"[LLM] Odpowiedź: {response_text[:100]}...")

            return LLMResponse(
                content=response_text,
                success=True,
                model=self.MODEL
            )

        except Exception as e:
            error_msg = f"Błąd Gemini API: {str(e)}"
            print(f"[LLM] {error_msg}")

            import traceback
            traceback.print_exc()

            return LLMResponse(
                content="",
                success=False,
                error_message=error_msg
            )

    def is_available(self) -> bool:
        """Sprawdza czy API key jest ustawiony"""
        return bool(self.api_key and len(self.api_key) > 10)