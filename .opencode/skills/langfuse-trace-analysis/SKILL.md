---
name: langfuse-trace-analysis
description: Read LangFuse trace exports from the SDx flow and pull structural, qualitative, and implicit-signal evidence out of one session of human-agent interaction.
license: MIT
compatibility: opencode
metadata:
  audience: evaluator-agent
  input: langfuse-csv-export
  output: per-session-trace-packet
---

# What I do

I teach you the shape of the LangFuse data captured by the SDx flow and the
specific signals you should pull out of it when writing a learnings report.

Load me when you are about to analyze a trace packet built by
`scripts/load_traces.py`. Skip me for unrelated tasks.

---

# Trace data shape (what's in the export)

The LangFuse CSV export has 15 columns. Most rows are not useful. Two trace
names matter:

| `name` value | What it is | Has content? | Use for |
|---|---|---|---|
| `ai.streamText` | One opencode model call (system prompt + messages → assistant + tool calls) | Yes — full input/output | Learnings report |
| `llm_request` | vLLM-side OpenTelemetry span: latency, token counts | No | Cost/latency rollups only |
| `Overall Loading` | Trace name from a different instrumentation path | No | Ignore |

**Always filter to `name == "ai.streamText"`** when looking for content. The
loader does this for you.

The fields you care about per `ai.streamText` row, after the loader normalizes
them:

- `timestamp`, `trace_id`, `session_id`, `userId`
- `system_prompt` (the agent's system message; often very long — the loader
  deduplicates by hash so you see each unique one once per packet)
- `user_messages` (list — usually one user message per turn, but the title
  generator passes two)
- `assistant_content` (the model's text output; may be empty when the model
  emits only tool calls)
- `tool_calls` (list of `{name, id, input}`)
- `finish_reason` — `"stop"`, `"tool-calls"`, `"length"`, `"error"`, `"content-filter"`
- `input_tokens`, `output_tokens`, `total_tokens`, `cached_input_tokens`
- `model_id`, `model_provider`, `opencode_user_agent`

---

# How to invoke the loader

```bash
# List sessions to pick from
python scripts/load_traces.py --csv <export.csv> --list

# Build a packet for one session (writes JSON to stdout)
python scripts/load_traces.py --csv <export.csv> --session <session_id> > packet.json

# Or batch every session into a directory
python scripts/load_traces.py --csv <export.csv> --out-dir packets/
```

A typical 20-turn session produces a ~70 KB JSON packet. Read it with the
`read` tool.

---

# Signals to extract

Group your findings into these three buckets. Every signal in the report must
cite a `trace_id` (or a list of them) so a reader can verify it.

## 1. Structural signals (deterministic — compute, don't infer)

Walk the `turns` array and count:

- **Turn count** and **wall-clock duration** (`last_timestamp - first_timestamp`)
- **Tool-call mix**: how many turns had tool calls, which tools, top 5 by count
- **Finish-reason distribution**: % `stop` vs `tool-calls` vs `length` vs `error`
- **Token usage**: total in / out, average per turn, peak input (often a
  ballooning context — flag it)
- **Cache hit rate**: `cached_input_tokens / input_tokens` if non-zero
- **System-prompt churn**: number of distinct `system_prompt_hash` values.
  More than one usually means the agent switched personas (e.g., from a
  title-generator helper into the main coordinator).

## 2. Qualitative observations (LLM judgment — cite turn timestamps)

Read the `user_messages` and `assistant_content` end-to-end and answer:

- What did the user actually want? (One sentence per session.)
- Did the agent succeed, partially succeed, or fail?
- Did the agent's plan match what the user asked for, or did it drift?
- Were any assistant responses unusually long, repetitive, or off-topic?
- Did the agent surface meaningful intermediate progress, or only a final answer?

Be specific. Quote ≤15-word excerpts when useful, citing trace_id.

## 3. Implicit signals (FLAME-style — pattern-match in the turns)

These are the "free" signals that come from real interaction, no labels needed.
Each one is a hypothesis about agent quality. Report them as evidence, not
verdicts.

| Signal | How to detect it in the packet |
|---|---|
| **User correction** | A user message that begins with words like "no", "actually", "wait", "that's wrong", "stop", or that asks to undo / redo something the agent just did. Also: a user message that re-states a constraint the agent just violated. |
| **Retry** | Two consecutive turns where the agent calls the same tool with similar inputs after a `tool-calls` finish, especially if the second call's input changes one parameter. |
| **Abandoned trajectory** | Session ends on `finish_reason == "tool-calls"` (the agent was mid-action) with no follow-up user message. Or: a long gap (>10 min) between the last assistant turn and any user reply. |
| **Follow-up edit** | A user message after the agent edited code or wrote a file, where the user's text references the edit (e.g., "change line", "remove that", "you missed", a filename or function name from the prior turn). |
| **Context bloat** | `input_tokens` for one turn jumps >3× the session median. Often signals the agent is re-sending tool output it already has. |
| **Tool failure echo** | Two adjacent assistant turns both calling tools, where the second turn's text mentions an error from the first (substring matches like "error", "failed", "not found", "permission denied"). |

---

# Report structure to produce

Write the markdown report to:

```
eval-reports/<session_id>_<UTC_TIMESTAMP>_learnings.md
```

Where `<UTC_TIMESTAMP>` is the moment the report is generated, in compact
ISO 8601 form `YYYYMMDDTHHMMSSZ` (always UTC, always with the trailing
`Z`). Get it with `date -u +%Y%m%dT%H%M%SZ` from the bash tool.

Example:
`eval-reports/ses_synthetic_camera_obj_det_001_20260509T140500Z_learnings.md`

This convention ensures:

- The same session can be re-evaluated as the agent improves, without
  overwriting prior reports.
- Files sort chronologically per session when listed.
- The trailing `_learnings.md` makes the file's purpose obvious in any
  directory listing.

Keep total length under 600 lines.

```markdown
# Eval report — <session_id>

**User:** <userId> | **Time:** <first_timestamp> → <last_timestamp> | **Turns:** <n>
**Models:** <list> | **opencode:** <version>

## Summary
One paragraph. What the user wanted, whether they got it, and the single most
important learning.

## Structural signals
- bullet list of metrics from section 1 above

## Qualitative observations
- bullet list, each ending with `(trace_id: <id>)` or `(turns: <ts1>, <ts2>)`

## Implicit signals (FLAME-style)
For each detected signal, one sub-section:
### <Signal name>
Evidence: short quote or description, with trace_ids.
Interpretation: what this suggests about the agent or the prompt.

## Recommendations
Concrete, prioritized changes to feed back into the SDx system. Address the
agent prompt, the tool surface, the user experience, or the workflow — never
the user.

## Appendix: raw packet
Path to the JSON packet on disk. (Do not inline it.)
```

---

# Things I will not do

- I will not invent signals that aren't in the data. If `user_messages` is
  empty for every turn (a title-generator session, for example), say so and
  produce a short report.
- I will not summarize the system prompt. Reference it by hash.
- I will not score the agent on a numeric scale unless the user asks; the
  point of this MVP is qualitative learning, not benchmarking.
- I will not include the full assistant text in the report. Quote sparingly.
