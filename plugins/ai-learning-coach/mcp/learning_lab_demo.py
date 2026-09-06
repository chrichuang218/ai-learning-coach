#!/usr/bin/env python3
"""PROTOTYPE: expose a small Learning Lab data flow over MCP stdio."""

from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Literal
from uuid import uuid4

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

from learning_core import get_snapshot, get_resume_context as read_resume_context, resolve_lab


SERVER_NAME = "learning-lab-demo"
PROTOTYPE_DIR = ".learning-coach-prototype"
CHECKINS_FILE = "checkins.jsonl"

READ_ONLY = ToolAnnotations(
    readOnlyHint=True,
    destructiveHint=False,
    idempotentHint=True,
    openWorldHint=False,
)
WRITE_LOCAL = ToolAnnotations(
    readOnlyHint=False,
    destructiveHint=False,
    idempotentHint=False,
    openWorldHint=False,
)

mcp = FastMCP(
    SERVER_NAME,
    instructions=(
        "This is a local prototype. Read MISSION.md and PROGRESS.md through "
        "get_learning_snapshot. record_checkin writes only to the isolated "
        f"{PROTOTYPE_DIR}/{CHECKINS_FILE} file and never changes mastery."
    ),
)


def checkins_path(lab: Path) -> Path:
    return lab / PROTOTYPE_DIR / CHECKINS_FILE


def load_checkins(lab: Path) -> list[dict[str, object]]:
    path = checkins_path(lab)
    if not path.exists():
        return []
    events: list[dict[str, object]] = []
    for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid check-in JSON at line {line_number}: {exc}") from exc
    return events


@mcp.tool(
    title="Get learning snapshot",
    description=(
        "Read a local Learning Lab's mission, current mainline, progress summary, "
        "next checkpoint, record count, and prototype check-ins."
    ),
    annotations=READ_ONLY,
    structured_output=True,
)
def get_learning_snapshot(lab_path: str) -> dict[str, object]:
    snapshot = get_snapshot(lab_path)
    return {
        **snapshot,
        "prototype": True,
        "prototypeCheckinCount": len(load_checkins(resolve_lab(lab_path))),
    }


@mcp.tool(
    title="Resume learning",
    description="Read the current checkpoint, recent evidence, assistance boundaries and state warnings before resuming. Source code still needs verification.",
    annotations=READ_ONLY,
    structured_output=True,
)
def get_resume_context(lab_path: str) -> dict[str, object]:
    return read_resume_context(lab_path)


@mcp.tool(
    title="Record prototype check-in",
    description=(
        "Append one attendance event to .learning-coach-prototype/checkins.jsonl. "
        "This never changes PROGRESS.md, mastery, evidence, or learning records."
    ),
    annotations=WRITE_LOCAL,
    structured_output=True,
)
def record_checkin(
    lab_path: str,
    checkin_date: str,
    level: Literal["review", "explain", "run", "milestone"],
    note: str,
) -> dict[str, object]:
    lab = resolve_lab(lab_path)
    try:
        date.fromisoformat(checkin_date)
    except ValueError as exc:
        raise ValueError("checkin_date must use YYYY-MM-DD") from exc

    normalized_note = " ".join(note.split())
    if not normalized_note:
        raise ValueError("note must not be empty")
    if len(normalized_note) > 200:
        raise ValueError("note must be at most 200 characters")

    path = checkins_path(lab)
    path.parent.mkdir(parents=True, exist_ok=True)
    event = {
        "schemaVersion": 1,
        "eventId": str(uuid4()),
        "eventType": "attendance",
        "date": checkin_date,
        "level": level,
        "note": normalized_note,
        "source": "codex-mcp-prototype",
        "recordedAt": datetime.now(timezone.utc).isoformat(),
    }
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")

    return {
        "prototype": True,
        "writtenTo": str(path),
        "event": event,
        "checkinCount": len(load_checkins(lab)),
        "masteryChanged": False,
    }


@mcp.tool(
    title="List prototype check-ins",
    description="Read prototype attendance events without changing Learning Lab state.",
    annotations=READ_ONLY,
    structured_output=True,
)
def list_checkins(lab_path: str) -> dict[str, object]:
    lab = resolve_lab(lab_path)
    events = load_checkins(lab)
    return {
        "prototype": True,
        "path": str(checkins_path(lab)),
        "count": len(events),
        "events": events,
    }


@mcp.tool(
    title="Check Learning Lab health",
    description=(
        "Check required files and obvious date drift. This is read-only and reports "
        "problems instead of inventing defaults."
    ),
    annotations=READ_ONLY,
    structured_output=True,
)
def doctor_learning_lab(lab_path: str) -> dict[str, object]:
    snapshot = get_snapshot(lab_path)
    return {
        "prototype": True,
        "status": snapshot["status"],
        "issues": [entry["message"] for entry in snapshot["issues"]],
        "diagnostics": snapshot["issues"],
        "checkedFiles": ["MISSION.md", "PROGRESS.md", "README.md", "learning-records/**/*.md", "sources/**/*.md"],
        "sourceVerification": "not_checked",
    }


if __name__ == "__main__":
    mcp.run(transport="stdio")
