from __future__ import annotations

import math
from dataclasses import dataclass, field

CONFUSION_TERMS = ("confused", "not sure", "don't understand", "doesn't make sense", "lost", "right?", "maybe")


@dataclass
class SignalWindow:
    sentiments: list[tuple[str, float]] = field(default_factory=list)
    keyword_flags: int = 0
    response_latencies: list[float] = field(default_factory=list)
    poll_correct: list[bool] = field(default_factory=list)
    student_quotes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class CCSResult:
    score: float
    sentiment_signal: float
    keyword_signal: float
    latency_signal: float
    poll_miss_rate: float
    evidence: dict
    confidence: float
    limitations: str

    def as_dict(self) -> dict:
        return self.__dict__


class CCSEngine:
    """Deterministic weighted-sigmoid fusion of four confusion signals."""

    def __init__(self, *, bias=-2.2, weights=(1.6, .8, .8, 1.8)):
        self.bias = bias
        self.weights = weights

    @staticmethod
    def keyword_count(text: str) -> int:
        lowered = text.lower()
        return sum(term in lowered for term in CONFUSION_TERMS)

    def score(self, window: SignalWindow) -> CCSResult:
        confused = [confidence for label, confidence in window.sentiments if label == "confused"]
        sentiment = sum(confused) / max(1, len(window.sentiments))
        keyword = min(1.0, window.keyword_flags / 3)
        average_latency = sum(window.response_latencies) / max(1, len(window.response_latencies))
        latency = min(1.0, max(0.0, (average_latency - 10) / 30))
        misses = sum(not answer for answer in window.poll_correct)
        poll_miss = misses / max(1, len(window.poll_correct)) if window.poll_correct else 0.0
        raw = self.bias + sum(weight * signal for weight, signal in zip(self.weights, (sentiment, keyword, latency, poll_miss)))
        value = 1 / (1 + math.exp(-raw))
        evidence = {
            "confused_lines": len(confused), "keyword_flags": window.keyword_flags,
            "average_latency_seconds": round(average_latency, 1), "poll_misses": misses,
            "poll_responses": len(window.poll_correct), "student_quotes": window.student_quotes[-3:],
        }
        evidence_points = len(window.sentiments) + len(window.poll_correct) + len(window.response_latencies)
        return CCSResult(
            round(value, 3), round(sentiment, 3), round(keyword, 3), round(latency, 3), round(poll_miss, 3),
            evidence, round(min(.96, .5 + evidence_points * .05), 2),
            "CCS estimates confusion from observed language, latency, and polls; silence and non-verbal cues are not captured.",
        )
