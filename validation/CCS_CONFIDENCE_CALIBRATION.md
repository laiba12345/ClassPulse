# CCS confidence calibration check

**Status: still uncalibrated.** Confidence is an evidence-quality heuristic, not a validated probability of correctness.

Checked 20 warning/confirmed event points across 9 authored fixtures. The formula now counts distinct signal types and student breadth rather than raw repeated evidence points.

Formula: `0.45 + 0.08×distinct signal types + 0.12×student breadth + 0.08 if confirmed; capped at 0.92`

| Confidence bucket | Events | Mean reported confidence | Empirical precision | Absolute gap |
|---|---:|---:|---:|---:|
| 0.6–0.69 | 2 | 0.655 | 0.000 | 0.655 |
| 0.7–0.79 | 7 | 0.751 | 1.000 | 0.249 |
| 0.8–0.89 | 3 | 0.830 | 0.333 | 0.497 |
| 0.9–0.99 | 8 | 0.913 | 0.875 | 0.038 |

Weighted absolute calibration gap: **0.242**.

## Interpretation

Empirical precision is the fraction of alert points inside authored confusion windows. The sample is small, event points within a lesson are correlated, and the fixtures were authored during development. The table can expose obviously misleading confidence behavior, but it cannot calibrate a deployment probability. Educator-labeled held-out lessons are still required.

## Machine-readable detail

```json
{
  "fixture_count": 9,
  "alert_points": 20,
  "buckets": [
    {
      "range": "0.6\u20130.69",
      "count": 2,
      "average_confidence": 0.655,
      "empirical_precision": 0.0,
      "absolute_gap": 0.655
    },
    {
      "range": "0.7\u20130.79",
      "count": 7,
      "average_confidence": 0.751,
      "empirical_precision": 1.0,
      "absolute_gap": 0.249
    },
    {
      "range": "0.8\u20130.89",
      "count": 3,
      "average_confidence": 0.83,
      "empirical_precision": 0.333,
      "absolute_gap": 0.497
    },
    {
      "range": "0.9\u20130.99",
      "count": 8,
      "average_confidence": 0.913,
      "empirical_precision": 0.875,
      "absolute_gap": 0.038
    }
  ],
  "weighted_absolute_gap": 0.242,
  "status": "still uncalibrated",
  "formula": "0.45 + 0.08\u00d7distinct signal types + 0.12\u00d7student breadth + 0.08 if confirmed; capped at 0.92"
}
```
