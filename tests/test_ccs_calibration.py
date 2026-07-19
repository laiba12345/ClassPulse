from pathlib import Path

from app.ccs import CCSEngine, SignalWindow
from scripts.calibrate_ccs_confidence import build_calibration, write_report


def test_evidence_quality_rewards_distinct_signals_not_repeated_raw_points():
    repeated = SignalWindow(sentiments=[("confused", .9)] * 4, active_students=4, student_ids=["s1"] * 4)
    corroborated = SignalWindow(
        sentiments=[("confused", .9)], keyword_flags=2, response_latencies=[35],
        poll_correct=[False], active_students=4, student_ids=["s1"],
    )
    assert CCSEngine().score(corroborated).evidence_quality > CCSEngine().score(repeated).evidence_quality


def test_calibration_report_is_repeatable_and_explicit_about_small_sample():
    calibration = build_calibration()
    assert calibration["alert_points"] > 0
    assert calibration["buckets"]
    assert all(0 <= bucket["empirical_precision"] <= 1 for bucket in calibration["buckets"])
    output = Path("validation/test-confidence-calibration.md")
    try:
        write_report(calibration, output)
        text = output.read_text(encoding="utf-8")
        assert "Empirical precision" in text
        assert "still uncalibrated" in text
    finally:
        output.unlink(missing_ok=True)
