#!/usr/bin/env python3
"""
generate_synthetic_traces.py — emit a small CSV in LangFuse export format,
representing one toy SDx engineering session.

We build a single session: an engineer adds object detection to a rear-camera
module. The session is intentionally short (7 turns) and intentionally
contains three things the eval agent should detect:

  1. A USER CORRECTION   — the engineer rejects the agent's first proposal
                            and asks for a different library.
  2. A TOOL FAILURE ECHO — a write call fails with permission denied and the
                            agent's next turn references that error.
  3. A RETRY             — the agent re-issues the same write call after the
                            failure.

Run:
    python scripts/generate_synthetic_traces.py --out data/synthetic-traces.csv

The output uses the same column set as the real LangFuse CSV export, so the
existing loader (scripts/load_traces.py) works on it unchanged.
"""

import argparse
import csv
import datetime as dt
import hashlib
import json
from pathlib import Path

# Deterministic trace IDs so documentation can cite them and stay accurate.
TRACE_IDS = [
    "tr_0001_codegraph",
    "tr_0002_vecdocs",
    "tr_0003_proposal",
    "tr_0004_correction",
    "tr_0005_write1",
    "tr_0006_write2_retry",
    "tr_0007_tests",
    "tr_0008_done",
]
_trace_iter = iter(TRACE_IDS)
_call_iter = iter(range(1, 100))


SESSION_ID = "ses_synthetic_camera_obj_det_001"
USER_ID = ""              # anonymous engineer; matches how real exports record unowned traces
ENVIRONMENT = "development"
MODEL_ID = "Qwen3.5-122B-A10B-GPTQ-Int4"
MODEL_PROVIDER = "SDILab-Think.chat"
OPENCODE_UA = "opencode/1.4.0"

SYSTEM_PROMPT = (
    "You are the Orchestrator Agent for the SDx development flow. "
    "Decompose the engineer's task, call MCP tools to gather context, "
    "delegate code edits to subagents, and write code that compiles and "
    "passes tests. Available tools include mcp-gateway_codegraphcontext-* "
    "for code graph queries, mcp-gateway_vector-factory-mcp-search for "
    "documentation retrieval, and the built-in write/bash tools. Confirm "
    "the engineer's intent before making large edits."
)


def _trace_id() -> str:
    return next(_trace_iter)


def _ts(seconds_offset: int) -> str:
    base = dt.datetime(2026, 5, 9, 10, 0, 0, tzinfo=dt.timezone.utc)
    out = base + dt.timedelta(seconds=seconds_offset)
    return f'"{out.isoformat().replace("+00:00", "Z")}"'


def _attrs(input_tokens: int, output_tokens: int, finish_reason: str) -> str:
    """Mimic the LangFuse `metadata.attributes` JSON-encoded string."""
    payload = {
        "operation.name": "ai.streamText",
        "ai.operationId": "ai.streamText",
        "ai.model.provider": MODEL_PROVIDER,
        "ai.model.id": MODEL_ID,
        "ai.settings.maxOutputTokens": "32000",
        "ai.request.headers.x-session-affinity": SESSION_ID,
        "ai.request.headers.User-Agent": OPENCODE_UA,
        "langfuse.environment": ENVIRONMENT,
        "ai.response.finishReason": finish_reason,
        "ai.usage.inputTokens": str(input_tokens),
        "ai.usage.outputTokens": str(output_tokens),
        "ai.usage.totalTokens": str(input_tokens + output_tokens),
        "ai.usage.cachedInputTokens": "0",
    }
    return json.dumps(payload)


def _metadata(input_tokens: int, output_tokens: int, finish_reason: str) -> str:
    return json.dumps({
        "attributes": _attrs(input_tokens, output_tokens, finish_reason),
        "resourceAttributes": json.dumps({
            "host.name": "sdx-engineer-workstation.local",
            "host.arch": "arm64",
            "process.executable.name": "bun",
            "service.name": "opencode",
        }),
        "scope": json.dumps({"name": "ai", "attributes": {}}),
    })


def _build_input(messages: list[dict]) -> str:
    return json.dumps({"messages": messages})


def _build_output(content: str, tool_calls: list[dict] | None = None) -> str:
    out = {"role": "assistant", "content": content}
    if tool_calls:
        out["tool_calls"] = json.dumps([
            {
                "type": "tool-call",
                "toolCallId": f"call_{next(_call_iter):04d}",
                "toolName": tc["name"],
                "input": tc.get("input", {}),
                "dynamic": True,
            }
            for tc in tool_calls
        ])
    return json.dumps(out)


