from app.llm import DemoStructuredProvider
from app.nudges import NudgeEngine

def test_one_concept_specific_nudge_per_spike():
    engine = NudgeEngine(DemoStructuredProvider(), threshold=.6, reset_threshold=.4)
    evidence = {"confused_lines": 3, "poll_misses": 2, "student_quotes": ["eight is bigger"]}
    first = engine.consider("fractions", .75, evidence)
    repeated = engine.consider("fractions", .82, evidence)
    assert first is not None
    assert first.concept == "fractions"
    assert "fraction" in first.suggested_reframing.lower()
    assert repeated is None

def test_calm_score_produces_no_nudge_and_resets_spike():
    engine = NudgeEngine(DemoStructuredProvider())
    assert engine.consider("forces", .2, {}) is None
