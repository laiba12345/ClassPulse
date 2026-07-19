"""Matched authored-scenario nudge outcome check—not a causal experiment."""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.llm import DemoStructuredProvider
from app.runtime import ClassRuntime
from app.stream import ScriptedClass

OUTCOME_DIR = ROOT / "data" / "outcome_pairs"
DEFAULT_REPORT = ROOT / "validation" / "NUDGE_OUTCOME_BACKTEST.md"


async def _replay_arm(path: Path) -> dict:
    raw = json.loads(path.read_text(encoding="utf-8"))
    lesson = ScriptedClass.load(path.stem, OUTCOME_DIR)
    runtime = ClassRuntime(lesson, DemoStructuredProvider())
    current_event = None
    trigger_at = None
    outcome_poll = None
    async for message in runtime.run(speed=100_000):
        if message["kind"] == "event":
            current_event = message["data"]
            if trigger_at is not None and current_event["type"] == "poll" and current_event["at"] > trigger_at and outcome_poll is None:
                responses = current_event["responses"]
                outcome_poll = {
                    "at": current_event["at"], "question": current_event["question"],
                    "correct": sum(responses.values()), "responses": len(responses),
                    "correctness": round(sum(responses.values()) / len(responses), 3),
                }
        elif message["kind"] == "nudge":
            trigger_at = current_event["at"] if current_event else None
    if trigger_at is None or outcome_poll is None:
        raise ValueError(f"{path.name} did not produce a nudge followed by a poll")
    return {
        "pair_id": raw["pair_id"], "arm": raw["arm"], "concept": raw["concept"],
        "nudge_applied": lesson.nudge_applied, "trigger_at": trigger_at,
        "outcome_poll": outcome_poll,
    }


def replay_arm(path: Path) -> dict:
    return asyncio.run(_replay_arm(path))


def backtest_all() -> dict:
    grouped: dict[str, dict[str, dict]] = defaultdict(dict)
    for path in sorted(OUTCOME_DIR.glob("*.json")):
        arm = replay_arm(path)
        grouped[arm["pair_id"]][arm["arm"]] = arm
    pairs = []
    for pair_id, arms in sorted(grouped.items()):
        if set(arms) != {"control", "reframed"}:
            raise ValueError(f"{pair_id} must have control and reframed arms")
        control, reframed = arms["control"], arms["reframed"]
        if control["trigger_at"] != reframed["trigger_at"] or control["outcome_poll"]["at"] != reframed["outcome_poll"]["at"]:
            raise ValueError(f"{pair_id} arms are not timeline-matched")
        pairs.append({
            "pair_id": pair_id, "concept": control["concept"], "trigger_at": control["trigger_at"],
            "outcome_poll_at": control["outcome_poll"]["at"],
            "control_poll_correctness": control["outcome_poll"]["correctness"],
            "reframed_poll_correctness": reframed["outcome_poll"]["correctness"],
            "poll_correctness_delta": round(reframed["outcome_poll"]["correctness"] - control["outcome_poll"]["correctness"], 3),
            "control_nudge_applied": control["nudge_applied"], "reframed_nudge_applied": reframed["nudge_applied"],
        })
    control_mean = sum(pair["control_poll_correctness"] for pair in pairs) / len(pairs)
    reframed_mean = sum(pair["reframed_poll_correctness"] for pair in pairs) / len(pairs)
    return {
        "pairs": pairs,
        "aggregate": {
            "pair_count": len(pairs), "control_poll_correctness": round(control_mean, 3),
            "reframed_poll_correctness": round(reframed_mean, 3),
            "poll_correctness_delta": round(reframed_mean - control_mean, 3),
        },
        "claim_boundary": "Authored matched-scenario behavior only; not a causal experiment or evidence of real student learning.",
    }


def write_report(results: dict, output: Path = DEFAULT_REPORT) -> Path:
    lines = [
        "# Nudge outcome backtest", "",
        "> **Authored matched-scenario comparison—not a causal experiment.** Improved responses are written into the reframed arms; this checks outcome-linking instrumentation and analysis, not whether nudges cause real learning.", "",
        "| Pair | Concept | Trigger | Next poll | Control | Reframed | Delta |", "|---|---|---:|---:|---:|---:|---:|",
    ]
    for pair in results["pairs"]:
        lines.append(f"| {pair['pair_id']} | {pair['concept']} | +{pair['trigger_at']}s | +{pair['outcome_poll_at']}s | {pair['control_poll_correctness']:.3f} | {pair['reframed_poll_correctness']:.3f} | {pair['poll_correctness_delta']:+.3f} |")
    aggregate = results["aggregate"]
    lines += [
        "", "## Aggregate", "",
        f"- Matched pairs: **{aggregate['pair_count']}**", f"- Control next-poll correctness: **{aggregate['control_poll_correctness']:.3f}**",
        f"- Reframed next-poll correctness: **{aggregate['reframed_poll_correctness']:.3f}**", f"- Authored delta: **{aggregate['poll_correctness_delta']:+.3f}**", "",
        "## What this establishes", "",
        "Both arms replay through the production runtime, trigger at the same timestamp, carry an explicit `nudge_applied` marker, and link the trigger to the immediately following poll. The analysis detects the authored control-versus-reframed difference.", "",
        "## What this does not establish", "",
        "The fixtures do not contain real teachers or students, random assignment, blinded grading, independent outcomes, or enough pairs for inference. The positive delta is authored by construction and cannot be interpreted as a treatment effect.", "",
        "## Machine-readable detail", "", "```json", json.dumps(results, indent=2), "```", "",
    ]
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(lines), encoding="utf-8")
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description="Backtest authored matched nudge-outcome pairs.")
    parser.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    results = backtest_all()
    path = write_report(results, args.output)
    print("AUTHORED MATCHED SCENARIOS — not a causal experiment")
    for pair in results["pairs"]:
        print(f"{pair['pair_id']}: {pair['control_poll_correctness']:.3f} -> {pair['reframed_poll_correctness']:.3f} ({pair['poll_correctness_delta']:+.3f})")
    print(f"Aggregate delta: {results['aggregate']['poll_correctness_delta']:+.3f}")
    print(f"Wrote {path}")


if __name__ == "__main__":
    main()
