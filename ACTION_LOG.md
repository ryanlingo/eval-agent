# Action log — SDx evaluation agent MVP

Append-only log so any future session (Claude or human) can pick up where we left off. Newest entries at the bottom.

---

## Goal

Build an MVP **evaluation agent** for the SDx flow, demonstrable on **2026-05-21**.

It is one of three deliverables:

1. **Eval flow** (executable): reads LangFuse trace data → analyzes → writes a learnings markdown report. Lives in `.opencode/`, `scripts/`, `eval-reports/`.
2. **System documentation** (static): `docs/SYSTEM-EXPLAINED.md`. Plain language for non-native English readers.
3. **Slide deck** (static): `docs/slides.md` rendered with Marp. Minimalist, color used only for meaning, simple language for Japanese audience.

Items 2 and 3 describe item 1 — they are not part of its runtime.

The repo contains **no real user names**. All worked examples use a synthetic dataset built by `scripts/generate_synthetic_traces.py`.

---

## Decisions

| Decision | Choice | Why |
|---|---|---|
| Slide deck format | **Markdown + Marp** | Plain text in repo; renders to PDF/HTML/PPTX; easy to diff. |
| Data source for MVP | **CSV file** (LangFuse export format) | Zero infra, deterministic, demo-safe. Live LangFuse API can come in v2. |
| Worked example | **Synthetic toy dataset** at `data/synthetic-traces.csv` | Demonstrates the format and signals end-to-end without exposing real users. |
| Flow shape | **One agent + one skill** | `.opencode/agent/evaluator.md` orchestrates; `.opencode/skills/langfuse-trace-analysis/SKILL.md` holds reusable schema knowledge, loaded on-demand. Matches opencode conventions. |
| Report content | **Structural + qualitative + FLAME-style implicit signals** | Aligns with the team's research direction. Structural signals are easy to compute; implicit signals are detected from message patterns; qualitative learnings are LLM-generated. |

---

## Trace data shape (LangFuse export format)

The LangFuse export has 15 columns. Two trace `name` values matter:

- **`ai.streamText`** = opencode-side traces with full content (system prompt, messages, tool_calls, finish_reason, headers `User-Agent: opencode/1.4.0`, session affinity). **These are the rows the eval agent uses.**
- `llm_request` = vLLM OpenTelemetry telemetry only (latency/token counts, no content). Useful for cost rollups, not for learnings.

The eval flow filters to `name == 'ai.streamText'` and groups by `sessionId` to build a per-session "trace packet."

The synthetic dataset (`data/synthetic-traces.csv`, 8 rows, 1 session) follows the same schema so the loader handles it identically to real exports.

---

## Plan (tasks 1-15)

1. ✅ Set up project skeleton and ACTION_LOG.md
2. ✅ Build `scripts/load_traces.py`
3. ✅ Validate loader on real-format CSV
4. ✅ Write `.opencode/skills/langfuse-trace-analysis/SKILL.md`
5. ✅ Write `.opencode/agent/evaluator.md`
6. ✅ Wire up `opencode.json`
7. ✅ Produce a sample report by hand-running the flow
8. ✅ Write `docs/SYSTEM-EXPLAINED.md`
9. ✅ Write `docs/slides.md` (Marp deck)
10. ✅ Final pass: update ACTION_LOG and tell user how to run
11. ✅ Build `scripts/generate_synthetic_traces.py`
12. ✅ Replace sample report with one from synthetic data
13. ✅ Scrub people's names from all repo files
14. ✅ Update slides + system doc to use synthetic toy case
15. ✅ Update ACTION_LOG with refactor entry (this entry)

---

## Log entries

### 2026-05-09 — kickoff
- Read all three input files (SDX Ideas md, the source pptx, sampled the LangFuse CSV).
- Confirmed opencode conventions via opencode.ai/docs (agents/, skills/, tools/).
- Confirmed four scoping decisions (logged in the Decisions table above).
- Created task list and this action log.
- Repo skeleton created: `.opencode/agent/`, `.opencode/skills/langfuse-trace-analysis/`, `scripts/`, `docs/`, `eval-reports/`.

