#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["mcp==1.27.0"]
# ///
"""Learning Lab state tools over MCP stdio. Markdown stays the source of truth."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any, Literal

sys.path.insert(0, str(Path(__file__).resolve().parent))

from mcp.server.fastmcp import FastMCP
from mcp.types import ToolAnnotations

import learning_core as core


SERVER_NAME = "learning-lab"

READ_ONLY = ToolAnnotations(readOnlyHint=True, destructiveHint=False, idempotentHint=True, openWorldHint=False)
WRITE_LOCAL = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=False, openWorldHint=False)
SYNC_LOCAL = ToolAnnotations(readOnlyHint=False, destructiveHint=False, idempotentHint=True, openWorldHint=False)

mcp = FastMCP(
    SERVER_NAME,
    instructions=(
        "Learning Lab state tools. Markdown files stay the source of truth. Write evidence with record_evidence, "
        "change mastery only through set_milestone_state (it refuses states the evidence does not support), and let "
        "sync_progress recompute percentages and rhythm instead of editing those numbers by hand. Check-ins count as "
        "attendance and never change mastery. Verify the source repository yourself before resuming."
    ),
)


@mcp.tool(title="Get learning snapshot", annotations=READ_ONLY, structured_output=True,
          description="Read mission, mainline, derived progress, milestones, rhythm, evidence, due reviews and state warnings.")
def get_learning_snapshot(lab_path: str, as_of: str | None = None) -> dict[str, Any]:
    return core.get_snapshot(lab_path, as_of)


@mcp.tool(title="Resume learning", annotations=READ_ONLY, structured_output=True,
          description="Read the checkpoint, recent evidence, due reviews and warnings before resuming. Source code still needs verification.")
def get_resume_context(lab_path: str, as_of: str | None = None) -> dict[str, Any]:
    return core.get_resume_context(lab_path, as_of)


@mcp.tool(title="Check Learning Lab health", annotations=READ_ONLY, structured_output=True,
          description="Report missing files, broken links, drift and unsupported mastery states without changing anything.")
def doctor_learning_lab(lab_path: str, as_of: str | None = None) -> dict[str, Any]:
    snapshot = core.get_snapshot(lab_path, as_of)
    return {"status": snapshot["status"], "asOf": snapshot["asOf"], "issues": snapshot["issues"],
            "sourceVerification": "not_checked"}


@mcp.tool(title="Review queue", annotations=READ_ONLY, structured_output=True,
          description="List evidence whose review_after date has passed without newer evidence on the same milestone, plus reviews due within 7 days.")
def get_review_queue(lab_path: str, as_of: str | None = None) -> dict[str, Any]:
    return core.get_review_queue(lab_path, as_of)


@mcp.tool(title="Weekly review", annotations=READ_ONLY, structured_output=True,
          description="Summarize the last seven days: learning days, evidence by milestone, due reviews and the next checkpoint, with a Markdown draft.")
def get_weekly_review(lab_path: str, as_of: str | None = None) -> dict[str, Any]:
    return core.get_weekly_review(lab_path, as_of)


@mcp.tool(title="Record learning evidence", annotations=WRITE_LOCAL, structured_output=True,
          description=("Append one observed action as a validated learning-evidence block to a file under learning-records/. "
                       "Fields: id, observed_at, milestone_id, action, assistance_level (demonstrated|guided|independent|transferred), "
                       "result, source_ref {kind: code(path,symbol,commit)|url(url)|document(title)|task(description)}, optional "
                       "review_reason, next_action, review_after (YYYY-MM-DD). Never changes mastery."))
def record_evidence(lab_path: str, record_path: str, evidence: dict[str, Any], title: str | None = None) -> dict[str, Any]:
    return core.record_evidence(lab_path, record_path, evidence, title)


@mcp.tool(title="Set milestone state", annotations=WRITE_LOCAL, structured_output=True,
          description=("Change one PROGRESS.md milestone state, link its learning record and recompute progress. Independent "
                       "needs independent or transferred evidence; transferred needs transferred evidence."))
def set_milestone_state(lab_path: str, milestone: str, state: str, evidence_record: str | None = None,
                        next_evidence: str | None = None, scope: Literal["goal", "project"] | None = None) -> dict[str, Any]:
    return core.set_milestone_state(lab_path, milestone, state, evidence_record, next_evidence, scope)


@mcp.tool(title="Sync derived progress", annotations=SYNC_LOCAL, structured_output=True,
          description="Recompute weighted progress lines, snapshot percentages and the rhythm section in PROGRESS.md. Authored text is kept.")
def sync_progress(lab_path: str) -> dict[str, Any]:
    return core.sync_progress(lab_path)


@mcp.tool(title="Record check-in", annotations=WRITE_LOCAL, structured_output=True,
          description="Append one attendance event to .learning-coach/checkins.jsonl. It counts toward rhythm and never changes mastery.")
def record_checkin(lab_path: str, checkin_date: str, level: Literal["review", "explain", "run", "milestone"], note: str) -> dict[str, Any]:
    return core.record_checkin(lab_path, checkin_date, level, note)


@mcp.tool(title="List check-ins", annotations=READ_ONLY, structured_output=True,
          description="Read attendance events without changing Learning Lab state.")
def list_checkins(lab_path: str) -> dict[str, Any]:
    lab = core.resolve_lab(lab_path)
    events = core.load_checkins(lab)
    return {"path": str(core.checkins_path(lab)), "count": len(events), "events": events}


if __name__ == "__main__":
    mcp.run(transport="stdio")
