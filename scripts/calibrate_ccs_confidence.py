"""Bucket CCS evidence quality against authored-window empirical precision."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.backtest_ccs import backtest_all

DEFAULT_REPORT = ROOT / "validation" / "CCS_CONFIDENCE_CALIBRATION.md"


def build_calibration() -> dict:
    points = [
        {"evidence_quality": point["evidence_quality"], "correct": point["ground_truth_confused"], "state": point["state"], "fixture": fixture["fixture"]}
        for fixture in backtest_all() for point in fixture["timeline"] if point["state"] in {"warning", "confirmed"}
    ]
    grouped: dict[float, list[dict]] = defaultdict(list)
    for point in points:
        lower = int(point["evidence_quality"] * 10) / 10
        grouped[lower].append(point)
    buckets = []
    for lower, rows in sorted(grouped.items()):
        average = sum(row["evidence_quality"] for row in rows) / len(rows)
        precision = sum(row["correct"] for row in rows) / len(rows)
        buckets.append({
            "range": f"{lower:.1f}–{min(.99, lower + .09):.2f}", "count": len(rows),
            "average_evidence_quality": round(average, 3), "empirical_precision": round(precision, 3),
            "absolute_gap": round(abs(average - precision), 3),
        })
    weighted_gap = sum(bucket["absolute_gap"] * bucket["count"] for bucket in buckets) / max(1, len(points))
    return {
        "fixture_count": len(backtest_all()), "alert_points": len(points), "buckets": buckets,
        "weighted_absolute_gap": round(weighted_gap, 3),
        "status": "still uncalibrated",
        "formula": "0.45 + 0.08×distinct signal types + 0.12×student breadth + 0.08 if confirmed; capped at 0.92",
    }


def write_report(calibration: dict, output: Path = DEFAULT_REPORT) -> Path:
    lines = [
        "# CCS evidence-quality calibration check", "",
        f"**Status: {calibration['status']}.** Evidence quality is not a validated probability of correctness.", "",
        f"Checked {calibration['alert_points']} warning/confirmed event points across {calibration['fixture_count']} authored fixtures. The formula now counts distinct signal types and student breadth rather than raw repeated evidence points.", "",
        f"Formula: `{calibration['formula']}`", "",
        "| Evidence-quality bucket | Events | Mean evidence quality | Empirical precision | Absolute gap |", "|---|---:|---:|---:|---:|",
    ]
    for bucket in calibration["buckets"]:
        lines.append(f"| {bucket['range']} | {bucket['count']} | {bucket['average_evidence_quality']:.3f} | {bucket['empirical_precision']:.3f} | {bucket['absolute_gap']:.3f} |")
    lines += [
        "", f"Weighted absolute calibration gap: **{calibration['weighted_absolute_gap']:.3f}**.", "",
        "## Interpretation", "",
        "Empirical precision is the fraction of alert points inside authored confusion windows. The sample is small, event points within a lesson are correlated, and the fixtures were authored during development. The table can expose obviously misleading evidence-quality behavior, but it cannot calibrate a deployment probability. Educator-labeled held-out lessons are still required.", "",
        "## Machine-readable detail", "", "```json", json.dumps(calibration, indent=2), "```", "",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Check CCS evidence quality against authored fixtures.")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    calibration = build_calibration()
    path = write_report(calibration, args.output)
    print(f"Status: {calibration['status']}; weighted gap={calibration['weighted_absolute_gap']:.3f}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
