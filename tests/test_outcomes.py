from app.outcomes import OutcomeTracker


def test_applied_nudge_links_baseline_and_next_poll_outcome():
    tracker = OutcomeTracker()
    record = tracker.register("fractions", trigger_at=10, baseline_correctness=.25)
    tracker.decide(record.nudge_id, "applied", decided_at=12)
    tracker.observe_poll("fractions", at=20, correctness=.75)
    result = tracker.get(record.nudge_id)
    assert result.decision == "applied"
    assert result.next_poll_correctness == .75
    assert result.correctness_delta == .5


def test_dismissed_nudge_is_recorded_but_not_attributed_as_applied():
    tracker = OutcomeTracker()
    record = tracker.register("forces", trigger_at=5, baseline_correctness=.5)
    tracker.decide(record.nudge_id, "dismissed", decided_at=6)
    tracker.observe_poll("forces", at=12, correctness=.75)
    result = tracker.get(record.nudge_id)
    assert result.decision == "dismissed"
    assert result.next_poll_correctness == .75
    assert result.applied is False


def test_strategy_evidence_counts_only_applied_complete_outcomes():
    tracker = OutcomeTracker()
    improved = tracker.register("fractions", 1, .25, strategy="visual_model")
    tracker.decide(improved.nudge_id, "applied", 2)
    dismissed = tracker.register("fractions", 3, .5, strategy="analogy")
    tracker.decide(dismissed.nudge_id, "dismissed", 4)
    pending = tracker.register("fractions", 5, .5, strategy="worked_example")
    tracker.observe_poll("fractions", 6, .75)
    evidence = tracker.strategy_evidence("fractions")
    assert evidence["visual_model"]["attempts"] == 1
    assert evidence["visual_model"]["mean_observed_delta"] == .5
    assert evidence["analogy"]["attempts"] == 0
    assert evidence["worked_example"]["attempts"] == 0


def test_strategy_selection_explores_sparse_or_worse_results():
    tracker = OutcomeTracker()
    strategy, mode, _ = tracker.select_strategy("forces")
    assert (strategy, mode) == ("visual_model", "exploration")
    record = tracker.register("forces", 1, .75, strategy="visual_model")
    tracker.decide(record.nudge_id, "applied", 2)
    tracker.observe_poll("forces", 3, .25)
    strategy, mode, _ = tracker.select_strategy("forces")
    assert strategy == "worked_example"
    assert mode == "exploration"


def test_positive_observed_strategy_evidence_informs_next_selection():
    tracker = OutcomeTracker()
    record = tracker.register("fractions", 1, .25, strategy="contrast_case")
    tracker.decide(record.nudge_id, "applied", 2)
    tracker.observe_poll("fractions", 3, .75)
    strategy, mode, reason = tracker.select_strategy("fractions")
    assert strategy == "contrast_case"
    assert mode == "evidence_informed"
    assert "one observed" in reason.lower()
