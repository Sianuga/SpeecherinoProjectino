"""
Moduł Analizy Sentymentu
Odpowiedzialny za analizę emocjonalną tekstu użytkownika.

Planowane implementacje:
- HerBERT (polski model)
- Prosty analizator bazujący na słowach kluczowych
- LLM-based analysis
"""

from abc import ABC, abstractmethod
from typing import Optional
from dataclasses import dataclass
from enum import Enum


class Sentiment(Enum):
    """Typy sentymentu"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Wynik analizy sentymentu"""
    sentiment: Sentiment
    confidence: float  # 0.0 - 1.0
    scores: dict[str, float] = None  # positive, negative, neutral scores
    
    def __post_init__(self):
        if self.scores is None:
            self.scores = {}


class SentimentAnalyzer(ABC):
    """Bazowa klasa dla analizatorów sentymentu"""
    
    @abstractmethod
    def analyze(self, text: str) -> SentimentResult:
        """
        Analizuje sentyment tekstu.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            SentimentResult z wynikiem analizy
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """Sprawdza czy analizator jest dostępny"""
        pass


class KeywordSentimentAnalyzer(SentimentAnalyzer):
    """
    Prosty analizator bazujący na słowach kluczowych.
    Szybki ale mniej dokładny.
    """
    
    def __init__(self):
        # Polskie słowa kluczowe
        self.negative_keywords = {
            # Frustracja
            "kurde", "kurwa", "cholera", "do diabła", "szlag",
            # Zmęczenie
            "zmęczony", "zmęczona", "wykończony", "wykończona", "padnięty",
            # Problemy
            "nie działa", "nie wiem", "nie rozumiem", "nie mogę",
            "błąd", "error", "bug", "problem", "utknąłem", "utknęłam",
            # Negatywne emocje
            "zły", "zła", "wkurzony", "wkurzona", "sfrustrowany", "sfrustrowana",
            "denerwuje", "irytuje", "wnerwiający", "głupi", "głupie",
            # Rezygnacja
            "poddaję się", "nie dam rady", "beznadziejne", "bezsensowne"
        }
        
        self.positive_keywords = {
            # Sukces
            "działa", "udało się", "rozwiązałem", "rozwiązałam",
            "naprawiłem", "naprawiłam", "znalazłem", "znalazłam",
            # Pozytywne emocje
            "super", "świetnie", "wspaniale", "ekstra", "fajnie",
            "rewelacja", "bomba", "git", "spoko",
            # Entuzjazm
            "ciekawe", "interesujące", "pomysł", "idea",
            # Pewność
            "wiem", "rozumiem", "jasne", "proste"
        }
    
    def analyze(self, text: str) -> SentimentResult:
        text_lower = text.lower()
        
        negative_count = sum(1 for kw in self.negative_keywords if kw in text_lower)
        positive_count = sum(1 for kw in self.positive_keywords if kw in text_lower)
        
        total = negative_count + positive_count
        
        if total == 0:
            return SentimentResult(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.5,
                scores={"positive": 0.33, "negative": 0.33, "neutral": 0.34}
            )
        
        positive_score = positive_count / total
        negative_score = negative_count / total
        
        if negative_score > positive_score:
            sentiment = Sentiment.NEGATIVE
            confidence = min(0.9, 0.5 + negative_score * 0.4)
        elif positive_score > negative_score:
            sentiment = Sentiment.POSITIVE
            confidence = min(0.9, 0.5 + positive_score * 0.4)
        else:
            sentiment = Sentiment.NEUTRAL
            confidence = 0.5
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            scores={
                "positive": positive_score,
                "negative": negative_score,
                "neutral": max(0, 1 - positive_score - negative_score)
            }
        )
    
    def is_available(self) -> bool:
        return True


class HerBERTSentimentAnalyzer(SentimentAnalyzer):
    """
    Analizator używający HerBERT - polskiego modelu BERT.
    Wymaga transformers i torch.
    """
    
    def __init__(self, model_name: str = "allegro/herbert-base-cased"):
        self.model_name = model_name
        self.model = None
        self.tokenizer = None
    
    def _load_model(self):
        """Ładuje model (lazy loading)"""
        if self.model is None:
            # TODO: Załaduj model
            pass
    
    def analyze(self, text: str) -> SentimentResult:
        # TODO: Implementacja analizy HerBERT
        raise NotImplementedError("HerBERT analyzer nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        try:
            import transformers
            import torch
            return True
        except ImportError:
            return False


class LLMSentimentAnalyzer(SentimentAnalyzer):
    """
    Analizator używający LLM do analizy sentymentu.
    Najbardziej dokładny ale najwolniejszy.
    """
    
    def __init__(self, llm_provider=None):
        self.llm_provider = llm_provider
    
    def analyze(self, text: str) -> SentimentResult:
        # TODO: Implementacja analizy przez LLM
        raise NotImplementedError("LLM sentiment analyzer nie jest jeszcze zaimplementowany")
    
    def is_available(self) -> bool:
        return self.llm_provider is not None


class SentimentManager:
    """
    Manager sentymentu - wybiera najlepszy dostępny analizator.
    """
    
    def __init__(self):
        self.analyzers: dict[str, SentimentAnalyzer] = {}
        self.active_analyzer: Optional[str] = None
        
        # Domyślnie rejestruj prosty analizator
        self.register_analyzer("keyword", KeywordSentimentAnalyzer())
    
    def register_analyzer(self, name: str, analyzer: SentimentAnalyzer):
        """Rejestruje analizator"""
        self.analyzers[name] = analyzer
    
    def set_active_analyzer(self, name: str) -> bool:
        """Ustawia aktywny analizator"""
        if name in self.analyzers and self.analyzers[name].is_available():
            self.active_analyzer = name
            return True
        return False
    
    def analyze(self, text: str) -> SentimentResult:
        """
        Analizuje sentyment tekstu.
        
        Args:
            text: Tekst do analizy
            
        Returns:
            SentimentResult
        """
        if not self.active_analyzer:
            # Znajdź dostępny analizator (preferuj lepsze)
            priority = ["herbert", "llm", "keyword"]
            for name in priority:
                if name in self.analyzers and self.analyzers[name].is_available():
                    self.active_analyzer = name
                    break
        
        if not self.active_analyzer:
            # Fallback do neutralnego
            return SentimentResult(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0
            )
        
        analyzer = self.analyzers.get(self.active_analyzer)
        if analyzer:
            return analyzer.analyze(text)
        
        return SentimentResult(sentiment=Sentiment.NEUTRAL, confidence=0.0)
    
    def get_available_analyzers(self) -> list[str]:
        """Zwraca listę dostępnych analizatorów"""
        return [name for name, a in self.analyzers.items() if a.is_available()]
