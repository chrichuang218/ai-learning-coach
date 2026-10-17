# Learning Lab MCP Server

`server.py` exposes a local Learning Lab over MCP stdio. Markdown files stay the source of truth; the server reads them, derives numbers, and writes only through validated operations.

| Tool | Writes | Purpose |
| --- | --- | --- |
| `get_learning_snapshot` | no | Mission, mainline, derived progress, milestones, rhythm, evidence, due reviews, warnings |
| `get_resume_context` | no | Checkpoint, recent evidence and due reviews before resuming |
| `doctor_learning_lab` | no | Missing files, broken links, drift, unsupported mastery states |
| `get_review_queue` | no | Evidence whose `review_after` date passed without newer evidence |
| `get_weekly_review` | no | Last seven days of evidence and rhythm, with a Markdown draft |
| `record_evidence` | `learning-records/*.md` | Append one validated `learning-evidence` block; never changes mastery |
| `set_milestone_state` | `PROGRESS.md` | Change one milestone row; refuses states the linked evidence does not support |
| `sync_progress` | `PROGRESS.md` | Recompute weighted-progress lines, snapshot percentages and the rhythm section |
| `record_checkin` | `.learning-coach/checkins.jsonl` | Attendance only; counts toward rhythm, never mastery |
| `list_checkins` | no | Read attendance events |

All tools share `learning_core.py` (standard library only), which also powers `scripts/learning_lab.py` and the offline HTML view. The server never verifies the learner's source repository; `sourceVerification: not_checked` reminds the coach to do that.

## Launch

Both plugin hosts start the server with [uv](https://docs.astral.sh/uv/), which reads the inline script metadata in `server.py` and provisions Python 3.10+ and `mcp==1.27.0` automatically:

- Codex: `.codex-mcp.json` (declared in `.codex-plugin/plugin.json`), relative to the plugin root.
- Claude Code: `.mcp.json`, using `${CLAUDE_PLUGIN_ROOT}`.

Without uv, a client can run `python -X utf8 mcp/server.py` after `python -m pip install "mcp==1.27.0"`.

## Smoke tests

```bash
python scripts/mcp_demo_smoke.py                      # in-process launch, needs mcp installed
python scripts/mcp_demo_smoke.py --use-config codex   # exactly as Codex launches it, needs uv
python scripts/mcp_demo_smoke.py --use-config claude  # exactly as Claude Code launches it, needs uv
python -X utf8 scripts/codex_mcp_demo_smoke.py        # a real Codex turn; needs Codex authentication
```

The smoke tests use a temporary Learning Lab and never touch a real one.
