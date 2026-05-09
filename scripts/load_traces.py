#!/usr/bin/env python3
"""
load_traces.py — turn a LangFuse CSV export into compact per-session trace packets.

The raw CSV is too large and too noisy to feed an LLM directly. This script:
  1. Reads the CSV (handles 100+ MB rows via csv.field_size_limit).
  2. Keeps only the rows that contain real opencode interaction content
     (default: name == 'ai.streamText'; the 'llm_request' rows are vLLM
     telemetry without user/assistant content).
  3. Groups rows by sessionId.
  4. Emits a compact JSON "packet" per session — small enough for an LLM to
     read end-to-end, but with enough signal to write a learnings report.

Usage:
  List sessions (sorted by trace count, with user and time range):
      python scripts/load_traces.py --csv path/to/export.csv --list

  Build one session packet to stdout:
      python scripts/load_traces.py --csv path/to/export.csv --session ses_XXX

  Build all session packets into a directory:
      python scripts/load_traces.py --csv path/to/export.csv --out-dir packets/
"""

import argparse
import csv
import hashlib
import json
import sys
from collections import defaultdict
from pathlib import Path

csv.field_size_limit(sys.maxsize)


def _safe_json(s):
    if not s:
        return None
    try:
        return json.loads(s)
    except (ValueError, TypeError):
        return None


def _short_hash(text: str) -> str:
    return hashlib.sha1(text.encode("utf-8", errors="ignore")).hexdigest()[:8]


def _flatten_metadata_attributes(metadata_obj):
    """LangFuse stores `metadata.attributes` as a JSON-encoded STRING. Decode it."""
    if not isinstance(metadata_obj, dict):
        return {}
    attrs = metadata_obj.get("attributes")
    if isinstance(attrs, str):
        decoded = _safe_json(attrs) or {}
    elif isinstance(attrs, dict):
        decoded = attrs
    else:
        decoded = {}
    return decoded


def _extract_turn(row):
    """Pull the useful fields out of one ai.streamText row."""
    inp = _safe_json(row.get("input")) or {}
    out_raw = row.get("output") or ""
    out = _safe_json(out_raw)
    meta = _safe_json(row.get("metadata")) or {}
    attrs = _flatten_metadata_attributes(meta)

    messages = inp.get("messages") if isinstance(inp, dict) else None
    system_prompt = ""
    user_messages = []
    if isinstance(messages, list):
        for m in messages:
            role = m.get("role")
            content = m.get("content")
            if isinstance(content, list):
                content = " ".join(
                    p.get("text", "") for p in content if isinstance(p, dict)
                )
            if not isinstance(content, str):
                content = json.dumps(content)[:500]
            if role == "system" and not system_prompt:
                system_prompt = content
            elif role == "user":
                user_messages.append(content)

    if isinstance(out, dict):
        assistant_content = out.get("content") or ""
        tool_calls_raw = out.get("tool_calls")
    else:
        assistant_content = out_raw
        tool_calls_raw = None

    tool_calls = []
    if isinstance(tool_calls_raw, str):
        decoded = _safe_json(tool_calls_raw)
        if isinstance(decoded, list):
            tool_calls_raw = decoded
    if isinstance(tool_calls_raw, list):
        for tc in tool_calls_raw:
            if not isinstance(tc, dict):
                continue
            tool_calls.append(
                {
                    "name": tc.get("toolName") or tc.get("name"),
                    "id": tc.get("toolCallId") or tc.get("id"),
                    "input": tc.get("input") or tc.get("args"),
                }
            )

    def _num(key):
        v = attrs.get(key)
        if isinstance(v, str):
            try:
                return float(v)
            except ValueError:
                return None
        if isinstance(v, (int, float)):
            return float(v)
        return None

    return {
        "trace_id": row.get("id"),
        "timestamp": row.get("timestamp", "").strip('"'),
        "system_prompt": system_prompt,
        "user_messages": user_messages,
        "assistant_content": assistant_content if isinstance(assistant_content, str) else json.dumps(assistant_content)[:2000],
        "tool_calls": tool_calls,
        "finish_reason": attrs.get("ai.response.finishReason"),
        "model_id": attrs.get("ai.model.id"),
        "model_provider": attrs.get("ai.model.provider"),
        "input_tokens": _num("ai.usage.inputTokens"),
        "output_tokens": _num("ai.usage.outputTokens"),
        "total_tokens": _num("ai.usage.totalTokens"),
        "cached_input_tokens": _num("ai.usage.cachedInputTokens"),
        "opencode_user_agent": attrs.get("ai.request.headers.User-Agent"),
    }


