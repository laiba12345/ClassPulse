# Nudge outcome backtest

> **Authored matched-scenario comparison—not a causal experiment.** Improved responses are written into the reframed arms; this checks outcome-linking instrumentation and analysis, not whether nudges cause real learning.

| Pair | Concept | Trigger | Next poll | Control | Reframed | Delta |
|---|---|---:|---:|---:|---:|---:|
| forces-outcome | forces | +7s | +15s | 0.250 | 1.000 | +0.750 |
| fractions-outcome | fractions | +10s | +18s | 0.250 | 1.000 | +0.750 |

## Aggregate

- Matched pairs: **2**
- Control next-poll correctness: **0.250**
- Reframed next-poll correctness: **1.000**
- Authored delta: **+0.750**

## What this establishes

Both arms replay through the production runtime, trigger at the same timestamp, carry an explicit `nudge_applied` marker, and link the trigger to the immediately following poll. The analysis detects the authored control-versus-reframed difference.

## What this does not establish

The fixtures do not contain real teachers or students, random assignment, blinded grading, independent outcomes, or enough pairs for inference. The positive delta is authored by construction and cannot be interpreted as a treatment effect.

## Machine-readable detail

```json
{
  "pairs": [
    {
      "pair_id": "forces-outcome",
      "concept": "forces",
      "trigger_at": 7,
      "outcome_poll_at": 15,
      "control_poll_correctness": 0.25,
      "reframed_poll_correctness": 1.0,
      "poll_correctness_delta": 0.75,
      "control_nudge_applied": false,
      "reframed_nudge_applied": true
    },
    {
      "pair_id": "fractions-outcome",
      "concept": "fractions",
      "trigger_at": 10,
      "outcome_poll_at": 18,
      "control_poll_correctness": 0.25,
      "reframed_poll_correctness": 1.0,
      "poll_correctness_delta": 0.75,
      "control_nudge_applied": false,
      "reframed_nudge_applied": true
    }
  ],
  "aggregate": {
    "pair_count": 2,
    "control_poll_correctness": 0.25,
    "reframed_poll_correctness": 1.0,
    "poll_correctness_delta": 0.75
  },
  "claim_boundary": "Authored matched-scenario behavior only; not a causal experiment or evidence of real student learning."
}
```
