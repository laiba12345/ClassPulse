# Codex Task Briefs — paste these in order, one per session/task

Do these in order. Each one should end with passing tests and a commit
before you start the next. Read AGENTS.md first if Codex hasn't already.

---

## Task 1 — Project scaffold + simulated live transcript stream

**Goal:** Set up the repo skeleton and a simulated live transcript feed
that plays back a pre-scripted class as if it's happening in real time.

**Context:** No real audio/speech-to-text — this is a scripted transcript
(teacher lines + student chat lines + timestamps + occasional poll
results) replayed on a timer to simulate a live stream. This is the input
every other component consumes.

**Constraints:**
- Python/FastAPI backend per AGENTS.md
- Write 2-3 sample scripted "classes" as JSON fixtures, each with at
  least one deliberate confusion moment (a concept where several student
  lines show confusion) so later components have something real to detect
- Expose the stream over a simple endpoint (WebSocket or SSE) that other
  components can subscribe to

**Definition of done:**
- Running the service replays a scripted class line-by-line with realistic
  timing
- At least one test confirms the stream emits lines in correct order with
  correct timestamps

---

## Task 2 — CCS (Confusion Confidence Score) engine

**Goal:** Build the live confusion-scoring engine described in
ClassPulse_Project_Document.md §4.1.

**Context:** For each transcript window, compute a CCS score from:
sentiment (via GPT-5.6, Structured Outputs), keyword flags (simple rule
list), response latency (from timestamps), and poll-miss rate. Combine
with a weighted sum through a sigmoid, per the formula in §4.1.

**Constraints:**
- Sentiment classification is one Structured Outputs call per transcript
  line: `{"sentiment": "confused"|"neutral"|"positive", "confidence": 0-1}`
- Keyword flagging and latency/poll-miss math are plain code, no LLM
- Fusion formula and weights are plain code — hardcode reasonable initial
  weights, they don't need to be ML-trained for the demo
- Write the test first: e.g. "given a window with 3 confused-sentiment
  lines and 2 poll misses, CCS should be above 0.6"; "given a calm window
  with no confusion signals, CCS should be below 0.3"

**Definition of done:**
- CCS score computed and printed/logged live as the Task 1 stream plays
- Tests for at least: a clearly-confused window, a clearly-calm window,
  and the sigmoid bounds (never outputs outside [0,1])

---

## Task 3 — BKT (Bayesian Knowledge Tracing) engine

**Goal:** Build the per-student, per-concept mastery tracker from §4.2.

**Context:** Standard BKT update rules (given in §4.2) plus the CCS-as-
soft-evidence extension. Pure deterministic code — no LLM involved here.

**Constraints:**
- Implement `update_mastery(student_id, concept, correct: bool | None,
  ccs: float | None)` — either correctness evidence, CCS evidence, or both
  can be passed for a given update
- Explicit evidence (correct/incorrect) should move the estimate more than
  CCS soft evidence, per the λ weighting described in §4.2

**Definition of done (write these tests first):**
- Given 10 correct answers on a concept, mastery increases
- Given a repeated pattern of incorrect answers, mastery decreases and
  stays low
- Given sustained high CCS with no graded evidence yet, mastery estimate
  dips modestly (not as much as an explicit wrong answer would move it)
- All tests pass before moving to Task 4

---

## Task 4 — Live nudge generation

**Goal:** When CCS crosses a threshold for a concept, generate a short,
concrete re-explanation suggestion for the teacher.

**Context:** Uses GPT-5.6 with Structured Outputs. Should reference which
concept triggered it and why (cite the actual signals — e.g. "3 students
showed confusion language and 2 missed the poll question").

**Constraints:**
- Output schema: `{"concept": str, "trigger_reason": str, "suggested_
  reframing": str}`
- Trigger only once per confusion spike, not repeatedly every window
  while CCS stays high (avoid spamming the teacher)

**Definition of done:**
- A test simulating a CCS spike produces exactly one nudge with a
  non-generic, concept-specific suggestion
- A test simulating calm CCS produces no nudge

---

## Task 5 — Dashboard UI (this is the "coherent product experience" piece)

**Goal:** One screen tying everything together live: transcript feed, CCS
indicator, nudge alerts, per-student mastery table.

**Context:** This is what gets demoed — it needs to
look and feel like a real product, not a debug console. Keep it simple but
polished: a clean layout, a visible confusion-score gauge or line chart, a
clearly visible alert when a nudge fires, and a live-updating table of
student mastery per concept.

**Constraints:**
- Plain HTML/JS or minimal React, per AGENTS.md
- Connects to the backend stream from Task 1-4 and updates live, no manual
  refresh
- Should be presentable on camera for the demo video with zero setup
  beyond the one-command launch

**Definition of done:**
- `./run_demo.sh` (or equivalent) starts backend + frontend + the
  simulated class, and the dashboard updates live end-to-end with no
  manual steps
- Looks intentional, not like a debug page

---

## Stretch tasks (only if Tasks 1-5 are done and fully working with time left)

- §4.2b Independent Outcome Verification: one follow-up check question,
  graded separately from CCS, feeding a real evidence point into BKT
- Teacher Memory Agent (§4.3): persisted style-tag stats across multiple
  scripted classes, not just the current session

Do not start these until the core 5 tasks are solid — a fully working
core loop beats a partially working full system for judging.
