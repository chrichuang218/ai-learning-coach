#!/usr/bin/env python3
"""Run a real Codex turn through the installed prototype MCP server."""

from __future__ import annotations

import json
import shutil
import subprocess
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def create_lab(root: Path) -> None:
    (root / "learning-records").mkdir()
    (root / "MISSION.md").write_text(
        "# Mission: 验证真实 Codex MCP 数据流\n",
        encoding="utf-8",
    )
    (root / "PROGRESS.md").write_text(
        "# Learning Progress\n\n"
        "更新日期：2026-09-03\n"
        "当前主线：让 Codex 调用 MCP 并读回打卡\n\n"
        "## 下一检查点\n\n"
        "- 完成真实 Codex tool call 往返。\n",
        encoding="utf-8",
    )


def main() -> int:
    codex = shutil.which("codex")
    if codex is None:
        raise RuntimeError("Codex CLI is not available on PATH")

    with tempfile.TemporaryDirectory(prefix="codex-learning-lab-prototype-") as temp:
        lab = Path(temp)
        create_lab(lab)
        prompt = (
            "Use the learning-lab-demo MCP tools. "
            f"First read the learning snapshot at {lab}. "
            "Then record a 2026-09-03 run-level check-in with note "
            "'real Codex MCP round trip'. Finally list check-ins and report the "
            "mission, check-in count, and whether mastery changed. You must use the MCP tools."
        )
        command = [
            codex,
            "exec",
            "--ephemeral",
            "--json",
            "--sandbox",
            "read-only",
            "--config",
            'plugins."ai-learning-coach".mcp_servers."learning-lab-demo".default_tools_approval_mode="approve"',
            prompt,
        ]
        completed = subprocess.run(
            command,
            cwd=ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"Codex smoke failed ({completed.returncode}):\n{completed.stderr}\n{completed.stdout}"
            )

        events = [json.loads(line) for line in completed.stdout.splitlines() if line.strip()]
        mcp_calls = [
            event
            for event in events
            if event.get("type") == "item.completed"
            and event.get("item", {}).get("type") == "mcp_tool_call"
        ]
        checkins = lab / ".learning-coach-prototype" / "checkins.jsonl"
        if not checkins.is_file():
            raise RuntimeError("Codex completed without creating the prototype check-in file")
        rows = [json.loads(line) for line in checkins.read_text(encoding="utf-8").splitlines()]
        if len(rows) != 1 or rows[0]["note"] != "real Codex MCP round trip":
            raise RuntimeError(f"Unexpected persisted events: {rows}")
        if len(mcp_calls) < 3:
            raise RuntimeError(f"Expected at least 3 MCP calls, got {len(mcp_calls)}")

        print("Real Codex MCP demo passed")
        print(f"mcpToolCalls={len(mcp_calls)}")
        print(f"persistedCheckins={len(rows)}")
        print("masteryChanged=false")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
