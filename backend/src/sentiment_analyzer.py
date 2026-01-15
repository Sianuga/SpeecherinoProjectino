"""
Moduł Analizy Sentymentu
Używa modelu HerBERT (Voicelab/herbert-base-cased-sentiment) do analizy emocji w tekście polskim.
"""

from typing import Optional
from dataclasses import dataclass
from enum import Enum

import numpy as np


class Sentiment(Enum):
    """Typy sentymentu"""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"


@dataclass
class SentimentResult:
    """Wynik analizy sentymentu"""
    sentiment: Sentiment
    confidence: float
    scores: dict

    def to_dict(self) -> dict:
        return {
            "sentiment": self.sentiment.value,
            "confidence": self.confidence,
            "scores": self.scores
        }


class HerBERTSentimentAnalyzer:
    """
    Analizator sentymentu używający modelu HerBERT.
    Model: Voicelab/herbert-base-cased-sentiment

    Zwraca trzy klasy: negative (0), neutral (1), positive (2)
    """

    MODEL_NAME = "Voicelab/herbert-base-cased-sentiment"

    def __init__(self):
        self.tokenizer = None
        self.model = None
        self._loaded = False

        # Mapowanie ID na etykiety
        self.id2label = {
            0: Sentiment.NEGATIVE,
            1: Sentiment.NEUTRAL,
            2: Sentiment.POSITIVE
        }

    def _load_model(self):
        """Ładuje model (lazy loading)"""
        if self._loaded:
            return True

        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification

            print(f"[Sentiment] Ładuję model {self.MODEL_NAME}...")

            self.tokenizer = AutoTokenizer.from_pretrained(self.MODEL_NAME)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.MODEL_NAME)

            self._loaded = True
            print("[Sentiment] Model załadowany pomyślnie")
            return True

        except Exception as e:
            print(f"[Sentiment] Błąd ładowania modelu: {e}")
            return False

    def analyze(self, text: str) -> SentimentResult:
        """
        Analizuje sentyment tekstu.

        Args:
            text: Tekst do analizy (po polsku)

        Returns:
            SentimentResult z wynikiem analizy
        """
        # Załaduj model jeśli nie załadowany
        if not self._load_model():
            return SentimentResult(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0,
                scores={"negative": 0.33, "neutral": 0.34, "positive": 0.33}
            )

        try:
            # Tokenizacja
            encoding = self.tokenizer(
                [text],
                add_special_tokens=True,
                return_token_type_ids=True,
                truncation=True,
                max_length=512,
                padding='max_length',
                return_attention_mask=True,
                return_tensors='pt'
            )

            # Predykcja
            import torch
            with torch.no_grad():
                output = self.model(**encoding)
                logits = output.logits.cpu().numpy()

            # Softmax dla prawdopodobieństw
            exp_logits = np.exp(logits - np.max(logits))
            probs = exp_logits / exp_logits.sum(axis=1, keepdims=True)
            probs = probs[0]  # Pierwszy (jedyny) przykład

            # Znajdź najwyższy wynik
            prediction_id = int(np.argmax(probs))
            confidence = float(probs[prediction_id])
            sentiment = self.id2label[prediction_id]

            scores = {
                "negative": float(probs[0]),
                "neutral": float(probs[1]),
                "positive": float(probs[2])
            }

            print(f"[Sentiment] Tekst: '{text[:50]}...' -> {sentiment.value} ({confidence:.2f})")

            return SentimentResult(
                sentiment=sentiment,
                confidence=confidence,
                scores=scores
            )

        except Exception as e:
            print(f"[Sentiment] Błąd analizy: {e}")
            return SentimentResult(
                sentiment=Sentiment.NEUTRAL,
                confidence=0.0,
                scores={"negative": 0.33, "neutral": 0.34, "positive": 0.33}
            )

    def is_available(self) -> bool:
        """Sprawdza czy model jest dostępny"""
        try:
            import transformers
            import torch
            return True
        except ImportError:
            return False