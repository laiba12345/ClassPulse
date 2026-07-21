# Nalmai

Nalmai is a real-time teaching copilot for online lessons. It transcribes a
teacher and student, detects confusion or explanation risk, suggests a better
teaching move, checks whether the teacher used it, generates a learning check,
and tracks the student's concept mastery over time.

## Core features

- Two-person browser video call with microphone and camera controls
- Separate teacher and student audio transcription in 10-second windows
- Live student Confusion Confidence Score (CCS)
- Teacher factual- and clarity-risk analysis
- GPT-5.6 teaching suggestions and automatic three-option polls
- Verification of suggestion implementation from later teacher speech
- Per-student, per-concept Bayesian Knowledge Tracing (BKT)
- SQLite progress persistence under stable pseudonymous IDs
- Teacher Memory Agent for concept-specific, history-informed suggestions
- Scripted presentation mode and real classroom-language validation

## How it works

```text
Teacher and student WebRTC audio
              |
              v
gpt-4o-transcribe-diarize
              |
       speaker-specific text
        /                 \
student learning state   teacher explanation risk
        |                 /
        v                v
 deterministic CCS -> GPT-5.6 teaching suggestion
                              |
                    automatic baseline poll
                              |
                 later teacher transcript
                              |
              implementation verification
                              |
                     follow-up poll
                              |
             BKT mastery + SQLite memory
```

GPT-5.6 handles language classification, explanation-risk analysis, teaching
suggestions, poll creation, implementation verification, and memory insights.
CCS, BKT, thresholds, grading, and outcome calculations are deterministic
Python code. OpenAI calls use strict Structured Outputs.

## Run locally

Install dependencies:

```powershell
py -m pip install -r requirements.txt
```

Create `.env` and add your API key:

```env
OPENAI_API_KEY=your-key
NALMAI_LLM_MODE=auto
```

Start everything on Windows:

```powershell
.\run_demo.ps1
```

On macOS or Linux:

```sh
./run_demo.sh
```

Open `http://127.0.0.1:8000`. The two-person lesson is at `/call`. Without an
API key, scripted lessons use a visibly labelled deterministic fallback; live
audio transcription requires the key.

## Live lesson flow

1. Open `/call` in two browsers.
2. The teacher creates a room and shares its six-character code.
3. The student joins with a stable pseudonymous ID.
4. The teacher starts analysis after both video streams appear.
5. Nalmai uploads separate teacher and student audio tracks every 10 seconds.
6. Suggestions, polls, mastery, implementation evidence, and memory insights
   appear on the teacher screen while the student sees only student controls.

Use HTTPS when joining from separate physical devices; browsers normally block
camera and microphone access on non-localhost HTTP pages.

## Project structure

```text
app/          FastAPI API, runtime, CCS, BKT, OpenAI, memory, and call logic
public/       Dashboard and two-person call UI
data/         Demo fixtures, validation scenarios, and licensed TalkMoves data
scripts/      Reproducible evaluation and import utilities
tests/        Unit, integration, API, persistence, and UI-contract tests
validation/   Evaluation reports and documented evidence boundaries
```

The dashboard receives live events through Server-Sent Events. WebRTC signaling
uses a FastAPI WebSocket, while participant media remains peer-to-peer.

## Data and evaluation

The reliable presentation mode uses authored transcript fixtures with known
confusion points. The repository also includes the public TalkMoves test splits:
30,401 anonymized K-12 mathematics utterance pairs under CC BY-NC-SA 4.0.
TalkMoves validates classroom-language ingestion, not CCS accuracy, because it
does not contain confusion or mastery labels.

The current suite contains **113 tests**:

```powershell
py -m pytest -q
```

Detailed CCS metrics, outcome-linkage experiments, educator-rating workflow,
real-data results, and limitations are in [EVALUATION.md](./EVALUATION.md) and
[`validation/`](./validation/). The presentation script is in
[DEMO.md](./DEMO.md).

## Persistence and privacy

SQLite stores pseudonymous profiles, concept mastery, and observed teaching
outcomes in `data/nalmai.db`. The Teacher Memory Agent retrieves only the
current concept's relevant student and teacher history; GPT-5.6 does not receive
unrestricted database access.

## How I collaborated with Codex

I used Codex throughout the build as an engineering and evaluation partner. I
defined Nalmai's purpose and core functionalities beforehand, then kept adding
new task briefs as the requirements increased and the live experience revealed
new needs. I selected the name, reviewed each result, and made the final product,
scope, privacy, and evidence decisions.

Representative prompts and task briefs included:

> “Build the project end to end and test every aspect of it.”

> “Add real data to the project for greater impact and validation.”

> “Allow two people to join a live call and show suggestions to the teacher.”

> “Apply language evidence only to the student who produced it; use class-wide
> CCS for nudges, not individual mastery.”

Codex implemented the FastAPI runtime, dashboard, WebRTC call, OpenAI adapters,
CCS and BKT engines, SQLite persistence, Teacher Memory Agent, and automated
tests. It also helped diagnose speaker-attribution errors,
transcription parsing, inaccessible scrolling, diluted one-student CCS, and the
missing connection between explanation risk and teaching suggestions.

I required deterministic CCS/BKT math, strict JSON schemas for model calls,
separate task commits, honest fallback labels, and clear separation between
authored validation and real-world evidence. I rejected class-wide mastery
penalties and claims that authored outcome improvements prove causality. The
full staged history is available in [TASK_BRIEFS.md](./TASK_BRIEFS.md).

Codex helped construct the 113-test suite and the CCS, TalkMoves, outcome, and
educator-evaluation workflows. I reviewed the reported limitations rather than
treating passing tests as evidence of classroom efficacy.

### Required Codex feedback reference

```text
019f6582-86b0-7f50-8b6a-9c00b666eff6
```

## License

Nalmai code is available under the [MIT License](./LICENSE). Bundled TalkMoves
data remains separately licensed under CC BY-NC-SA 4.0; see
[`data/real/talkmoves/DATASET.md`](./data/real/talkmoves/DATASET.md).