### 2026-05-09 — loader built and validated
- Wrote `scripts/load_traces.py`. Three modes: `--list`, `--session`, `--out-dir`.
- Confirmed `csv.field_size_limit(sys.maxsize)` handles 100+ MB rows.
- Filter is `name == 'ai.streamText'` (configurable via `--name`).
- Built and inspected a packet from a real-format export to confirm the JSON shape: ~70 KB for a typical 22-turn session, including system prompts deduplicated by hash, normalized turns, and rolled-up token totals.

### 2026-05-09 — agent + skill + config
- Wrote skill at `.opencode/skills/langfuse-trace-analysis/SKILL.md`. Defines
  trace shape, six implicit-signal detectors (user correction, retry,
  abandoned trajectory, follow-up edit, context bloat, tool failure echo),
  and the report layout.
- Wrote agent at `.opencode/agent/evaluator.md`. Mode: primary. Loads the
  skill on every run as the source of truth.
- Wrote `opencode.json` registering the agent and pre-allowing the
  `langfuse-trace-analysis` skill.

### 2026-05-09 — initial documentation and slides
- Wrote `docs/SYSTEM-EXPLAINED.md`. Plain-language, short sentences for
  non-native English readers. Numbered sections + glossary.
- Wrote `docs/slides.md`. Marp deck. Color reserved for meaning:
  blue=system, amber=data, red=problem, black=text. Minimalist; no
  decorative imagery.

### 2026-05-09 — synthetic dataset refactor
- Per request: removed all real user names from the repo, and built a
  synthetic toy dataset to anchor the worked examples.
- Wrote `scripts/generate_synthetic_traces.py`. Emits one session in
  LangFuse export format (`data/synthetic-traces.csv`, 8 rows). Trace IDs
  are deterministic (`tr_0001_codegraph` … `tr_0008_done`) so docs can
  cite them.
- The toy task: *"Add YOLO object detection to the rear camera module."*
  Designed to surface three signals: a user correction
  (`tr_0004_correction`), a tool failure echo (`tr_0006_write2_retry`,
  the assistant text echoes "permission denied"), and a retry
  (`tr_0005_write1` → `tr_0006_write2_retry`, same `write` call repeated
  with identical inputs).
- Deleted the prior real-data sample report. Wrote a new one against the
  synthetic packet at
  `eval-reports/ses_synthetic_camera_obj_det_001_20260509T140500Z_learnings.md`.
- Scrubbed names from `docs/SYSTEM-EXPLAINED.md`, `docs/slides.md`,
  `.opencode/agent/evaluator.md`, `.opencode/skills/...SKILL.md`. The
  `SDX Ideas related to evaluation.md` file is the team's input
  document and is left unchanged.

### How to use what we built

1. **Run the eval flow live (in opencode):**
   ```bash
   cd <repo>
   opencode
   # press Tab, pick `evaluator`, then say:
   # "Evaluate session ses_synthetic_camera_obj_det_001
   #  in data/synthetic-traces.csv"
   ```

2. **Regenerate the toy dataset:**
   ```bash
   python3 scripts/generate_synthetic_traces.py --out data/synthetic-traces.csv
   ```

3. **Run the loader directly (no LLM, just data prep):**
   ```bash
   python3 scripts/load_traces.py --csv data/synthetic-traces.csv --list
   python3 scripts/load_traces.py --csv data/synthetic-traces.csv \
     --session ses_synthetic_camera_obj_det_001 > /tmp/packet.json
   ```

4. **Preview the slide deck:**
   ```bash
   npx @marp-team/marp-cli docs/slides.md -o docs/slides.html
   npx @marp-team/marp-cli docs/slides.md -o docs/slides.pdf
   npx @marp-team/marp-cli --watch docs/slides.md          # live preview
   npx @marp-team/marp-cli docs/slides.md --pptx -o docs/slides.pptx   # PowerPoint export
   ```

