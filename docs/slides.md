---
marp: true
theme: default
paginate: true
size: 16:9
header: 'SDx Evaluation Agent'
style: |
  /* Minimalist academic style. Color reserved for meaning.
     --c-system  blue   = system component (agent, skill, script, opencode)
     --c-data    amber  = data (logs, packet, report, corpus)
     --c-warn    red    = problem framing
     --c-mute    gray   = supporting/secondary
     all other text     = black on white                                */
  :root {
    --c-system: #1f5fbf;
    --c-data:   #c98a04;
    --c-warn:   #b03a2e;
    --c-mute:   #6b6b6b;
  }
  section {
    font-family: 'EB Garamond', 'Georgia', 'Hiragino Mincho ProN', serif;
    background: #ffffff;
    color: #111111;
    padding: 48px 72px 48px;
    line-height: 1.45;
  }
  header {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 12px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--c-mute);
  }
  footer {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 12px; color: var(--c-mute);
  }
  section::after { color: var(--c-mute); font-size: 12px; }   /* page number */

  h1 { font-weight: 600; font-size: 40px; margin: 0 0 8px; letter-spacing: -0.01em; }
  h2 { font-weight: 600; font-size: 28px; margin: 0 0 12px; letter-spacing: -0.01em; }
  h3 { font-weight: 600; font-size: 18px; margin: 14px 0 4px; }
  p, li { font-size: 19px; line-height: 1.5; }
  small { color: var(--c-mute); font-size: 14px; }
  strong { font-weight: 600; }

  /* Meaning-color text spans */
  .system { color: var(--c-system); font-weight: 600; }
  .data   { color: var(--c-data);   font-weight: 600; }
  .warn   { color: var(--c-warn);   font-weight: 600; }
  .mute   { color: var(--c-mute); }

  /* Section labels and thesis lines */
  .section-label {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 11px; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--c-mute); margin-bottom: 6px;
  }
  .thesis {
    font-style: italic; color: #222; font-size: 20px;
    border-left: 3px solid var(--c-mute); padding-left: 14px; margin: 8px 0 18px;
  }
  .defn { margin: 4px 0; }
  .defn .term { font-weight: 600; }

  /* Two-column layout */
  .cols { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }

  /* ---- Signal-class card (Method slide) ---- */
  .signal {
    border-top: 2px solid #222;
    padding-top: 8px;
    margin-bottom: 14px;
  }
  .signal .class-name {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 22px; font-weight: 700;
    color: #111; letter-spacing: 0.01em;
    margin: 0 0 8px 0;
    display: flex; align-items: baseline; gap: 10px;
  }
  .signal .class-num {
    font-size: 14px; color: var(--c-mute); font-weight: 500;
    letter-spacing: 0.1em;
  }
  .signal .class-tag {
    font-size: 11px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 500;
  }
  /* Class 3 is rendered identically to classes 1 and 2 — it is one of three
     signal types we use, not a novel contribution we are claiming. */

  .signal .field {
    display: grid;
    grid-template-columns: 100px 1fr;
    gap: 10px;
    margin: 3px 0;
    font-size: 16px;
    line-height: 1.4;
  }
  .signal .field-label {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 600;
    padding-top: 4px;
  }
  .signal .field-body { color: #111; }
  .signal .field-body em { color: #444; }

  .catalogue {
    display: flex; flex-wrap: wrap; gap: 4px 8px;
    font-family: 'Helvetica Neue', 'Arial', sans-serif; font-size: 14px;
  }
  .catalogue span {
    border: 1px solid var(--c-mute);
    border-radius: 999px;
    padding: 1px 10px;
    color: #222;
  }

  .conclusion {
    margin-top: 6px;
    font-style: italic;
    font-size: 17px;
    color: #333;
  }
  .conclusion .accent { color: var(--c-system); font-style: normal; font-weight: 600; }

  /* Pipeline diagram — sized to fit a 16:9 slide without overflow. */
  .pipeline {
    display: flex; flex-direction: column; align-items: center; gap: 1px;
    margin-top: 0;
  }
  .stage-label {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 11px; letter-spacing: 0.14em; color: var(--c-mute);
    text-transform: uppercase; margin: 4px 0 2px;
  }

  /* I/O divider: amber-coded rule + label. Used on the demonstration
     slide to separate INPUT (trace fed to the evaluator) from
     OUTPUT (report it produces). */
  .io-divider {
    display: flex; align-items: center; gap: 10px;
    width: 100%; margin: 6px 0 6px;
  }
  .io-divider::before {
    content: ''; width: 18px; height: 2px; background: var(--c-data);
  }
  .io-divider .label {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 11px; letter-spacing: 0.2em; text-transform: uppercase;
    color: var(--c-data); font-weight: 700; white-space: nowrap;
  }
  .io-divider::after {
    content: ''; flex: 1; height: 1px; background: var(--c-data); opacity: 0.4;
  }
  .demo-table {
    border-collapse: collapse; width: 100%; font-size: 14px;
    margin: 4px 0;
  }
  .demo-table th {
    text-align: left; font-family: 'Helvetica Neue', sans-serif;
    font-size: 10px; letter-spacing: 0.16em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 600;
    padding: 4px 8px 3px 0; border-bottom: 1px solid #ccc;
  }
  .demo-table td {
    padding: 3px 8px 3px 0; vertical-align: top;
    border-bottom: 1px dotted #e2e2e2;
  }
  .demo-table td:first-child { white-space: nowrap; color: var(--c-mute); font-family: 'SF Mono', monospace; font-size: 12px; }
  .demo-table .signal-name { font-weight: 600; color: #111; }
  .demo-table .signal-type { font-family: 'Helvetica Neue', sans-serif; font-size: 10px; letter-spacing: 0.14em; text-transform: uppercase; color: var(--c-mute); }

  /* Component card — used on the "Agent + Skill" slide. */
  .component {
    border-left: 3px solid var(--c-system);
    padding: 0 0 0 14px;
    margin: 2px 0;
  }
  .component .comp-name {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 18px; font-weight: 600; color: #111;
    margin: 0 0 2px;
  }
  .component .comp-path {
    font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 11px; color: var(--c-mute); margin: 0 0 6px;
  }
  .component .comp-role {
    font-size: 14px; margin: 4px 0 6px; color: #222; line-height: 1.4;
  }
  .component h4 {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 700;
    margin: 8px 0 3px;
  }
  .comp-list { margin: 0 0 0 18px; padding: 0; }
  .comp-list li { font-size: 13px; line-height: 1.45; margin: 2px 0; }
  .comp-list li::marker { color: var(--c-mute); }

  /* Three-method extractor grid — one row per signal class.
     Each row aligns method · class name · description in fixed columns.
     Cells must be direct children of .extractors with NO blank lines
     between them, otherwise Markdown wraps them in <p> and the grid
     layout breaks. */
  .extractors {
    display: grid;
    grid-template-columns: 56px 92px 1fr;
    column-gap: 12px;
    row-gap: 6px;
    align-items: baseline;
    margin: 6px 0;
    padding: 8px 12px;
    background: #f6f6f6;
    border-radius: 4px;
    font-size: 13px;
  }
  .extractors > .method {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 700;
  }
  .extractors > .class-name {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-weight: 600; color: #111; font-size: 13px;
  }
  .extractors > .how { color: #222; line-height: 1.45; }

  /* Report card — stylized as a document excerpt for the
     "Sample learning report" slide. All three signal classes shown. */
  .report-card {
    border: 1px solid #ccc; border-radius: 4px;
    background: #fbfbfa; padding: 14px 22px 16px;
    font-family: 'EB Garamond', 'Georgia', serif;
    font-size: 14px; line-height: 1.4;
    box-shadow: 0 1px 0 #f0f0f0;
  }
  .report-card .filename {
    display: block; font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 11px; color: var(--c-mute);
    margin-bottom: 8px; word-break: break-all;
  }
  .report-card h4 {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 10px; letter-spacing: 0.18em; text-transform: uppercase;
    color: var(--c-mute); font-weight: 700;
    margin: 9px 0 3px; padding-top: 6px;
    border-top: 1px solid #e2e2e2;
  }
  .report-card h4:first-of-type { border-top: none; padding-top: 0; margin-top: 0; }
  .report-card .meta {
    font-family: 'SF Mono', 'Menlo', monospace; font-size: 12px;
    color: #444; margin: 0 0 4px;
  }
  .report-card .summary { margin: 0 0 4px; font-size: 14px; color: #111; }
  .report-card ul, .report-card ol { margin: 1px 0 2px 18px; padding: 0; }
  .report-card li { font-size: 13px; line-height: 1.4; margin: 0; }
  .report-card .cite {
    font-family: 'SF Mono', 'Menlo', monospace; font-size: 11px;
    color: var(--c-mute);
  }

  /* Phase divider: centered horizontal rule with a roman numeral and
     phase name. Marks the three phases of the pipeline unambiguously. */
  .phase-divider {
    display: flex; align-items: center; gap: 10px;
    width: 100%; max-width: 660px;
    margin: 4px 0 2px;
  }
  .phase-divider::before, .phase-divider::after {
    content: ''; flex: 1; height: 1px; background: #888;
  }
  .phase-divider .roman {
    font-family: 'EB Garamond', 'Georgia', serif;
    font-size: 17px; font-weight: 600; font-style: italic;
    color: #111; line-height: 1;
  }
  .phase-divider .name {
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    font-size: 11px; letter-spacing: 0.22em; text-transform: uppercase;
    color: #222; font-weight: 600; white-space: nowrap; line-height: 1;
  }
  .box {
    border: 2px solid #444; border-radius: 5px;
    padding: 2px 14px; font-size: 14px; font-weight: 500;
    background: #fff; min-width: 260px; text-align: center;
    font-family: 'Helvetica Neue', 'Arial', sans-serif;
    line-height: 1.4;
  }
  .box.system { border-color: var(--c-system); color: var(--c-system); }
  .box.data   { border-color: var(--c-data);   color: var(--c-data);   }
  .box.actor  { border-color: #444; color: #111; background: #f6f6f6; }
  .arrow      { font-size: 12px; color: var(--c-mute); line-height: 0.9; margin: 0; }
  .row        { display: flex; align-items: center; gap: 10px; }
  .row .arrow.side { font-size: 16px; }

  /* Code-style spans */
  code {
    font-family: 'SF Mono', 'Menlo', monospace;
    font-size: 0.86em;
    background: #f3f3f3; padding: 1px 5px; border-radius: 3px;
  }

  hr { border: none; border-top: 1px solid #e0e0e0; margin: 18px 0; }

  /* Title slide */
  section.title { padding-top: 130px; text-align: left; }
  section.title h1 { font-size: 52px; margin-bottom: 14px; }
  section.title .thesis { border: none; padding: 0; font-size: 22px; max-width: 760px; }
  section.title header, section.title footer { display: none; }
---

<!-- _class: title -->
<!-- _paginate: false -->

# SDx Evaluation Agent

<div class="section-label">MVP · F2F update 2026-05-21</div>

<div class="thesis">
Reads engineer–agent traces and extracts evidence of agent quality
across three signal classes. Integrates the resulting learning
artifacts into the SDx knowledge layer for use in future runs.
</div>

<br>

<small>Color key &nbsp;·&nbsp; <span class="system">■ system</span> &nbsp; <span class="data">■ data</span> &nbsp; <span class="warn">■ problem</span></small>

---

<div class="section-label">1 · Problem</div>

## Why we need a measurement layer

<div class="thesis">
Without measurement, we cannot direct improvement.
Without scalable measurement, we cannot keep up with the
agent surface we are building.
</div>

The SDx flow runs many agents across many engineers.
We are building a systematic measurement layer so we can direct
that growing surface with confidence.

**Why explicit evaluation alone is insufficient:**

- Hand-labeled outcomes are slow to collect and biased toward visible failures.
- Numeric post-hoc ratings capture little of what went wrong mid-task.
- Both scale poorly with the number of agents and engineers.

The cost of *not* measuring grows with every agent we add.

---

<div class="section-label">2 · Method</div>

## Three orthogonal classes of signal

<div class="thesis">
A single session's trace yields three independent kinds of evidence about agent quality. We extract all three from the same data, in one pass.
</div>

<div class="cols">
<div>

<div class="signal">
<div class="class-name"><span class="class-num">1.</span> Structural</div>
<div class="field"><div class="field-label">Definition</div><div class="field-body">Deterministic counts over the trace.</div></div>
<div class="field"><div class="field-label">Examples</div><div class="field-body">Turn count, tool-call mix, finish-reason distribution, token usage, system-prompt churn.</div></div>
<div class="field"><div class="field-label">Method</div><div class="field-body"><em>Computed</em>.</div></div>
</div>

<div class="signal">
<div class="class-name"><span class="class-num">2.</span> Qualitative</div>
<div class="field"><div class="field-label">Definition</div><div class="field-body">Bounded judgement on intent and outcome.</div></div>
<div class="field"><div class="field-label">Examples</div><div class="field-body">Did the agent answer the request? Did the plan match the ask?</div></div>
<div class="field"><div class="field-label">Method</div><div class="field-body"><em>Model judgement, cited per turn</em>.</div></div>
</div>

</div>
<div>

<div class="signal">
<div class="class-name">
  <span class="class-num">3.</span> Implicit
  <span class="class-tag">CMU FLAME–OpenHands inspired</span>
</div>
<div class="field"><div class="field-label">Definition</div><div class="field-body">Pattern-matched user behavior in the message stream.</div></div>
<div class="field"><div class="field-label">Catalogue</div><div class="field-body"><div class="catalogue"><span>user correction</span><span>retry</span><span>abandoned trajectory</span><span>follow-up edit</span><span>context bloat</span><span>tool failure echo</span></div></div></div>
<div class="field"><div class="field-label">Method</div><div class="field-body"><em>Pattern-matched against turns; each instance evidenced by trace ID</em>.</div></div>
</div>

</div>
</div>

<p class="conclusion">Classes 1 and 2 are well-established practice. Class 3 follows the implicit-signal approach presented at CMU FLAME by the OpenHands team.</p>

---

<div class="section-label">3 · Architecture</div>

## The pipeline

<div class="pipeline">

<div class="phase-divider"><span class="roman">I</span><span class="name">Capture</span></div>
<div class="box actor">Engineer</div>
<div class="arrow">↓</div>
<div class="box system">SDX</div>
<div class="arrow">↓</div>
<div class="box data">LangFuse · trace storage</div>
<div class="arrow">↓</div>
<div class="box data">trace export (.csv)</div>

<div class="phase-divider"><span class="roman">II</span><span class="name">Evaluate</span></div>
<div class="box system">load_traces.py</div>
<div class="arrow">↓</div>
<div class="box data">trace packet (.json)</div>
<div class="arrow">↓</div>
<div class="row">
  <div class="box system">evaluator agent</div>
  <div class="arrow side">←</div>
  <div class="box system">trace-analysis skill</div>
</div>
<div class="arrow">↓</div>
<div class="box data">learnings report (.md)</div>

<div class="phase-divider"><span class="roman">III</span><span class="name">Improve</span></div>
<div class="box actor">team · prompts · agents · knowledge</div>

</div>

---

<div class="section-label">4 · Components</div>

## The evaluator agent and its skill

<div class="thesis">
Two opencode primitives. The agent orchestrates each run; the skill holds the trace schema and signal definitions. Separating them lets the rules evolve without touching the orchestration.
</div>

<div class="cols" style="gap: 32px;">

<div>
<div class="component">

<div class="comp-name">evaluator <span class="mute" style="font-weight: 400;">· primary agent</span></div>
<div class="comp-path">.opencode/agent/evaluator.md</div>

<p class="comp-role">A primary opencode agent. Orchestrates one session evaluation end-to-end. Permissions: <code>edit</code>, <code>bash</code> allowed; web access denied.</p>

<h4>Per-run workflow</h4>
<ol class="comp-list">
  <li>Load the skill.</li>
  <li>Build the trace packet via <code>load_traces.py</code> and read it.</li>
  <li>Apply three signal extractors — one row, one method:</li>
</ol>

<div class="extractors">
<div class="method">count</div><div class="class-name">Structural</div><div class="how">walk <code>turns</code>; tally tool calls, finish reasons, tokens.</div>
<div class="method">judge</div><div class="class-name">Qualitative</div><div class="how">read messages; form bounded observations, cited per trace.</div>
<div class="method">match</div><div class="class-name">Implicit</div><div class="how">match each turn against the six-item catalogue; cite evidence per trace.</div>
</div>

<ol class="comp-list" start="4">
  <li>Derive recommendations from the evidence above.</li>
  <li>Write the report to <code>eval-reports/&lt;id&gt;_&lt;ts&gt;_learnings.md</code>.</li>
</ol>

<h4>Guardrails</h4>
<ul class="comp-list">
  <li>One session per run.</li>
  <li>No numeric scores. No invented signals.</li>
  <li>Every claim cites a trace ID or timestamp.</li>
</ul>

</div>
</div>

<div>
<div class="component">

<div class="comp-name">langfuse-trace-analysis <span class="mute" style="font-weight: 400;">· skill</span></div>
<div class="comp-path">.opencode/skills/langfuse-trace-analysis/SKILL.md</div>

<p class="comp-role">An opencode agent skill. Loaded on demand via the <code>skill</code> tool. Single source of truth for what the agent should look at and what it should produce.</p>

<h4>Contents</h4>
<ul class="comp-list">
  <li>Trace schema — which rows carry real content.</li>
  <li>Definitions for the three signal classes.</li>
  <li>Implicit-signal catalogue — six patterns.</li>
  <li>The report layout the agent must follow.</li>
</ul>

<h4>Why separate from the agent</h4>
<ul class="comp-list">
  <li>Schema or signal rules can evolve without touching the agent prompt.</li>
  <li>Same skill can be reused by future evaluator variants.</li>
  <li>Loaded only when needed; keeps the agent's context small.</li>
</ul>

</div>
</div>

</div>

---

<div class="section-label">5 · Demonstration</div>

## Toy session — eight turns

<div class="thesis">
We feed the evaluator a synthetic eight-turn session and inspect the report it produces.
</div>

<div class="cols">

<div>

<div class="io-divider"><span class="label">Input · trace fed to evaluator</span></div>

<p style="font-size: 15px; margin: 0 0 4px;">Source: <code>data/synthetic-traces.csv</code></p>
<p style="font-size: 15px; margin: 0 0 6px;">Engineer's request: <em>"Add YOLO object detection to the rear camera module."</em></p>

<table class="demo-table">
<tr><th>Turn</th><th>What happened in the session</th></tr>
<tr><td><code>tr_0001–03</code></td><td>agent searches code graph &amp; docs; proposes YOLOv8</td></tr>
<tr><td><code>tr_0004</code></td><td>engineer: <em>"no, use YOLO11"</em></td></tr>
<tr><td><code>tr_0005</code></td><td><code>write</code> → permission denied</td></tr>
<tr><td><code>tr_0006</code></td><td>retry with same input → success</td></tr>
<tr><td><code>tr_0007–08</code></td><td>tests run; session closes cleanly</td></tr>
</table>

</div>

<div>

<div class="io-divider"><span class="label">Output · learnings report</span></div>

<p style="font-size: 14px; margin: 0 0 4px; color: var(--c-mute); font-family: 'Helvetica Neue', sans-serif; letter-spacing: 0.04em;">Signals the evaluator detected:</p>

<table class="demo-table">
<tr><th>Trace</th><th>Signal</th><th></th></tr>
<tr><td><code>tr_0004</code></td><td><span class="signal-name">User correction</span> — <em>"no"</em> + deprecation reason</td><td><span class="signal-type">implicit</span></td></tr>
<tr><td><code>tr_0006</code></td><td><span class="signal-name">Tool failure echo</span> — text mirrors "permission denied"</td><td><span class="signal-type">implicit</span></td></tr>
<tr><td><code>tr_0005→06</code></td><td><span class="signal-name">Retry</span> — identical <code>path</code> &amp; <code>content</code></td><td><span class="signal-type">implicit</span></td></tr>
<tr><td>—</td><td><span class="signal-name">6 tool calls / 8 turns</span></td><td><span class="signal-type">structural</span></td></tr>
</table>

<p style="font-size: 14px; margin: 6px 0 0;"><strong>Recommendation surfaced.</strong> Add a "preferred libraries" page to the knowledge layer so the first proposal selects the project-standard library.</p>

</div>

</div>

<small>Limitation. The session is synthetic, designed to exhibit the signal classes. Validation against real sessions is part of the roadmap.</small>

---

<div class="section-label">6 · Sample learning report</div>

## What the evaluator writes

<div class="thesis">
One Markdown file. All three signal classes. Every claim cited to a specific trace.
</div>

<div class="report-card">

<span class="filename">eval-reports/ses_synthetic_camera_obj_det_001_20260509T140500Z_learnings.md</span>

<h4>Header</h4>
<p class="meta">8 turns · 2m · Qwen3.5-122B · opencode 1.4.0</p>

<h4>Summary</h4>
<p class="summary">Engineer asked for YOLO object detection. The agent proposed v8; the engineer corrected to v11. A <code>write</code> failed with permission denied; the agent retried successfully.</p>

<div class="cols" style="gap: 22px;">
<div>

<h4>Structural signals</h4>
<ul>
  <li>6 tool calls across 8 turns <span class="cite">(75% tool-using)</span></li>
  <li>Finish reasons — tool-calls 6/8, stop 2/8</li>
  <li>Tokens — 17,320 input / 1,322 output</li>
</ul>

<h4>Qualitative observations</h4>
<ul>
  <li>YOLOv8 selection is a knowledge-layer coverage gap, not a reasoning failure.</li>
  <li>Agent retried <code>write</code> without re-confirming — saved a turn, bypassed engineer review.</li>
</ul>

</div>
<div>

<h4>Implicit signals <span class="cite">CMU FLAME–OpenHands inspired</span></h4>
<ul>
  <li>User correction <span class="cite">tr_0004</span> — <em>"no, use YOLO11"</em></li>
  <li>Tool failure echo <span class="cite">tr_0006</span> — text mirrors <em>"permission denied"</em></li>
  <li>Retry <span class="cite">tr_0005→tr_0006</span> — identical write input</li>
</ul>

<h4>Recommendations</h4>
<ol>
  <li>Add a "preferred libraries" page to the knowledge layer.</li>
  <li>Coordinator prompt: confirm version-sensitive choices before proposing.</li>
  <li>Document the write-retry pattern in the orchestrator prompt.</li>
</ol>

</div>
</div>

</div>

---

<div class="section-label">7 · Integration</div>

## The report is a knowledge artifact

<div class="thesis">
Each report is committed to the repo with a stable, sortable name.
The knowledge layer ingests <code>eval-reports/</code> as a corpus
alongside requirements, specs, and FDA/ASPICE documents.
</div>

**File-name convention.**
<code>eval-reports/&lt;session_id&gt;_&lt;YYYYMMDDTHHMMSSZ&gt;_learnings.md</code>

**The closed loop.**

<div class="pipeline" style="margin-top: 4px;">
<div class="row">
  <div class="box actor">engineer ↔ agent</div>
  <div class="arrow side">→</div>
  <div class="box system">evaluator agent</div>
  <div class="arrow side">→</div>
  <div class="box data">learnings report (in repo)</div>
</div>
<div class="arrow">↓</div>
<div class="row">
  <div class="box data" style="min-width:200px;">eval-reports corpus</div>
  <div class="arrow side">→</div>
  <div class="box system">knowledge layer · vector index</div>
  <div class="arrow side">→</div>
  <div class="box system">future agent context</div>
</div>
</div>

The same machinery that ingests requirements now ingests evaluation
findings. Recommendations surface as agent context on the next
similar task.

---

<div class="section-label">8 · Roadmap</div>

## What is next

<div class="cols">
<div>

<h3>Before the demo · this iteration</h3>

- Replace the CSV-export step with the LangFuse <span class="data">scoring/cost API</span>. <small>(30-min spike.)</small>
- Run the agent against three real sessions to estimate signal recall.
- Cite reports from the eval-reports corpus inside one downstream agent run.

</div>
<div>

<h3>Beyond MVP</h3>

- **Cross-session rollups.** Aggregate signals across sessions to detect agent-level regressions.
- **Formal signal extractors.** Implement the implicit-signal detectors as deterministic Python; reserve the LLM for qualitative judgement.
- **Automated feedback.** Convert recommendations into prompt/skill diffs the team reviews and merges.
- **Framework comparison.** Trial Laminar against LangFuse on the same sessions.

</div>
</div>

<hr>

<small>Reference materials &nbsp;·&nbsp; architecture &nbsp;<code>docs/SYSTEM-EXPLAINED.md</code> &nbsp;·&nbsp; toy data &nbsp;<code>data/synthetic-traces.csv</code> &nbsp;·&nbsp; worked example &nbsp;<code>eval-reports/ses_synthetic_camera_obj_det_001_20260509T140500Z_learnings.md</code></small>
