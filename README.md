# SDx Evaluation Agent

An MVP evaluation agent for the SDx development flow.
It reads engineer–agent traces from LangFuse, extracts evidence of
agent quality across three signal classes, and writes a markdown
learnings report. Reports are designed to be ingested by the SDx
knowledge layer alongside requirements, specs, and FDA/ASPICE
documents.

> Demo target: F2F update on **2026-05-21**.

---

## What this repo contains

```
eval-agent/
├── .opencode/
│   ├── agent/evaluator.md                            # primary opencode agent
│   └── skills/langfuse-trace-analysis/SKILL.md       # on-demand skill
├── scripts/
│   ├── load_traces.py                                # LangFuse CSV → packet
│   └── generate_synthetic_traces.py                  # deterministic toy data
├── data/
│   └── synthetic-traces.csv                          # 1 session, 8 turns
├── eval-reports/
│   └── ses_synthetic_camera_obj_det_001_…_learnings.md   # worked example
├── docs/
│   ├── SYSTEM-EXPLAINED.md                           # plain-language docs
│   ├── slides.md                                     # Marp source
│   ├── slides.html                                   # rendered deck
│   └── slides.pdf                                    # exported deck
├── opencode.json                                     # agent registration
└── ACTION_LOG.md                                     # decisions + progress
```

---

## How it works (one diagram)

```
                      I · Capture
                      ─────────────────
                      Engineer → SDX → LangFuse → trace export (.csv)

                      II · Evaluate
                      ─────────────────
                      load_traces.py → trace packet (.json)
                                       │
                                       ▼
                          evaluator agent ← trace-analysis skill
                                       │
                                       ▼
                                       learnings report (.md)

                      III · Improve
                      ─────────────────
                      team · prompts · agents · knowledge layer
```

The agent extracts three orthogonal signal classes from each session:

| Class | Method | What it captures |
|---|---|---|
| **Structural** | count over turns | tool-call mix, finish reasons, tokens, system-prompt churn |
| **Qualitative** | model judgement, cited per turn | did the agent answer the request; did the plan match the ask |
| **Implicit** | pattern-match the six-item catalogue | user correction, retry, abandoned trajectory, follow-up edit, context bloat, tool failure echo |

The implicit class follows the approach presented at the CMU FLAME event by the OpenHands team.

---

## Quick start

### 1 · Run the agent in opencode

```bash
git clone https://github.com/ryanlingo/eval-agent.git
cd eval-agent
opencode
# press Tab, pick `evaluator`, then ask:
# "Evaluate session ses_synthetic_camera_obj_det_001 in data/synthetic-traces.csv"
```

The agent loads the `langfuse-trace-analysis` skill, reads the trace
packet, applies the three extractors, and writes a report to
`eval-reports/<session_id>_<UTC_TIMESTAMP>_learnings.md`.

### 2 · Run the loader directly (no LLM)

```bash
# List sessions in a CSV
python scripts/load_traces.py --csv data/synthetic-traces.csv --list

# Build a packet for one session
python scripts/load_traces.py --csv data/synthetic-traces.csv \
  --session ses_synthetic_camera_obj_det_001 > /tmp/packet.json
```

### 3 · Regenerate the toy dataset

```bash
python scripts/generate_synthetic_traces.py --out data/synthetic-traces.csv
```

The synthetic session is deliberately designed to surface three signals:
a **user correction** (`tr_0004`), a **tool failure echo** (`tr_0006`),
and a **retry** (`tr_0005` → `tr_0006`).

### 4 · Render or update the slide deck

```bash
npx --yes @marp-team/marp-cli docs/slides.md -o docs/slides.html
npx --yes @marp-team/marp-cli docs/slides.md --pdf --allow-local-files \
  -o docs/slides.pdf
```

---

## Report file naming

```
eval-reports/<session_id>_<YYYYMMDDTHHMMSSZ>_learnings.md
```

Examples for the same session over time sort together in a directory
listing. UTC timestamps are second-precision so re-evaluations of the
same session never overwrite older reports.

---

## Documentation

- **`docs/SYSTEM-EXPLAINED.md`** — plain-language description of every
  component, the data flow, file naming conventions, and a glossary.
  Sentences are deliberately short; written with non-native English
  readers in mind.
- **`docs/slides.pdf`** — nine-slide deck for the F2F. Title · Problem ·
  Method · Architecture · Components · Demonstration · Sample report ·
  Integration · Roadmap.
- **`ACTION_LOG.md`** — append-only log of decisions, scope changes,
  and progress. Read this first if you're picking up the project mid-stream.

---

## Scope and limitations

This is an MVP. It is **not**:

- a benchmark — no numeric scores;
- a real-time monitor — runs on past traces only;
- a cross-session aggregator — one report per session;
- a replacement for FDA or ASPICE reports — it is a new artifact that
  lives next to them in the knowledge layer.

The worked example uses a synthetic toy session generated from
`scripts/generate_synthetic_traces.py`. Validation against real
sessions is part of the roadmap on the final slide.

---

## Roadmap

**Before the demo (this iteration):**
- Replace the CSV-export step with the LangFuse scoring/cost API.
- Run the agent against three real sessions to estimate signal recall.
- Cite reports from the eval-reports corpus inside one downstream agent run.

**Beyond MVP:**
- Cross-session rollups to detect agent-level regressions.
- Implement implicit-signal detectors as deterministic Python; reserve
  the LLM for qualitative judgement.
- Convert recommendations into prompt/skill diffs the team can review.
- Trial Laminar against LangFuse on the same sessions.
