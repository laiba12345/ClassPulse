# ClassPulse evaluation

## Automated coverage of behavior

The Python test suite covers:

- three fixture files, ordered timestamps, and poll confusion moments;
- clearly confused and clearly calm CCS windows;
- CCS range guarantees;
- ten correct BKT updates, repeated incorrect updates, soft CCS evidence, and combined evidence;
- GPT‑5.6 model selection and strict sentiment/nudge JSON schemas;
- exactly one concept-specific nudge per spike and no calm nudge;
- complete runtime production of transcript, CCS, mastery, and nudge messages;
- FastAPI health/catalog endpoints, SSE delivery, static dashboard delivery;
- presence of the live transcript, CCS gauge, nudge panel, mastery table, and EventSource client.

Latest implementation checkpoint after real-data integration: **22 passed, 0 failed** in 0.88 seconds. Five deprecation warnings originate inside FastAPI under Python 3.14; no ClassPulse warning or failure was emitted.

## Real-data validation

Official TalkMoves public test splits were loaded from the SumnerLab release:

| Measure | Result |
|---|---:|
| Total annotated utterance pairs | 30,401 |
| Teacher pairs | 23,250 |
| Teacher non-empty responses | 23,208 |
| Student pairs | 7,151 |
| Student non-empty responses | 6,994 |
| Teacher annotation categories | 7 |
| Student annotation categories | 5 |
| Schema errors | 0 |

This validates operation on real classroom language and authentic discourse annotations. TalkMoves has no confusion, latency, poll, or mastery labels, so it is not reported as a CCS accuracy benchmark.

## Authored-fixture CCS backtest

The production CCS path was replayed against explicit confusion windows in all three scripted fixtures:

- Aggregate precision: **0.857**
- Aggregate recall: **0.500**
- Confusion matrix: TP 6, FP 1, TN 4, FN 6
- Pre-poll majority-miss prediction: **0/4**

The pre-poll calculation uses the score from the prior event, so the poll result cannot leak into its own prediction. These results show late/reactive detection rather than reliable early warning. No post-hoc weight tuning was performed. Full timelines are in [validation/CCS_BACKTEST.md](./validation/CCS_BACKTEST.md).

## Real-server smoke test

Uvicorn was launched on a real localhost socket and verified independently of FastAPI’s in-process test client:

- `GET /api/health`: 200, `status=ok`
- `GET /`: 200
- `GET /static/styles.css`: 200
- `GET /api/stream/fractions-live?speed=10000`: 200
- SSE contained `event`, `ccs`, `mastery`, `nudge`, and `complete` message types
- Provider was honestly reported as `deterministic-demo-fallback` because no API credential was supplied

## Interpretation boundaries

This evaluates functional correctness and deterministic math on known scripted scenarios. It does not establish classroom efficacy, fairness, sentiment-model accuracy, or mastery calibration. A pilot should add educator-labeled transcript windows, CCS calibration curves, nudge usefulness ratings, and BKT predictive log loss.
