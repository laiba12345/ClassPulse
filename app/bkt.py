from __future__ import annotations

from dataclasses import dataclass


@dataclass
class MasteryState:
    mastery: float
    observations: int = 0
    correct: int = 0
    soft_updates: int = 0


class BKTTracker:
    def __init__(self, initial_mastery=.35, learn=.12, slip=.1, guess=.2, ccs_lambda=.18):
        self.initial_mastery, self.learn, self.slip, self.guess, self.ccs_lambda = initial_mastery, learn, slip, guess, ccs_lambda
        self.states: dict[tuple[str, str], MasteryState] = {}

    def _state(self, student_id: str, concept: str) -> MasteryState:
        return self.states.setdefault((student_id, concept), MasteryState(self.initial_mastery))

    def get(self, student_id: str, concept: str) -> float:
        return self._state(student_id, concept).mastery

    def update_mastery(self, student_id: str, concept: str, correct: bool | None, ccs: float | None) -> float:
        if correct is None and ccs is None:
            raise ValueError("correctness evidence, CCS evidence, or both are required")
        state = self._state(student_id, concept); mastery = state.mastery
        if correct is not None:
            if correct:
                posterior = mastery * (1 - self.slip) / (mastery * (1 - self.slip) + (1 - mastery) * self.guess)
                state.correct += 1
            else:
                posterior = mastery * self.slip / (mastery * self.slip + (1 - mastery) * (1 - self.guess))
            mastery = posterior + (1 - posterior) * self.learn
            state.observations += 1
        if ccs is not None:
            mastery -= self.ccs_lambda * max(0.0, min(1.0, ccs)) * mastery
            state.soft_updates += 1
        state.mastery = round(max(.01, min(.99, mastery)), 4)
        return state.mastery

    def snapshot(self, concept: str, students: list[str]) -> list[dict]:
        output = []
        for student in students:
            state = self._state(student, concept)
            output.append({
                "student_id": student.lower().replace(" ", "-"), "name": student, "concept": concept,
                "mastery": state.mastery, "observations": state.observations,
                "confidence": round(min(.95, .4 + .1 * state.observations + .025 * state.soft_updates), 2),
                "evidence": f"{state.observations} graded and {state.soft_updates} CCS soft-evidence updates.",
                "limitations": "BKT is an estimate based on the current scripted session, not a fixed learner label.",
            })
        return output