def build_rows() -> list[dict]:
    """Return one list of CSV-row dicts representing the toy session."""
    rows = []
    sys_msg = {"role": "system", "content": SYSTEM_PROMPT}

    user_msg_initial = {"role": "user", "content": "Add YOLO object detection to the rear camera module."}

    # Turn 0 — orchestrator surveys the code graph
    msgs0 = [sys_msg, user_msg_initial]
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(0),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs0),
        "output": _build_output(
            "I'll plan this. First I need to find the rear camera module in the code graph.",
            [{"name": "mcp-gateway_codegraphcontext-search",
              "input": {"query": "rear camera module sensor publisher", "language": "python"}}],
        ),
        "metadata": _metadata(620, 88, "tool-calls"),
        "comments": "[]",
    })

    # Turn 1 — knowledge-layer search for documentation
    msgs1 = msgs0  # input unchanged in this trace; opencode passes the same message stream
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(6),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs1),
        "output": _build_output(
            "Found the module at sensors/camera/rear_view.py. Now searching the knowledge layer for object-detection patterns used elsewhere in the codebase.",
            [{"name": "mcp-gateway_vector-factory-mcp-search",
              "input": {"collections": ["sdx_code_docs"], "query": "camera object detection integration pattern", "top_k": 5}}],
        ),
        "metadata": _metadata(1240, 142, "tool-calls"),
        "comments": "[]",
    })

    # Turn 2 — initial proposal (the wrong library)
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(12),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs1),
        "output": _build_output(
            "Plan: (1) add an `ObjectDetector` class to sensors/camera/rear_view.py using ultralytics YOLOv8, (2) wire detections into the existing camera publisher, (3) add a unit test. Shall I proceed?",
        ),
        "metadata": _metadata(2010, 312, "stop"),
        "comments": "[]",
    })

    # Turn 3 — USER CORRECTION
    user_msg_correction = {"role": "user", "content": "no, use YOLO11. v8 is deprecated for our project."}
    msgs3 = msgs1 + [
        {"role": "assistant", "content": "Plan: (1) add an `ObjectDetector` class ... using ultralytics YOLOv8 ..."},
        user_msg_correction,
    ]
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(64),  # ~1 minute gap — engineer thinking / replying
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs3),
        "output": _build_output(
            "Understood — switching to YOLO11. Re-searching the knowledge layer for any YOLO11 examples already in the project.",
            [{"name": "mcp-gateway_vector-factory-mcp-search",
              "input": {"collections": ["sdx_code_docs"], "query": "YOLO11 ultralytics integration", "top_k": 5}}],
        ),
        "metadata": _metadata(2390, 96, "tool-calls"),
        "comments": "[]",
    })

    # Turn 4 — first write attempt (will fail)
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(72),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs3),
        "output": _build_output(
            "Plan updated for YOLO11. Writing the new detector module now.",
            [{"name": "write",
              "input": {"path": "sensors/camera/rear_view_detector.py",
                        "content": "from ultralytics import YOLO\n\nclass ObjectDetector:\n    ..."}}],
        ),
        "metadata": _metadata(2510, 168, "tool-calls"),
        "comments": "[]",
    })

    # Turn 5 — TOOL FAILURE ECHO + RETRY
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(78),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs3),
        "output": _build_output(
            "The write tool returned permission denied for sensors/camera/rear_view_detector.py. Retrying via the build subagent which has the correct write permissions.",
            [{"name": "write",
              "input": {"path": "sensors/camera/rear_view_detector.py",
                        "content": "from ultralytics import YOLO\n\nclass ObjectDetector:\n    ..."}}],
        ),
        "metadata": _metadata(2680, 184, "tool-calls"),
        "comments": "[]",
    })

    # Turn 6 — run tests
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(86),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs3),
        "output": _build_output(
            "File written successfully. Running the camera module test suite.",
            [{"name": "bash", "input": {"command": "python -m pytest tests/test_rear_camera.py -q"}}],
        ),
        "metadata": _metadata(2890, 92, "tool-calls"),
        "comments": "[]",
    })

    # Turn 7 — done
    rows.append({
        "id": _trace_id(),
        "timestamp": _ts(120),
        "name": "ai.streamText",
        "userId": USER_ID,
        "sessionId": SESSION_ID,
        "release": "",
        "version": "",
        "environment": ENVIRONMENT,
        "tags": "[]",
        "bookmarked": "false",
        "public": "false",
        "input": _build_input(msgs3),
        "output": _build_output(
            "Tests pass (8 passed, 0 failed). The detector is wired into the publisher. The platform's FDA and ASPICE report agents have been queued. Anything else?",
        ),
        "metadata": _metadata(2980, 240, "stop"),
        "comments": "[]",
    })

    return rows


COLUMNS = [
    "id", "timestamp", "name", "userId", "sessionId", "release", "version",
    "environment", "tags", "bookmarked", "public", "input", "output",
    "metadata", "comments",
]


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--out", default="data/synthetic-traces.csv",
                   help="Output CSV path (default: data/synthetic-traces.csv)")
    args = p.parse_args()

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = build_rows()
    with out_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COLUMNS, quoting=csv.QUOTE_ALL)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

    print(f"Wrote {len(rows)} rows to {out_path}")


if __name__ == "__main__":
    main()
