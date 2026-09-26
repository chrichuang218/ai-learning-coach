"""Read-only Learning Lab projections. Standard library only; Markdown owns facts."""

from __future__ import annotations

import json
import re
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import unquote, urlsplit


STATES = {"未开始": 0, "接触": 25, "需提示": 50, "独立": 75, "迁移验证": 100}
ASSISTANCE = {"demonstrated", "guided", "independent", "transferred"}
LEVELS = {"░": 1, "▒": 2, "▓": 3, "█": 4}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EVIDENCE = re.compile(r"^```learning-evidence\s*\n(.*?)^```\s*$", re.M | re.S)


def resolve_lab(lab_path: str) -> Path:
    lab = Path(lab_path).expanduser().resolve()
    if not lab.is_dir():
        raise ValueError(f"Learning Lab directory does not exist: {lab}")
    return lab


def first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.M)
    return match.group(1).strip() if match else None


def markdown_section(text: str, heading: str) -> str | None:
    match = re.search(rf"^##\s+{re.escape(heading)}\s*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1).strip() if match else None


def table_rows(section: str) -> list[list[str]]:
    result = []
    for line in section.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if cells and not all(re.fullmatch(r":?-+:?", c) for c in cells):
            result.append(cells)
    return result


def local_link(owner: Path, target: str, lab: Path) -> Path | None:
    target = target.strip("<>").split("#", 1)[0]
    if not target or urlsplit(target).scheme or target.startswith(("/", "\\", "~")):
        return None
    resolved = (owner.parent / unquote(target)).resolve()
    return resolved if resolved.is_relative_to(lab) else None


def issue(issues: list[dict], code: str, message: str, path: str) -> None:
    issues.append({"code": code, "message": message, "path": path})


def parse_day(value: str | None) -> date | None:
    if not value or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
        return None
    try:
        return date.fromisoformat(value or "")
    except ValueError:
        return None


def read_evidence(path: Path, text: str, lab: Path, issues: list[dict]) -> list[dict]:
    items = []
    blocks = EVIDENCE.findall(text)
    if len(re.findall(r"^```learning-evidence\s*$", text, re.M)) != len(blocks):
        issue(issues, "invalid_evidence", "unclosed learning-evidence block", path.relative_to(lab).as_posix())
    for block in blocks:
        relative = path.relative_to(lab).as_posix()
        try:
            data = json.loads(block)
            if not isinstance(data, dict) or data.get("schema_version") != 1:
                raise ValueError("expected schema_version 1 object")
            for field in ("id", "observed_at", "milestone_id", "action", "result"):
                if not isinstance(data.get(field), str) or not data[field].strip():
                    raise ValueError(f"missing non-empty {field}")
            if parse_day(data["observed_at"]) is None:
                raise ValueError("observed_at must be YYYY-MM-DD")
            if data.get("assistance_level") not in ASSISTANCE:
                raise ValueError("unknown assistance_level")
            source = data.get("source_ref")
            if not isinstance(source, dict) or not all(
                isinstance(source.get(k), str) and source[k].strip() for k in ("path", "symbol", "commit")
            ):
                raise ValueError("source_ref needs path, symbol and commit")
            if not re.fullmatch(r"[0-9a-fA-F]{40}", source["commit"]):
                raise ValueError("source_ref.commit must be a full Git commit")
            if urlsplit(source["path"]).scheme or source["path"].startswith(("/", "\\")) or ".." in source["path"].replace("\\", "/").split("/"):
                raise ValueError("source_ref.path must be repository-relative")
            for field in ("next_action", "review_reason"):
                if field in data and not isinstance(data[field], str):
                    raise ValueError(f"{field} must be text")
            items.append({**data, "recordPath": relative})
        except (ValueError, TypeError) as exc:
            issue(issues, "invalid_evidence", str(exc), relative)
    return items


def project_milestones(progress: str, lab: Path, evidence: list[dict], issues: list[dict]) -> tuple[list[dict], list[dict]]:
    milestones, summaries = [], []
    project_heading = next((h.strip() for h in re.findall(r"^##[ \t]+([^\n]*学习范围进度)[ \t]*$", progress, re.M)), "项目学习范围进度")
    for heading, label in (("目标能力进度", "目标能力"), (project_heading, "项目学习范围")):
        section = markdown_section(progress, heading)
        if section is None:
            continue
        group = []
        for cells in table_rows(section)[1:]:
            if len(cells) < 5:
                issue(issues, "invalid_milestone", f"{heading}: expected five columns", "PROGRESS.md")
                continue
            weight = re.fullmatch(r"(\d+(?:\.\d+)?)%", cells[1])
            state = re.fullmatch(r"(未开始|接触|需提示|独立|迁移验证)\s+(\d+)%", cells[2])
            if not weight or not state or int(state[2]) != STATES[state[1]]:
                issue(issues, "invalid_milestone", f"{cells[0]}: unsupported weight/state", "PROGRESS.md")
                continue
            paths = []
            for target in LINK.findall(cells[3]):
                linked = local_link(lab / "PROGRESS.md", target, lab)
                if linked and linked.is_file() and linked.is_relative_to(lab / "learning-records"):
                    paths.append(linked.relative_to(lab).as_posix())
            if int(state[2]) > 0 and not paths:
                issue(issues, "missing_mastery_evidence", f"{cells[0]}: link a learning record for this state", "PROGRESS.md")
            matching = [e for e in evidence if e["recordPath"] in paths and e["milestone_id"] == cells[0]]
            # Metadata can reveal a contradiction, but absence in legacy prose is not proof of one.
            if matching and int(state[2]) >= 75:
                latest = max(matching, key=lambda e: e["observed_at"])
                allowed = {"transferred"} if int(state[2]) == 100 else {"independent", "transferred"}
                if latest["assistance_level"] not in allowed:
                    issue(issues, "assistance_conflict", f"{cells[0]}: latest evidence is {latest['assistance_level']}, state is {state[1]}", "PROGRESS.md")
            row = {"scope": label, "name": cells[0], "weight": float(weight[1]), "state": state[1],
                   "value": int(state[2]), "evidencePaths": paths, "nextEvidence": cells[4]}
            group.append(row)
        milestones.extend(group)
        if group:
            total = sum(r["weight"] for r in group)
            valid = abs(total - 100) < 0.001 and len(group) == len(table_rows(section)) - 1
            if not valid:
                issue(issues, "invalid_weights", f"{heading}: valid weights must total 100 (got {total:g})", "PROGRESS.md")
            raw = sum(r["weight"] * r["value"] for r in group) / 100 if valid else None
            summaries.append({"label": label, "percent": int(raw / 5 + 0.5) * 5 if raw is not None else None,
                              "rawPercent": raw, "basis": "documented_milestones"})
    snapshot = table_rows(markdown_section(progress, "快照") or "")
    for cells in snapshot[1:]:
        if len(cells) < 2:
            continue
        value = re.search(r"(?<!\d)(100|\d{1,2})%", cells[1])
        if not value:
            continue
        label = "目标能力" if cells[0] == "目标能力" else "项目学习范围" if "学习范围" in cells[0] else cells[0]
        derived = next((s for s in summaries if s["label"] == label), None)
        if derived and derived["percent"] is not None and derived["percent"] != int(value[1]):
            issue(issues, "snapshot_drift", f"{label}: snapshot {value[1]}%, milestones {derived['percent']}%", "PROGRESS.md")
        elif not derived:
            summaries.append({"label": label, "percent": int(value[1]), "rawPercent": None, "basis": "legacy_snapshot"})
    return milestones, summaries


def project_attendance(progress: str, as_of: date, issues: list[dict]) -> dict:
    section = markdown_section(progress, "学习节奏") or ""
    days: dict[date, int] = {}
    calendar_start = None
    coverage: set[date] = set()
    for cells in table_rows(section):
        week = re.fullmatch(r"(\d{4})-W(\d{2})", cells[0])
        if not week:
            continue
        try:
            monday = date.fromisocalendar(int(week[1]), int(week[2]), 1)
            if len(cells) != 8:
                raise ValueError("expected seven weekdays")
            calendar_start = min(calendar_start or monday, monday)
            for offset, mark in enumerate(cells[1:]):
                if mark not in {*LEVELS, "·"}:
                    raise ValueError(f"unknown calendar mark {mark}")
                day = monday + timedelta(days=offset)
                coverage.add(day)
                if mark in LEVELS:
                    if day > as_of:
                        issue(issues, "future_activity", f"calendar activity on {day} is after {as_of}", "PROGRESS.md")
                    else:
                        days[day] = max(days.get(day, 0), LEVELS[mark])
        except ValueError as exc:
            issue(issues, "invalid_calendar", str(exc), "PROGRESS.md")
    stated = first_match(r"累计有效学习日：\s*(\d+)\s*天", section)
    since = parse_day(first_match(r"^进度起算日：\s*(\d{4}-\d{2}-\d{2})\s*$", progress))
    complete = since is not None and since <= as_of and sum(since <= d <= as_of for d in coverage) == (as_of - since).days + 1
    if stated and calendar_start and ((complete and int(stated) != len(days)) or int(stated) < len(days)):
        issue(issues, "attendance_drift", f"stated {stated} days, calendar contains {len(days)} (complete={complete})", "PROGRESS.md")
    eta = markdown_section(progress, "时间估算") or ""
    old_count = first_match(r"已累计\s*(\d+)\s*个有效学习日", eta)
    if old_count and stated and int(old_count) != int(stated):
        issue(issues, "eta_attendance_drift", f"ETA says {old_count} learning days; rhythm says {stated}", "PROGRESS.md")
    streak = 0
    cursor = as_of if as_of in days else as_of - timedelta(days=1) if as_of > date.min else None
    while cursor in days:
        streak += 1
        cursor = cursor - timedelta(days=1) if cursor > date.min else None
    week_start = as_of - timedelta(days=as_of.weekday())
    current_known = as_of in coverage
    week_known = all(week_start + timedelta(days=i) in coverage for i in range(as_of.weekday() + 1))
    if calendar_start and not week_known:
        issue(issues, "calendar_gap", f"calendar does not cover this week through {as_of}; current rhythm is unknown", "PROGRESS.md")
    return {"asOf": as_of.isoformat(), "calendarDays": len(days), "calendarComplete": complete,
            "statedTotalDays": int(stated) if stated is not None else None,
            "currentStreak": streak if current_known else None, "thisWeekDays": sum(d >= week_start for d in days) if week_known else None,
            "days": [{"date": d.isoformat(), "level": days[d]} for d in sorted(days)]}


def get_snapshot(lab_path: str, as_of: str | None = None) -> dict:
    lab = resolve_lab(lab_path)
    today = parse_day(as_of) if as_of is not None else date.today()
    if today is None:
        raise ValueError("as_of must be YYYY-MM-DD")
    issues: list[dict] = []
    docs: dict[Path, str] = {}
    paths = [lab / name for name in ("MISSION.md", "PROGRESS.md", "README.md")]
    paths += sorted((lab / "learning-records").rglob("*.md"))
    paths += sorted((lab / "sources").rglob("*.md"))
    for path in paths:
        if not path.resolve().is_relative_to(lab):
            issue(issues, "external_file", "file resolves outside Learning Lab", path.relative_to(lab).as_posix())
            continue
        if not path.is_file():
            if path.name in {"MISSION.md", "PROGRESS.md"}:
                issue(issues, "missing_file", f"missing {path.name}", path.name)
            continue
        try:
            docs[path] = path.read_text(encoding="utf-8-sig")
        except (OSError, UnicodeError) as exc:
            issue(issues, "unreadable_file", str(exc), path.relative_to(lab).as_posix())
    progress = docs.get(lab / "PROGRESS.md", "")
    if progress and (not first_match(r"^当前主线：[ \t]*(.+)$", progress) or not markdown_section(progress, "下一检查点")):
        issue(issues, "incomplete_state", "progress needs current mainline and next checkpoint", "PROGRESS.md")
    updated = parse_day(first_match(r"^更新日期：\s*(\d{4}-\d{2}-\d{2})\s*$", progress))
    if progress and updated is None:
        issue(issues, "invalid_update_date", "missing or invalid update date", "PROGRESS.md")
    if updated and updated > today:
        issue(issues, "future_update", f"update date {updated} is after {today}", "PROGRESS.md")
    planned = first_match(r"下一次学习会话计划从\s*\*\*(\d{4}-\d{2}-\d{2})", docs.get(lab / "README.md", ""))
    if planned and updated and planned < updated.isoformat():
        issue(issues, "stale_readme", f"next-session date {planned} precedes progress {updated}", "README.md")
    records, evidence = [], []
    for path, content in docs.items():
        for target in LINK.findall(content):
            linked = local_link(path, target, lab)
            if linked is not None and not linked.is_file():
                issue(issues, "broken_link", f"missing local target: {target}", path.relative_to(lab).as_posix())
        if path.is_relative_to(lab / "learning-records"):
            parsed = read_evidence(path, content, lab, issues)
            evidence.extend(parsed)
            header_dates = re.findall(r"\d{4}-\d{2}-\d{2}", first_match(r"^日期：[ \t]*(.+)$", content) or "")
            records.append({"path": path.relative_to(lab).as_posix(), "title": first_match(r"^#\s+(.+)$", content),
                            "date": max((e["observed_at"] for e in parsed), default=None) or max((d for d in header_dates if parse_day(d)), default=None),
                            "evidenceFormat": "structured" if parsed else "invalid" if "```learning-evidence" in content else "legacy",
                            "boundary": markdown_section(content, "能力边界"),
                            "nextAction": markdown_section(content, "下一处真实入口")})
    ids: set[str] = set()
    for item in evidence:
        if item["id"] in ids:
            issue(issues, "duplicate_evidence", f"duplicate id: {item['id']}", item["recordPath"])
        ids.add(item["id"])
        if item["observed_at"] > today.isoformat():
            issue(issues, "future_evidence", f"evidence is dated {item['observed_at']}", item["recordPath"])
    milestones, summaries = project_milestones(progress, lab, evidence, issues)
    attendance = project_attendance(progress, today, issues)
    records.sort(key=lambda r: (r["date"] or "", r["path"]), reverse=True)
    return {"schemaVersion": 1, "labPath": str(lab), "scope": "workspace", "asOf": today.isoformat(),
            "mission": first_match(r"^#\s+(?:Mission:\s*)?(.+)$", docs.get(lab / "MISSION.md", "")),
            "updatedAt": updated.isoformat() if updated else None,
            "currentMainline": first_match(r"^当前主线：\s*(.+)$", progress),
            "progress": summaries, "milestones": milestones, "attendance": attendance,
            "nextCheckpoint": markdown_section(progress, "下一检查点"),
            "learningRecordCount": len(records), "records": records, "evidence": evidence,
            "issues": issues, "sourceVerification": "not_checked",
            "status": "warning" if issues else "pass"}


def get_resume_context(lab_path: str, as_of: str | None = None) -> dict:
    snapshot = get_snapshot(lab_path, as_of)
    return {"asOf": snapshot["asOf"], "updatedAt": snapshot["updatedAt"],
            "currentMainline": snapshot["currentMainline"], "nextCheckpoint": snapshot["nextCheckpoint"],
            "recentRecords": snapshot["records"][:3], "recentEvidence": sorted(snapshot["evidence"], key=lambda e: e["observed_at"], reverse=True)[:5],
            "issues": snapshot["issues"], "sourceVerification": "not_checked",
            "instruction": "Verify the registered repository, current commit and symbol before resuming. Use recent evidence to choose one meaningful action; running a supplied test does not prove independent test design."}