def _build_session_packet(session_id, turns):
    turns = sorted(turns, key=lambda t: t["timestamp"])

    system_prompts = {}
    for t in turns:
        sp = t.get("system_prompt") or ""
        if sp:
            h = _short_hash(sp)
            system_prompts.setdefault(h, {"hash": h, "char_count": len(sp), "preview": sp[:600]})
        t["system_prompt_hash"] = _short_hash(sp) if sp else None
        del t["system_prompt"]

    total_input = sum((t.get("input_tokens") or 0) for t in turns)
    total_output = sum((t.get("output_tokens") or 0) for t in turns)
    total_tokens = sum((t.get("total_tokens") or 0) for t in turns)

    tool_call_names = []
    for t in turns:
        for tc in t.get("tool_calls", []):
            if tc.get("name"):
                tool_call_names.append(tc["name"])

    return {
        "session_id": session_id,
        "first_timestamp": turns[0]["timestamp"] if turns else None,
        "last_timestamp": turns[-1]["timestamp"] if turns else None,
        "turn_count": len(turns),
        "tool_call_count": len(tool_call_names),
        "unique_tool_names": sorted(set(tool_call_names)),
        "total_input_tokens": int(total_input),
        "total_output_tokens": int(total_output),
        "total_tokens": int(total_tokens),
        "models_seen": sorted({t["model_id"] for t in turns if t.get("model_id")}),
        "opencode_versions": sorted({t["opencode_user_agent"] for t in turns if t.get("opencode_user_agent")}),
        "system_prompts": list(system_prompts.values()),
        "turns": turns,
    }


def _iter_target_rows(csv_path: Path, name_filter: str):
    with csv_path.open("r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("name") != name_filter:
                continue
            yield row


def cmd_list(args):
    by_session = defaultdict(lambda: {"count": 0, "users": set(), "first": None, "last": None})
    for row in _iter_target_rows(Path(args.csv), args.name):
        sid = row.get("sessionId") or "(no-session)"
        ts = row.get("timestamp", "").strip('"')
        rec = by_session[sid]
        rec["count"] += 1
        if row.get("userId"):
            rec["users"].add(row["userId"])
        if rec["first"] is None or ts < rec["first"]:
            rec["first"] = ts
        if rec["last"] is None or ts > rec["last"]:
            rec["last"] = ts

    rows = sorted(by_session.items(), key=lambda kv: -kv[1]["count"])
    print(f"{'session_id':<48} {'turns':>6}  {'users':<24} {'first':<28} {'last':<28}")
    for sid, rec in rows:
        users = ",".join(sorted(rec["users"])) or "-"
        print(f"{sid:<48} {rec['count']:>6}  {users[:24]:<24} {rec['first'][:28]:<28} {rec['last'][:28]:<28}")
    print(f"\n{len(rows)} sessions, {sum(r['count'] for _, r in rows)} '{args.name}' rows total.")


def cmd_packet(args):
    by_session = defaultdict(list)
    for row in _iter_target_rows(Path(args.csv), args.name):
        sid = row.get("sessionId") or "(no-session)"
        if args.session and sid != args.session:
            continue
        by_session[sid].append(_extract_turn(row))

    if args.session:
        if args.session not in by_session:
            print(f"No '{args.name}' rows found for session {args.session}", file=sys.stderr)
            sys.exit(2)
        packet = _build_session_packet(args.session, by_session[args.session])
        sys.stdout.write(json.dumps(packet, indent=2, ensure_ascii=False))
        return

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    for sid, turns in by_session.items():
        packet = _build_session_packet(sid, turns)
        safe = sid.replace("/", "_")
        (out_dir / f"{safe}.json").write_text(
            json.dumps(packet, indent=2, ensure_ascii=False)
        )
    print(f"Wrote {len(by_session)} packets to {out_dir}/", file=sys.stderr)


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--csv", required=True, help="Path to LangFuse CSV export")
    p.add_argument("--name", default="ai.streamText",
                   help="Trace name to keep (default: ai.streamText, the opencode-side rows)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--list", action="store_true", help="List sessions instead of building a packet")
    g.add_argument("--session", help="Build a packet for this single sessionId, write JSON to stdout")
    g.add_argument("--out-dir", help="Build packets for ALL sessions, write one JSON file per session here")
    args = p.parse_args()

    if args.list:
        cmd_list(args)
    else:
        cmd_packet(args)


if __name__ == "__main__":
    main()
