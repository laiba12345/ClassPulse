from __future__ import annotations

from app.llm import NudgeResult, StructuredProvider
from app.outcomes import OutcomeTracker


class NudgeEngine:
    def __init__(self, provider: StructuredProvider, threshold=.6, reset_threshold=.4, outcomes: OutcomeTracker | None = None):
        self.provider, self.threshold, self.reset_threshold = provider, threshold, reset_threshold
        self.outcomes = outcomes or OutcomeTracker()
        self.active_spikes: set[str] = set()

    def consider(self, concept: str, ccs: float, evidence: dict) -> NudgeResult | None:
        selection = self.prepare(concept, ccs)
        if selection is None:
            return None
        strategy, mode, reason = selection
        return self.provider.generate_nudge(concept, evidence, strategy, mode, reason)

    def prepare(self, concept: str, ccs: float) -> tuple[str, str, str] | None:
        if ccs <= self.reset_threshold:
            self.active_spikes.discard(concept)
            return None
        if ccs < self.threshold or concept in self.active_spikes:
            return None
        self.active_spikes.add(concept)
        return self.outcomes.select_strategy(concept)
