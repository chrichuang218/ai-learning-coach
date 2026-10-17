#!/usr/bin/env python3
"""Exercise the Learning Lab MCP server end to end without making a model request."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from datetime import date
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "ai-learning-coach"
SERVER = PLUGIN_ROOT / "mcp" / "server.py"
EXPECTED_TOOLS = {
    "get_learning_snapshot", "get_resume_context", "doctor_learning_lab", "get_review_queue", "get_weekly_review",
    "record_evidence", "set_milestone_state", "sync_progress", "record_checkin", "list_checkins",
}


def create_lab(root: Path) -> None:
    (root / "MISSION.md").write_text("# Mission: 验证 Learning Lab 数据流\n", encoding="utf-8")
    (root / "PROGRESS.md").write_text(
        "# Learning Progress\n\n"
        "更新日期：2026-09-03\n"
        "当前主线：通过 MCP 写入证据并派生进度\n"
        "进度起算日：2026-09-03\n\n"
        "## 快照\n\n"
        "| 维度 | 进度 |\n"
        "| --- | --- |\n"
        "| 目标能力 | `[--------------------] 0%` |\n\n"
        "## 目标能力进度\n\n"
        "| 里程碑 | 权重 | 掌握状态 | 当前证据 | 下一次升级证据 |\n"
        "| --- | ---: | --- | --- | --- |\n"
        "| 缓存失效 | 100% | 未开始 0% | 尚无证据 | 运行目标测试 |\n\n"
        "## 下一检查点\n\n"
        "- 写入一条证据，升级里程碑，再读回确认。\n",
        encoding="utf-8",
    )


CONFIGS = {"codex": ".codex-mcp.json", "claude": ".mcp.json"}


def config_params(server: Path, host: str) -> StdioServerParameters:
    """Launch exactly as a host's plugin MCP config says: Codex resolves cwd, Claude Code expands the plugin root."""
    plugin_root = server.parent.parent
    config = json.loads((plugin_root / CONFIGS[host]).read_text(encoding="utf-8"))["mcpServers"]["learning-lab"]
    args = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(plugin_root)) for a in config["args"]]
    cwd = (plugin_root / config["cwd"]).resolve() if "cwd" in config else Path(tempfile.gettempdir())
    return StdioServerParameters(command=config["command"], args=args, cwd=cwd, env={**os.environ, **config.get("env", {})})


async def run_smoke(server: Path = SERVER, use_config: str | None = None) -> None:
    today = date.today().isoformat()
    with tempfile.TemporaryDirectory(prefix="learning-lab-mcp-") as temp:
        lab = Path(temp)
        create_lab(lab)
        params = config_params(server, use_config) if use_config else StdioServerParameters(
            command=sys.executable, args=["-X", "utf8", str(server)], cwd=server.parent)
        async with stdio_client(params) as (read_stream, write_stream):
            async with ClientSession(read_stream, write_stream) as session:
                await session.initialize()
                names = {tool.name for tool in (await session.list_tools()).tools}
                if names != EXPECTED_TOOLS:
                    raise RuntimeError(f"Unexpected tool set: {sorted(names)}")

                async def call(name: str, arguments: dict) -> dict:
                    result = await session.call_tool(name, {"lab_path": str(lab), **arguments})
                    if result.isError:
                        raise RuntimeError(f"{name} failed: {result.content}")
                    return result.structuredContent

                snapshot = await call("get_learning_snapshot", {})
                if [row["percent"] for row in snapshot["progress"]] != [0]:
                    raise RuntimeError("Expected derived progress 0%")
                evidence = {"id": "smoke-1", "observed_at": today, "milestone_id": "缓存失效", "action": "运行目标测试",
                            "assistance_level": "guided", "result": "Green", "review_after": today,
                            "source_ref": {"kind": "task", "description": "MCP smoke"}}
                written = await call("record_evidence", {"record_path": "learning-records/smoke.md", "evidence": evidence})
                if written["masteryChanged"] is not False:
                    raise RuntimeError("Evidence must not change mastery")
                refused = await session.call_tool("set_milestone_state", {"lab_path": str(lab), "milestone": "缓存失效",
                                                                         "state": "独立", "evidence_record": "learning-records/smoke.md"})
                if not refused.isError:
                    raise RuntimeError("Guided evidence must not support an independent state")
                moved = await call("set_milestone_state", {"milestone": "缓存失效", "state": "需提示",
                                                           "evidence_record": "learning-records/smoke.md"})
                if moved["progress"][0]["percent"] != 50 or moved["status"] != "pass":
                    raise RuntimeError(f"Unexpected milestone result: {moved}")
                await call("record_checkin", {"checkin_date": today, "level": "run", "note": "MCP smoke"})
                if (await call("list_checkins", {}))["count"] != 1:
                    raise RuntimeError("Expected one persisted check-in")
                if not (await call("get_review_queue", {}))["due"]:
                    raise RuntimeError("Expected the smoke evidence to be due for review")
                resume = await call("get_resume_context", {})
                if not resume["nextCheckpoint"] or not resume["reviewDue"]:
                    raise RuntimeError("Resume lost the checkpoint or due review")
                if "smoke-1" not in json.dumps(await call("get_weekly_review", {})):
                    raise RuntimeError("Weekly review missed this week's evidence")
                if (await call("doctor_learning_lab", {}))["status"] != "pass":
                    raise RuntimeError("Doctor reported problems after tool writes")
                print("MCP smoke passed")
                print(f"tools={len(names)} launcher={use_config or 'python'} progress=50%")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--use-config", choices=sorted(CONFIGS), help="Launch with a host's plugin MCP config (needs uv)")
    asyncio.run(run_smoke(use_config=parser.parse_args().use_config))
