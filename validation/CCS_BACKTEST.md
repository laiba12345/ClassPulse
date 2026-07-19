# CCS Backtest

Generated from the three authored ClassPulse fixtures using the production CCS path and deterministic demo sentiment provider.

| Fixture | Precision | Recall | Poll prediction |
|---|---:|---:|---:|
| Balanced Forces and Motion | 1.000 | 0.500 | 0.000 (1 polls) |
| Comparing Fractions | 0.667 | 0.500 | 0.000 (2 polls) |
| Where Plant Mass Comes From | 1.000 | 0.500 | 0.000 (1 polls) |

## Aggregate

- Authored-window precision: **0.857**
- Authored-window recall: **0.500**
- Pre-poll majority-miss prediction: **0/4**
- Confusion matrix: `{'tp': 6, 'fp': 1, 'tn': 4, 'fn': 6}`

## Interpretation

This is fixture backtesting, not real-world confusion accuracy. Authored windows test whether the current threshold behaves as intended in known demo moments. Poll prediction uses only the CCS from the previous event, preventing poll-result leakage. The sample is three deliberately constructed lessons and is too small for calibration, fairness, or deployment claims.

## Machine-readable detail

```json
[
  {
    "fixture": "forces-live",
    "title": "Balanced Forces and Motion",
    "confusion_window": {
      "start": 4,
      "end": 14
    },
    "window_precision": 1.0,
    "window_recall": 0.5,
    "confusion_points": 4,
    "confusion_matrix": {
      "tp": 2,
      "fp": 0,
      "tn": 1,
      "fn": 2
    },
    "polls": 1,
    "poll_prediction_accuracy": 0.0,
    "poll_predictions": [
      {
        "at": 10,
        "pre_poll_ccs": 0.351,
        "predicted_miss": false,
        "poll_miss_rate": 0.75,
        "actual_majority_miss": true,
        "score_source": "previous_event"
      }
    ],
    "timeline": [
      {
        "at": 0,
        "event_type": "teacher",
        "score": 0.1,
        "ground_truth_confused": false
      },
      {
        "at": 4,
        "event_type": "chat",
        "score": 0.123,
        "ground_truth_confused": true
      },
      {
        "at": 7,
        "event_type": "chat",
        "score": 0.351,
        "ground_truth_confused": true
      },
      {
        "at": 10,
        "event_type": "poll",
        "score": 0.676,
        "ground_truth_confused": true
      },
      {
        "at": 14,
        "event_type": "chat",
        "score": 0.647,
        "ground_truth_confused": true
      }
    ]
  },
  {
    "fixture": "fractions-live",
    "title": "Comparing Fractions",
    "confusion_window": {
      "start": 4,
      "end": 13
    },
    "window_precision": 0.667,
    "window_recall": 0.5,
    "confusion_points": 4,
    "confusion_matrix": {
      "tp": 2,
      "fp": 1,
      "tn": 2,
      "fn": 2
    },
    "polls": 2,
    "poll_prediction_accuracy": 0.0,
    "poll_predictions": [
      {
        "at": 10,
        "pre_poll_ccs": 0.285,
        "predicted_miss": false,
        "poll_miss_rate": 0.75,
        "actual_majority_miss": true,
        "score_source": "previous_event"
      },
      {
        "at": 20,
        "pre_poll_ccs": 0.736,
        "predicted_miss": true,
        "poll_miss_rate": 0.0,
        "actual_majority_miss": false,
        "score_source": "previous_event"
      }
    ],
    "timeline": [
      {
        "at": 0,
        "event_type": "teacher",
        "score": 0.1,
        "ground_truth_confused": false
      },
      {
        "at": 4,
        "event_type": "chat",
        "score": 0.121,
        "ground_truth_confused": true
      },
      {
        "at": 7,
        "event_type": "chat",
        "score": 0.285,
        "ground_truth_confused": true
      },
      {
        "at": 10,
        "event_type": "poll",
        "score": 0.606,
        "ground_truth_confused": true
      },
      {
        "at": 13,
        "event_type": "chat",
        "score": 0.736,
        "ground_truth_confused": true
      },
      {
        "at": 17,
        "event_type": "teacher",
        "score": 0.736,
        "ground_truth_confused": false
      },
      {
        "at": 20,
        "event_type": "poll",
        "score": 0.587,
        "ground_truth_confused": false
      }
    ]
  },
  {
    "fixture": "photosynthesis-live",
    "title": "Where Plant Mass Comes From",
    "confusion_window": {
      "start": 4,
      "end": 14
    },
    "window_precision": 1.0,
    "window_recall": 0.5,
    "confusion_points": 4,
    "confusion_matrix": {
      "tp": 2,
      "fp": 0,
      "tn": 1,
      "fn": 2
    },
    "polls": 1,
    "poll_prediction_accuracy": 0.0,
    "poll_predictions": [
      {
        "at": 10,
        "pre_poll_ccs": 0.288,
        "predicted_miss": false,
        "poll_miss_rate": 0.75,
        "actual_majority_miss": true,
        "score_source": "previous_event"
      }
    ],
    "timeline": [
      {
        "at": 0,
        "event_type": "teacher",
        "score": 0.1,
        "ground_truth_confused": false
      },
      {
        "at": 4,
        "event_type": "chat",
        "score": 0.112,
        "ground_truth_confused": true
      },
      {
        "at": 7,
        "event_type": "chat",
        "score": 0.288,
        "ground_truth_confused": true
      },
      {
        "at": 10,
        "event_type": "poll",
        "score": 0.609,
        "ground_truth_confused": true
      },
      {
        "at": 14,
        "event_type": "chat",
        "score": 0.639,
        "ground_truth_confused": true
      }
    ]
  }
]
```
