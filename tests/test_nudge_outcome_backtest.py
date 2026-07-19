import asyncio
from pathlib import Path

from app.stream import ScriptedClass, replay_events
from scripts.backtest_nudge_outcome import OUTCOME_DIR, backtest_all, write_report


def test_two_matched_outcome_pairs_replay_with_arm_marker():
    paths = sorted(OUTCOME_DIR.glob("*.json"))
    assert len(paths) == 4
    for path in paths:
        lesson = ScriptedClass.load(path.stem, OUTCOME_DIR)
        events = asyncio.run(_collect(lesson))
        assert events
        assert all(event["nudge_applied"] is lesson.nudge_applied for event in events)


async def _collect(lesson):
    return [event async for event in replay_events(lesson, speed=100_000)]


def test_outcome_backtest_reports_positive_matched_deltas_and_caveat():
    results = backtest_all()
    assert len(results["pairs"]) == 2
    assert results["aggregate"]["poll_correctness_delta"] > 0
    assert all(pair["reframed_poll_correctness"] > pair["control_poll_correctness"] for pair in results["pairs"])
    output = Path("validation/test-nudge-outcomes.md")
    try:
        write_report(results, output)
        text = output.read_text(encoding="utf-8")
        assert "not a causal experiment" in text.lower()
        assert "Control" in text and "Reframed" in text
    finally:
        output.unlink(missing_ok=True)
