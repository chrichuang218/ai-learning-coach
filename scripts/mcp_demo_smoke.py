#!/usr/bin/env python3
"""Exercise the prototype MCP server without making a model request."""

from __future__ import annotations

import asyncio
import sys
import tempfile
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "ai-learning-coach"
SERVER = PLUGIN_ROOT / "mcp" / "learning_lab_demo.py"


def create_lab(root: Path) -> None:
    (root / "learning-records").mkdir()
    (root / "MISSION.md").write_text(
        "# Mission: 验证 Codex 与 Learning Lab 数据流\n",
        encoding="utf-8",
    )
    (root / "PROGRESS.md").write_text(
        "# Learning Progress\n\n"
        "更新日期：2026-09-03\n"
        "当前主线：通过 MCP 读写隔离的打卡事件\n\n"
        "## 快照\n\n"
        "| 维度 | 进度 |\n"
        "| --- | --- |\n"
        "| 目标能力 | `[############--------] 60%` |\n"
        "| 项目学习范围 | `[########------------] 40%` |\n\n"
        "## 下一检查点\n\n"
        "- 让 Codex 写入一条原型打卡，再读回确认。\n",
        encoding="utf-8",
    )


async def run_smoke(server: Path = SERVER) -> None:
    with tempfile.TemporaryDirectory(prefix="learning-lab-mcp-prototype-") as temp:
        lab = Path(temp)
        create_lab(lab)
        params = StdioServerParameters(
            command=sys.executable,
            args=["-X", "utf8", str(server)],
            cwd=server.parent,
        )
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                tools = await session.list_tools()
                names = {tool.name for tool in tools.tools}
                expected = {
                    "get_learning_snapshot",
                    "record_checkin",
                    "list_checkins",
                    "doctor_learning_lab",
                    "get_resume_context",
                }
                if names != expected:
                    raise RuntimeError(f"Unexpected tool set: {sorted(names)}")

                snapshot = await session.call_tool(
                    "get_learning_snapshot", {"lab_path": str(lab)}
                )
                if snapshot.structuredContent["prototypeCheckinCount"] != 0:
                    raise RuntimeError("Expected an empty prototype check-in log")
                if [row["percent"] for row in snapshot.structuredContent["progress"]] != [60, 40]:
                    raise RuntimeError("Expected legacy snapshot percentages 60/40")
                resume = await session.call_tool("get_resume_context", {"lab_path": str(lab)})
                if not resume.structuredContent["nextCheckpoint"] or resume.structuredContent["nextCheckpoint"] != snapshot.structuredContent["nextCheckpoint"]:
                    raise RuntimeError("Resume lost the real checkpoint")
                before = {p.name: p.read_bytes() for p in lab.glob("*.md")}

                written = await session.call_tool(
                    "record_checkin",
                    {
                        "lab_path": str(lab),
                        "checkin_date": "2026-09-03",
                        "level": "run",
                        "note": "MCP protocol smoke passed",
                    },
                )
                if written.structuredContent["masteryChanged"] is not False:
                    raise RuntimeError("Prototype check-in must not change mastery")

                listed = await session.call_tool(
                    "list_checkins", {"lab_path": str(lab)}
                )
                if listed.structuredContent["count"] != 1:
                    raise RuntimeError("Expected one persisted prototype check-in")
                if before != {p.name: p.read_bytes() for p in lab.glob("*.md")}:
                    raise RuntimeError("Prototype changed authoritative Markdown")

                doctor = await session.call_tool(
                    "doctor_learning_lab", {"lab_path": str(lab)}
                )
                if doctor.structuredContent["status"] != "pass":
                    raise RuntimeError(f"Doctor failed: {doctor.structuredContent}")

                print("MCP demo smoke passed")
                print(f"tools={','.join(sorted(names))}")
                print(f"mission={snapshot.structuredContent['mission']}")
                print(f"checkins={listed.structuredContent['count']}")
                print("masteryChanged=false")


if __name__ == "__main__":
    asyncio.run(run_smoke())
