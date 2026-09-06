# Learning Lab MCP Prototype

This throwaway, no-UI prototype answers one question:

> Can Codex read structured learning state from a local Learning Lab, append an isolated check-in event, and read the updated state back through a bundled MCP server?

It exposes five tools:

- `get_learning_snapshot`
- `record_checkin`
- `list_checkins`
- `doctor_learning_lab`
- `get_resume_context`

Snapshot, health and resume tools share the standard-library `learning_core.py` reader. It preserves legacy Markdown, recursively finds multitrack records, derives weighted progress, and reports date, attendance, link and assistance conflicts. It does not verify the source repository; the coach must do that before resuming.

The same reader powers the offline CLI and HTML view: see [Learning Lab tools](../../../docs/learning-lab.md).

`record_checkin` writes only to `.learning-coach-prototype/checkins.jsonl` inside the selected Learning Lab. It never edits `MISSION.md`, `PROGRESS.md`, `learning-records/`, or mastery values.

## Prerequisite

```powershell
python -m pip install "mcp==1.27.0"
```

## Protocol smoke test

```powershell
python -X utf8 scripts/mcp_demo_smoke.py
```

## Real Codex smoke test

After reinstalling the local plugin, run:

```powershell
python -X utf8 scripts/codex_mcp_demo_smoke.py
```

The real smoke uses a temporary Learning Lab, requires Codex authentication, and deletes the temporary directory after validation.

## Prototype boundary

- No UI.
- No production schema migration.
- No mastery writes.
- No direct changes to the user's real Learning Lab during automated smoke tests.
- The shared reader and pinned MCP dependency are included; check-in writing remains an isolated prototype and is not merged into attendance or mastery.