### Open questions for the team / next session
- LangFuse export size: the SDX Ideas doc flags this. The team has
  suggested using LangFuse's built-in scoring/cost API instead of
  dumping raw JSON. Worth a 30-min spike before 5/21 to see if a
  smaller endpoint makes the loader unnecessary.
- Should the loader also process `llm_request` rows for cost/latency
  rollups in a future report variant? (Currently ignored.)
- Cross-session trend reports (mentioned as v2) — we have the
  per-session packets; rolling them up is one more script, not a new
  system.

### 2026-05-09 — input materials moved out of the repo
- The three input materials (real LangFuse CSV export, the source pptx,
  and the team alignment markdown) all contained real names. Per request,
  they were moved out of the repo to a sibling folder:
  `../eval-agent-inputs/` (i.e. `/Users/ryan/Desktop/eval-agent-inputs/`).
- The repo is now fully name-free. Confirmed via grep across all files.
- The synthetic dataset (`data/synthetic-traces.csv`) and the worked
  example report (`eval-reports/ses_synthetic_camera_obj_det_001_20260509T140500Z_learnings.md`)
  are now the canonical demo materials. They cover the full flow
  end-to-end without referencing the original inputs.

### 2026-05-09 — clearer flow diagram
- Replaced the lightweight text flow on the slides' "The flow" slide with
  a vertical pipeline diagram drawn in HTML/CSS. Three stages stacked
  (Capture / Evaluate / Improve), boxes are color-coded by meaning
  (blue = system, amber = data, gray = actor).
- Added matching ASCII and Mermaid diagrams to
  `docs/SYSTEM-EXPLAINED.md` section 3, plus a stage-summary table.
- Mermaid block uses the same color classes so the rendered diagram
  matches the slides when viewed on GitHub or in any Mermaid-aware
  Markdown viewer.

### 2026-05-09 — report filenames now include UTC timestamp
- Convention is now
  `eval-reports/<session_id>_<YYYYMMDDTHHMMSSZ>_learnings.md`.
- Re-evaluating the same session no longer overwrites prior reports;
  each run gets a unique, sortable file name.
- The `_learnings.md` suffix makes the file's purpose obvious in a
  directory listing.
- Updated: `.opencode/agent/evaluator.md`,
  `.opencode/skills/langfuse-trace-analysis/SKILL.md`,
  `docs/SYSTEM-EXPLAINED.md`, `docs/slides.md`, ACTION_LOG references.
- Renamed the existing sample report to follow the new convention.

### 2026-05-09 — slides rewritten for high-stakes presentation
- Replaced the tutorial-style deck with a 7-slide academic-register
  presentation: Title · Problem · Method · Architecture · Demonstration ·
  Integration · Roadmap.
- Each slide carries an italicized thesis line, a numbered section
  label, and a Helvetica running header / footer for institutional feel.
  Body type changed to a serif (Garamond/Georgia) for academic register;
  labels and code stay sans-serif for hierarchy.
- Method slide defines the three signal classes (structural,
  qualitative, implicit / FLAME-style) with explicit method tags.
- Demonstration slide reports the toy-session findings as an evidence
  table (signal · trace ID · type) and includes a "Limitation" call-out
  pointing to real-session validation in the roadmap.
- Added an Integration slide: file-name convention; closed loop showing
  reports → eval-reports corpus → knowledge-layer vector index → future
  agent context. Establishes that the evaluator's output is itself a
  knowledge artifact ingested by the same machinery as requirements,
  specs, and FDA/ASPICE documents.
- Added a Roadmap slide split into "before the demo" and "beyond MVP".
- Color meaning preserved (system / data / problem / mute). Color is
  used only for those four classes; everything else is black on white.

### Resume instructions for a future session
- Read this file top-to-bottom; everything's here.
- All deliverables are in this directory tree.
- The synthetic dataset and worked example let you run the flow without
  any external data. opencode 1.4.0 is the only external dependency.
- Original input materials (CSV, pptx, alignment doc) live at
  `../eval-agent-inputs/` if needed for reference.
