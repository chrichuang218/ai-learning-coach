"""Learning Lab state: Markdown owns facts; tools derive and write them safely. Standard library only."""

from __future__ import annotations

import json
import os
import re
import tempfile
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from urllib.parse import unquote, urlsplit
from uuid import uuid4


STATES = {"未开始": 0, "接触": 25, "需提示": 50, "独立": 75, "迁移验证": 100}
STATE_ALIASES = {"not started": "未开始", "exposed": "接触", "prompted": "需提示", "independent": "独立", "transferred": "迁移验证"}
STATE_EN = {v: k.capitalize() for k, v in STATE_ALIASES.items()}
ASSISTANCE = {"demonstrated", "guided", "independent", "transferred"}
# Evidence and check-ins imply a calendar intensity; this never changes mastery.
ASSISTANCE_LEVEL = {"demonstrated": 2, "guided": 3, "independent": 3, "transferred": 4}
CHECKIN_LEVEL = {"review": 1, "explain": 2, "run": 3, "milestone": 4}
SOURCE_KINDS = {"code": ("path", "symbol", "commit"), "url": ("url",), "document": ("title",), "task": ("description",)}
LEVELS = {"░": 1, "▒": 2, "▓": 3, "█": 4}
MARKS = {v: k for k, v in LEVELS.items()}
LINK = re.compile(r"\[[^\]]*\]\(([^)]+)\)")
EVIDENCE = re.compile(r"^```learning-evidence\s*\n(.*?)^```\s*$", re.M | re.S)
STATE_DIR = ".learning-coach"
LEGACY_STATE_DIR = ".learning-coach-prototype"
CHECKINS_FILE = "checkins.jsonl"

FIELDS = {
    "updated": ("更新日期", "Updated"),
    "mainline": ("当前主线", "Current mainline"),
    "since": ("进度起算日", "Tracking since"),
    "total_days": ("累计有效学习日", "Total learning days"),
    "date": ("日期", "Date"),
}
SECTIONS = {
    "snapshot": ("快照", "Snapshot"),
    "goal": ("目标能力进度", "Goal progress"),
    "rhythm": ("学习节奏", "Rhythm"),
    "eta": ("时间估算", "Estimate"),
    "next": ("下一检查点", "Next checkpoint"),
    "activity": ("最近活动", "Recent activity"),
    "boundary": ("能力边界", "Boundary"),
    "next_entry": ("下一处真实入口", "Next entry"),
}
PROJECT_HEADING = re.compile(r"^##[ \t]+([^\n]*(?:学习范围进度|[Ss]cope [Pp]rogress))[ \t]*$", re.M)
TEXT = {
    "zh": {"goal": "目标能力", "project": "项目学习范围", "raw": "原始加权进度：{raw}；展示进度：{shown}%。",
           "streak": "当前连续学习：{n} 天", "longest": "最长连续学习：{n} 天", "week": "本周有效学习日：{n} 天",
           "total": "累计有效学习日：{n} 天", "week_header": "| ISO 周 | 一 | 二 | 三 | 四 | 五 | 六 | 日 |",
           "legend": "强度：`·` 无有效学习；`░` 回忆、复习或阅读；`▒` 主动解释、预测或源码追踪；`▓` Run、Debug、修改或真实输出；`█` 里程碑、迁移或独立完成。",
           "derived": "<!-- 节奏由状态工具从最近活动、学习证据和打卡派生；手改会在下次同步时被覆盖。 -->",
           "date": "日期"},
    "en": {"goal": "Goal", "project": "Project scope", "raw": "Raw weighted progress: {raw}; shown: {shown}%.",
           "streak": "Current streak: {n} days", "longest": "Longest streak: {n} days", "week": "Learning days this week: {n}",
           "total": "Total learning days: {n}", "week_header": "| ISO week | Mon | Tue | Wed | Thu | Fri | Sat | Sun |",
           "legend": "Intensity: `·` none; `░` recall, review or reading; `▒` explanation, prediction or tracing; `▓` run, debug, edit or real output; `█` milestone, transfer or independent completion.",
           "derived": "<!-- Rhythm is derived by the state tools from recent activity, evidence and check-ins; manual edits are replaced on the next sync. -->",
           "date": "Date"},
}


def resolve_lab(lab_path: str) -> Path:
    lab = Path(lab_path).expanduser().resolve()
    if not lab.is_dir():
        raise ValueError(f"Learning Lab directory does not exist: {lab}")
    return lab


def first_match(pattern: str, text: str) -> str | None:
    match = re.search(pattern, text, re.M)
    return match.group(1).strip() if match else None


def field(text: str, key: str, value: str = r".+") -> str | None:
    names = "|".join(map(re.escape, FIELDS[key]))
    return first_match(rf"^[-*]?[ \t]*(?:{names})[ \t]*[：:][ \t]*({value})[ \t]*$", text)


def markdown_section(text: str, heading: str | tuple[str, ...]) -> str | None:
    headings = (heading,) if isinstance(heading, str) else heading
    names = "|".join(map(re.escape, headings))
    match = re.search(rf"^##[ \t]+(?:{names})[ \t]*\n(.*?)(?=^##\s|\Z)", text, re.M | re.S)
    return match.group(1).strip() if match else None


def section(text: str, key: str) -> str | None:
    return markdown_section(text, SECTIONS[key])


def language(progress: str) -> str:
    return "en" if re.search(r"^[-*]?[ \t]*Updated[ \t]*:", progress, re.M) and "更新日期" not in progress else "zh"


def table_rows(text: str) -> list[list[str]]:
    result = []
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            continue
        cells = [c.strip().strip("`") for c in re.split(r"(?<!\\)\|", line.strip().strip("|"))]
        if cells and not all(re.fullmatch(r":?-+:?", c) for c in cells):
            result.append(cells)
    return result


def parse_state(cell: str) -> tuple[str, int] | None:
    match = re.fullmatch(r"(.+?)\s+(\d+)%", cell.strip())
    if not match:
        return None
    name = match[1].strip()
    name = name if name in STATES else STATE_ALIASES.get(name.lower(), "")
    if not name or int(match[2]) != STATES[name]:
        return None
    return name, STATES[name]


def state_label(state: str, lang: str) -> str:
    return f"{STATE_EN[state] if lang == 'en' else state} {STATES[state]}%"


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
        return date.fromisoformat(value)
    except ValueError:
        return None


def today_or(as_of: str | None) -> date:
    day = parse_day(as_of) if as_of is not None else date.today()
    if day is None:
        raise ValueError("as_of must be YYYY-MM-DD")
    return day


def validate_evidence(data: object) -> None:
    """Raise ValueError when an evidence object cannot be trusted by the state tools."""
    if not isinstance(data, dict) or data.get("schema_version") != 1:
        raise ValueError("expected schema_version 1 object")
    for name in ("id", "observed_at", "milestone_id", "action", "result"):
        if not isinstance(data.get(name), str) or not data[name].strip():
            raise ValueError(f"missing non-empty {name}")
    observed = parse_day(data["observed_at"])
    if observed is None:
        raise ValueError("observed_at must be YYYY-MM-DD")
    if data.get("assistance_level") not in ASSISTANCE:
        raise ValueError("unknown assistance_level")
    source = data.get("source_ref")
    if not isinstance(source, dict):
        raise ValueError("source_ref must be an object")
    kind = source.get("kind", "code" if "commit" in source else None)
    if kind not in SOURCE_KINDS:
        raise ValueError("source_ref.kind must be code, url, document or task")
    if not all(isinstance(source.get(k), str) and source[k].strip() for k in SOURCE_KINDS[kind]):
        raise ValueError(f"{kind} source_ref needs {', '.join(SOURCE_KINDS[kind])}")
    if kind == "code":
        if not re.fullmatch(r"[0-9a-fA-F]{40}", source["commit"]):
            raise ValueError("source_ref.commit must be a full Git commit")
        if urlsplit(source["path"]).scheme or source["path"].startswith(("/", "\\")) or ".." in source["path"].replace("\\", "/").split("/"):
            raise ValueError("source_ref.path must be repository-relative")
    if kind == "url" and urlsplit(source["url"]).scheme not in {"http", "https"}:
        raise ValueError("source_ref.url must be http(s)")
    for name in ("next_action", "review_reason"):
        if name in data and not isinstance(data[name], str):
            raise ValueError(f"{name} must be text")
    if "review_after" in data:
        review = parse_day(data["review_after"]) if isinstance(data["review_after"], str) else None
        if review is None or review < observed:
            raise ValueError("review_after must be YYYY-MM-DD on or after observed_at")


def read_evidence(path: Path, text: str, lab: Path, issues: list[dict]) -> list[dict]:
    items = []
    blocks = EVIDENCE.findall(text)
    relative = path.relative_to(lab).as_posix()
    if len(re.findall(r"^```learning-evidence\s*$", text, re.M)) != len(blocks):
        issue(issues, "invalid_evidence", "unclosed learning-evidence block", relative)
    for block in blocks:
        try:
            data = json.loads(block)
            validate_evidence(data)
            items.append({**data, "recordPath": relative})
        except (ValueError, TypeError) as exc:
            issue(issues, "invalid_evidence", str(exc), relative)
    return items


def project_milestones(progress: str, lab: Path, evidence: list[dict], issues: list[dict]) -> tuple[list[dict], list[dict]]:
    milestones, summaries = [], []
    project_heading = next((m.strip() for m in PROJECT_HEADING.findall(progress)), "项目学习范围进度")
    for headings, label, key in ((SECTIONS["goal"], "目标能力", "goal"), ((project_heading,), "项目学习范围", "project")):
        body = markdown_section(progress, headings)
        if body is None:
            continue
        group = []
        for cells in table_rows(body)[1:]:
            if len(cells) < 5:
                issue(issues, "invalid_milestone", f"{headings[0]}: expected five columns", "PROGRESS.md")
                continue
            weight = re.fullmatch(r"(\d+(?:\.\d+)?)%", cells[1])
            state = parse_state(cells[2])
            if not weight or not state:
                issue(issues, "invalid_milestone", f"{cells[0]}: unsupported weight/state", "PROGRESS.md")
                continue
            paths = []
            for target in LINK.findall(cells[3]):
                linked = local_link(lab / "PROGRESS.md", target, lab)
                if linked and linked.is_file() and linked.is_relative_to(lab / "learning-records"):
                    paths.append(linked.relative_to(lab).as_posix())
            if state[1] > 0 and not paths:
                issue(issues, "missing_mastery_evidence", f"{cells[0]}: link a learning record for this state", "PROGRESS.md")
            matching = [e for e in evidence if e["recordPath"] in paths and e["milestone_id"] == cells[0]]
            # Metadata can reveal a contradiction, but absence in legacy prose is not proof of one.
            if matching and state[1] >= 75:
                latest = max(matching, key=lambda e: e["observed_at"])
                if latest["assistance_level"] not in allowed_assistance(state[1]):
                    issue(issues, "assistance_conflict", f"{cells[0]}: latest evidence is {latest['assistance_level']}, state is {state[0]}", "PROGRESS.md")
            group.append({"scope": label, "scopeKey": key, "name": cells[0], "weight": float(weight[1]), "state": state[0],
                          "value": state[1], "evidencePaths": paths, "nextEvidence": cells[4]})
        milestones.extend(group)
        if group:
            total = sum(r["weight"] for r in group)
            valid = abs(total - 100) < 0.001 and len(group) == len(table_rows(body)) - 1
            if not valid:
                issue(issues, "invalid_weights", f"{headings[0]}: valid weights must total 100 (got {total:g})", "PROGRESS.md")
            raw = sum(r["weight"] * r["value"] for r in group) / 100 if valid else None
            summaries.append({"label": label, "scopeKey": key, "percent": int(raw / 5 + 0.5) * 5 if raw is not None else None,
                              "rawPercent": raw, "basis": "documented_milestones"})
    for cells in table_rows(section(progress, "snapshot") or "")[1:]:
        if len(cells) < 2:
            continue
        value = re.search(r"(?<!\d)(100|\d{1,2})%", cells[1])
        if not value:
            continue
        key = snapshot_key(cells[0])
        label = {"goal": "目标能力", "project": "项目学习范围"}.get(key, cells[0])
        derived = next((s for s in summaries if s["label"] == label), None)
        if derived and derived["percent"] is not None and derived["percent"] != int(value[1]):
            issue(issues, "snapshot_drift", f"{label}: snapshot {value[1]}%, milestones {derived['percent']}%", "PROGRESS.md")
        elif not derived:
            summaries.append({"label": label, "scopeKey": key, "percent": int(value[1]), "rawPercent": None, "basis": "legacy_snapshot"})
    return milestones, summaries


def allowed_assistance(value: int) -> set[str]:
    return {"transferred"} if value == 100 else {"independent", "transferred"} if value == 75 else ASSISTANCE


def snapshot_key(label: str) -> str | None:
    if label in {"目标能力", "Goal"}:
        return "goal"
    if "学习范围" in label or "scope" in label.lower():
        return "project"
    return None


def calendar_weeks(progress: str, issues: list[dict]) -> tuple[dict[date, int], set[date]]:
    days: dict[date, int] = {}
    coverage: set[date] = set()
    for cells in table_rows(section(progress, "rhythm") or ""):
        week = re.fullmatch(r"(\d{4})-W(\d{2})", cells[0])
        if not week:
            continue
        try:
            monday = date.fromisocalendar(int(week[1]), int(week[2]), 1)
            if len(cells) != 8:
                raise ValueError("expected seven weekdays")
            for offset, mark in enumerate(cells[1:]):
                if mark not in {*LEVELS, "·"}:
                    raise ValueError(f"unknown calendar mark {mark}")
                day = monday + timedelta(days=offset)
                coverage.add(day)
                if mark in LEVELS:
                    days[day] = max(days.get(day, 0), LEVELS[mark])
        except ValueError as exc:
            issue(issues, "invalid_calendar", str(exc), "PROGRESS.md")
    return days, coverage


def activity_events(progress: str, evidence: list[dict], checkins: list[dict]) -> dict[date, int]:
    """Positive learning facts: recent-activity rows, evidence and check-ins."""
    days: dict[date, int] = {}

    def add(day: date | None, level: int) -> None:
        if day is not None:
            days[day] = max(days.get(day, 0), level)

    for cells in table_rows(section(progress, "activity") or ""):
        if len(cells) >= 2 and cells[1] in LEVELS:
            add(parse_day(cells[0]), LEVELS[cells[1]])
    for item in evidence:
        add(parse_day(item["observed_at"]), ASSISTANCE_LEVEL[item["assistance_level"]])
    for event in checkins:
        add(parse_day(str(event.get("date"))), CHECKIN_LEVEL.get(str(event.get("level")), 1))
    return days


def streaks(days: dict[date, int], as_of: date) -> tuple[int, int]:
    current, cursor = 0, as_of if as_of in days else as_of - timedelta(days=1)
    while cursor in days:
        current += 1
        cursor -= timedelta(days=1)
    longest = run = 0
    previous = None
    for day in sorted(days):
        run = run + 1 if previous and day - previous == timedelta(days=1) else 1
        longest, previous = max(longest, run), day
    return current, longest


def project_attendance(progress: str, as_of: date, issues: list[dict], evidence: list[dict] | None = None,
                       checkins: list[dict] | None = None) -> dict:
    calendar, coverage = calendar_weeks(progress, issues)
    events = activity_events(progress, evidence or [], checkins or [])
    days = dict(calendar)
    for day, level in events.items():
        if day in coverage and day not in calendar and day <= as_of:
            issue(issues, "calendar_missing_activity", f"calendar shows no learning on {day}, but activity or evidence exists", "PROGRESS.md")
        days[day] = max(days.get(day, 0), level)
    for day in [d for d in days if d > as_of]:
        issue(issues, "future_activity", f"activity on {day} is after {as_of}", "PROGRESS.md")
        del days[day]
    since = parse_day(field(progress, "since", r"\d{4}-\d{2}-\d{2}"))
    # Without a hand-kept calendar, positive facts form the whole log from the start date onward.
    source = "calendar" if coverage else "events"
    if source == "events":
        start = since or min(days, default=as_of)
        coverage = {start + timedelta(days=i) for i in range((as_of - start).days + 1)} if start <= as_of else set()
    rhythm = section(progress, "rhythm") or ""
    names = "|".join(map(re.escape, FIELDS["total_days"]))
    stated = first_match(rf"(?:{names})[ \t]*[：:][ \t]*(\d+)", rhythm)
    complete = since is not None and since <= as_of and sum(since <= d <= as_of for d in coverage) == (as_of - since).days + 1
    if stated and (coverage or days) and ((complete and int(stated) != len(days)) or int(stated) < len(days)):
        issue(issues, "attendance_drift", f"stated {stated} days, activity contains {len(days)} (complete={complete})", "PROGRESS.md")
    old_count = first_match(r"已累计\s*(\d+)\s*个有效学习日", section(progress, "eta") or "")
    if old_count and stated and int(old_count) != int(stated):
        issue(issues, "eta_attendance_drift", f"ETA says {old_count} learning days; rhythm says {stated}", "PROGRESS.md")
    week_start = as_of - timedelta(days=as_of.weekday())
    week_known = source == "events" or all(week_start + timedelta(days=i) in coverage for i in range(as_of.weekday() + 1))
    if source == "calendar" and not week_known:
        issue(issues, "calendar_gap", f"calendar does not cover this week through {as_of}; current rhythm is unknown", "PROGRESS.md")
    current, longest = streaks(days, as_of)
    return {"asOf": as_of.isoformat(), "source": source, "calendarDays": len(days), "calendarComplete": complete,
            "statedTotalDays": int(stated) if stated is not None else None,
            "currentStreak": current if as_of in coverage else None, "longestStreak": longest,
            "thisWeekDays": sum(d >= week_start for d in days) if week_known else None,
            "days": [{"date": d.isoformat(), "level": days[d]} for d in sorted(days)]}


def checkins_path(lab: Path) -> Path:
    return lab / STATE_DIR / CHECKINS_FILE


def load_checkins(lab: Path) -> list[dict]:
    events: list[dict] = []
    for path in (lab / LEGACY_STATE_DIR / CHECKINS_FILE, checkins_path(lab)):
        if not path.is_file():
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                events.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid check-in JSON in {path.name} line {number}: {exc}") from exc
    return events


def review_queue(evidence: list[dict], as_of: date, horizon: int = 7) -> dict:
    """Evidence whose review_after has passed without newer evidence on the same milestone."""
    due, upcoming = [], []
    for item in evidence:
        review = parse_day(item.get("review_after"))
        if review is None:
            continue
        if any(e["id"] != item["id"] and e["milestone_id"] == item["milestone_id"] and e["observed_at"] >= review.isoformat()
               for e in evidence):
            continue
        entry = {"milestoneId": item["milestone_id"], "reviewAfter": review.isoformat(), "evidenceId": item["id"],
                 "recordPath": item["recordPath"], "reason": item.get("review_reason"), "nextAction": item.get("next_action")}
        if review <= as_of:
            due.append({**entry, "overdueDays": (as_of - review).days})
        elif review <= as_of + timedelta(days=horizon):
            upcoming.append(entry)
    due.sort(key=lambda e: (-e["overdueDays"], e["milestoneId"]))
    upcoming.sort(key=lambda e: e["reviewAfter"])
    return {"asOf": as_of.isoformat(), "due": due, "upcoming": upcoming}


def get_snapshot(lab_path: str, as_of: str | None = None) -> dict:
    lab = resolve_lab(lab_path)
    today = today_or(as_of)
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
    if progress and (not field(progress, "mainline") or not section(progress, "next")):
        issue(issues, "incomplete_state", "progress needs current mainline and next checkpoint", "PROGRESS.md")
    updated = parse_day(field(progress, "updated", r"\d{4}-\d{2}-\d{2}"))
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
            header_dates = re.findall(r"\d{4}-\d{2}-\d{2}", field(content, "date") or "")
            records.append({"path": path.relative_to(lab).as_posix(), "title": first_match(r"^#\s+(.+)$", content),
                            "date": max((e["observed_at"] for e in parsed), default=None) or max((d for d in header_dates if parse_day(d)), default=None),
                            "evidenceFormat": "structured" if parsed else "invalid" if "```learning-evidence" in content else "legacy",
                            "boundary": section(content, "boundary"),
                            "nextAction": section(content, "next_entry")})
    ids: set[str] = set()
    for item in evidence:
        if item["id"] in ids:
            issue(issues, "duplicate_evidence", f"duplicate id: {item['id']}", item["recordPath"])
        ids.add(item["id"])
        if item["observed_at"] > today.isoformat():
            issue(issues, "future_evidence", f"evidence is dated {item['observed_at']}", item["recordPath"])
    try:
        checkins = load_checkins(lab)
    except ValueError as exc:
        checkins = []
        issue(issues, "invalid_checkin", str(exc), f"{STATE_DIR}/{CHECKINS_FILE}")
    milestones, summaries = project_milestones(progress, lab, evidence, issues)
    attendance = project_attendance(progress, today, issues, evidence, checkins)
    records.sort(key=lambda r: (r["date"] or "", r["path"]), reverse=True)
    reviews = review_queue(evidence, today)
    return {"schemaVersion": 1, "labPath": str(lab), "scope": "workspace", "asOf": today.isoformat(),
            "language": language(progress),
            "mission": first_match(r"^#\s+(?:Mission:\s*)?(.+)$", docs.get(lab / "MISSION.md", "")),
            "updatedAt": updated.isoformat() if updated else None,
            "currentMainline": field(progress, "mainline"),
            "progress": summaries, "milestones": milestones, "attendance": attendance,
            "nextCheckpoint": section(progress, "next"),
            "learningRecordCount": len(records), "records": records, "evidence": evidence,
            "checkinCount": len(checkins), "reviewDue": reviews["due"], "reviewUpcoming": reviews["upcoming"],
            "issues": issues, "sourceVerification": "not_checked",
            "status": "warning" if issues else "pass"}


def get_resume_context(lab_path: str, as_of: str | None = None) -> dict:
    snapshot = get_snapshot(lab_path, as_of)
    return {"asOf": snapshot["asOf"], "updatedAt": snapshot["updatedAt"],
            "currentMainline": snapshot["currentMainline"], "nextCheckpoint": snapshot["nextCheckpoint"],
            "recentRecords": snapshot["records"][:3], "recentEvidence": sorted(snapshot["evidence"], key=lambda e: e["observed_at"], reverse=True)[:5],
            "reviewDue": snapshot["reviewDue"][:3],
            "issues": snapshot["issues"], "sourceVerification": "not_checked",
            "instruction": "Verify the registered repository, current commit and symbol before resuming. If a review is due, start with one "
                           "unprompted recall or transfer check on it; otherwise use recent evidence to choose one meaningful action. "
                           "Running a supplied test does not prove independent test design."}


def get_review_queue(lab_path: str, as_of: str | None = None) -> dict:
    snapshot = get_snapshot(lab_path, as_of)
    return {"asOf": snapshot["asOf"], "due": snapshot["reviewDue"], "upcoming": snapshot["reviewUpcoming"]}


def get_weekly_review(lab_path: str, as_of: str | None = None) -> dict:
    snapshot = get_snapshot(lab_path, as_of)
    end = date.fromisoformat(snapshot["asOf"])
    start = end - timedelta(days=6)
    week = [e for e in snapshot["evidence"] if start.isoformat() <= e["observed_at"] <= end.isoformat()]
    days = [d for d in snapshot["attendance"]["days"] if d["date"] >= start.isoformat()]
    by_milestone: dict[str, list[dict]] = {}
    for item in sorted(week, key=lambda e: e["observed_at"]):
        by_milestone.setdefault(item["milestone_id"], []).append(item)
    lang = snapshot["language"]
    zh = lang == "zh"
    lines = [f"# 学习周复盘（{start} → {end}）" if zh else f"# Weekly learning review ({start} → {end})", "",
             f"有效学习日：{len(days)} / 7" if zh else f"Learning days: {len(days)} / 7"]
    lines += ["", f"## {'本周证据' if zh else 'Evidence this week'}", ""]
    if not by_milestone:
        lines.append("- 本周没有新的结构化证据。" if zh else "- No new structured evidence this week.")
    for milestone, items in by_milestone.items():
        latest = items[-1]
        lines.append(f"- **{milestone}**：{latest['action']} → {latest['result']}（{latest['assistance_level']}）" if zh
                     else f"- **{milestone}**: {latest['action']} → {latest['result']} ({latest['assistance_level']})")
    lines += ["", f"## {'到期复习' if zh else 'Reviews due'}", ""]
    lines += [f"- {r['milestoneId']}（{r['reviewAfter']}）：{r['reason'] or r['nextAction'] or ''}" for r in snapshot["reviewDue"]] or \
             ["- 暂无。" if zh else "- None."]
    lines += ["", f"## {'下一检查点' if zh else 'Next checkpoint'}", "", snapshot["nextCheckpoint"] or ("待确认" if zh else "Not set"), ""]
    return {"from": start.isoformat(), "to": end.isoformat(), "learningDays": len(days), "evidence": week,
            "milestonesTouched": sorted(by_milestone), "reviewDue": snapshot["reviewDue"],
            "nextCheckpoint": snapshot["nextCheckpoint"], "markdown": "\n".join(lines), "issues": snapshot["issues"]}


# --- Writes. Each one touches a single fact file inside the lab and re-reads the result. ---

def atomic_write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temp = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        os.replace(temp, path)
    except BaseException:
        Path(temp).unlink(missing_ok=True)
        raise


def lab_file(lab: Path, relative: str, under: str, suffix: str = ".md") -> Path:
    if not relative or Path(relative).is_absolute() or ".." in relative.replace("\\", "/").split("/"):
        raise ValueError(f"path must be relative to the Learning Lab and inside {under}/")
    path = (lab / relative).resolve()
    if not path.is_relative_to((lab / under).resolve()) or path.suffix != suffix:
        raise ValueError(f"path must point to a {suffix} file inside {under}/")
    return path


def record_checkin(lab_path: str, checkin_date: str, level: str, note: str, as_of: str | None = None) -> dict:
    lab = resolve_lab(lab_path)
    day = parse_day(checkin_date)
    if day is None:
        raise ValueError("checkin_date must use YYYY-MM-DD")
    if day > today_or(as_of):
        raise ValueError("checkin_date must not be in the future")
    if level not in CHECKIN_LEVEL:
        raise ValueError(f"level must be one of {', '.join(CHECKIN_LEVEL)}")
    normalized = " ".join(note.split())
    if not normalized or len(normalized) > 200:
        raise ValueError("note must contain 1 to 200 characters")
    event = {"schemaVersion": 1, "eventId": str(uuid4()), "eventType": "attendance", "date": checkin_date, "level": level,
             "note": normalized, "source": "learning-lab-mcp", "recordedAt": datetime.now(timezone.utc).isoformat()}
    path = checkins_path(lab)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(event, ensure_ascii=False) + "\n")
    return {"writtenTo": str(path), "event": event, "checkinCount": len(load_checkins(lab)), "masteryChanged": False}


def record_evidence(lab_path: str, record_path: str, evidence: dict, title: str | None = None, as_of: str | None = None) -> dict:
    lab = resolve_lab(lab_path)
    path = lab_file(lab, record_path, "learning-records")
    data = {"schema_version": 1, **evidence}
    validate_evidence(data)
    if data["observed_at"] > today_or(as_of).isoformat():
        raise ValueError("observed_at must not be in the future")
    if any(e["id"] == data["id"] for e in get_snapshot(str(lab), as_of)["evidence"]):
        raise ValueError(f"evidence id already exists: {data['id']}")
    if path.is_file():
        text = path.read_text(encoding="utf-8-sig").rstrip("\n") + "\n"
    else:
        progress = (lab / "PROGRESS.md").read_text(encoding="utf-8-sig") if (lab / "PROGRESS.md").is_file() else ""
        label = TEXT[language(progress)]["date"]
        text = f"# {title or data['milestone_id']}\n\n{label}：{data['observed_at']}\n" if label == "日期" else \
            f"# {title or data['milestone_id']}\n\n{label}: {data['observed_at']}\n"
    text += "\n```learning-evidence\n" + json.dumps(data, ensure_ascii=False, indent=2) + "\n```\n"
    atomic_write(path, text)
    snapshot = get_snapshot(str(lab), as_of)
    return {"writtenTo": str(path), "evidence": data, "masteryChanged": False,
            "issues": [i for i in snapshot["issues"] if i["path"] == path.relative_to(lab).as_posix()]}


def bar(percent: int) -> str:
    return f"`[{'#' * (percent // 5)}{'-' * (20 - percent // 5)}] {percent}%`"


def replace_section(text: str, headings: tuple[str, ...], body: str) -> str:
    names = "|".join(map(re.escape, headings))
    pattern = re.compile(rf"(^##[ \t]+(?:{names})[ \t]*\n)(.*?)(?=^##\s|\Z)", re.M | re.S)
    return pattern.sub(lambda m: m.group(1) + "\n" + body.strip("\n") + "\n\n", text, count=1)


def render_rhythm(attendance: dict, lang: str) -> str:
    t = TEXT[lang]
    days = {date.fromisoformat(d["date"]): d["level"] for d in attendance["days"]}
    as_of = date.fromisoformat(attendance["asOf"])
    lines = [t["derived"], "", f"- {t['streak'].format(n=attendance['currentStreak'] or 0)}",
             f"- {t['longest'].format(n=attendance['longestStreak'])}",
             f"- {t['week'].format(n=attendance['thisWeekDays'] or 0)}", f"- {t['total'].format(n=len(days))}", ""]
    if days:
        lines += [t["week_header"], "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        monday = min(days) - timedelta(days=min(days).weekday())
        while monday <= as_of:
            year, week, _ = monday.isocalendar()
            marks = [MARKS.get(days.get(monday + timedelta(days=i), 0), "·") for i in range(7)]
            lines.append(f"| {year}-W{week:02d} | " + " | ".join(marks) + " |")
            monday += timedelta(days=7)
        lines.append("")
    lines.append(t["legend"])
    return "\n".join(lines)


def sync_progress(lab_path: str, as_of: str | None = None) -> dict:
    """Rewrite only derived numbers in PROGRESS.md: weighted lines, snapshot percentages and rhythm."""
    lab = resolve_lab(lab_path)
    path = lab / "PROGRESS.md"
    if not path.is_file():
        raise ValueError("PROGRESS.md does not exist; create it from PROGRESS-FORMAT.md first")
    snapshot = get_snapshot(str(lab), as_of)
    text = path.read_text(encoding="utf-8-sig")
    lang = snapshot["language"]
    t = TEXT[lang]
    derived = {s["scopeKey"]: s for s in snapshot["progress"] if s["basis"] == "documented_milestones" and s["percent"] is not None}
    project_heading = next((m.strip() for m in PROJECT_HEADING.findall(text)), None)
    for key, headings in (("goal", SECTIONS["goal"]), ("project", (project_heading,) if project_heading else ())):
        if key not in derived or not headings:
            continue
        body = markdown_section(text, headings) or ""
        raw = f"{derived[key]['rawPercent']:g}%"
        line = t["raw"].format(raw=raw, shown=derived[key]["percent"])
        existing = re.compile(r"^(?:原始加权进度|Raw weighted progress)[：:].*$", re.M)
        text = replace_section(text, headings, existing.sub(line, body) if existing.search(body) else body + "\n\n" + line)
    snap = markdown_section(text, SECTIONS["snapshot"])
    if snap is not None:
        rows = []
        for line in snap.splitlines():
            cells = [c.strip() for c in line.strip().strip("|").split("|")] if line.lstrip().startswith("|") else []
            key = snapshot_key(cells[0].strip("`")) if cells else None
            if key in derived and len(cells) >= 2:
                cells[1] = bar(derived[key]["percent"])
                line = "| " + " | ".join(cells) + " |"
            rows.append(line)
        text = replace_section(text, SECTIONS["snapshot"], "\n".join(rows))
    if snapshot["attendance"]["source"] == "events":
        rhythm = render_rhythm(snapshot["attendance"], lang)
        if section(text, "rhythm") is not None:
            text = replace_section(text, SECTIONS["rhythm"], rhythm)
        else:
            text = text.rstrip("\n") + f"\n\n## {SECTIONS['rhythm'][1 if lang == 'en' else 0]}\n\n{rhythm}\n"
    names = "|".join(map(re.escape, FIELDS["updated"]))
    text = re.sub(rf"^((?:{names})[ \t]*[：:][ \t]*)\d{{4}}-\d{{2}}-\d{{2}}", lambda m: m.group(1) + snapshot["asOf"], text, count=1, flags=re.M)
    text = text.rstrip("\n") + "\n"
    changed = text != path.read_text(encoding="utf-8-sig")
    if changed:
        atomic_write(path, text)
    after = get_snapshot(str(lab), as_of)
    return {"changed": changed, "progress": after["progress"], "attendance": {k: v for k, v in after["attendance"].items() if k != "days"},
            "issues": after["issues"], "status": after["status"]}


def set_milestone_state(lab_path: str, milestone: str, state: str, evidence_record: str | None = None,
                        next_evidence: str | None = None, scope: str | None = None, as_of: str | None = None) -> dict:
    """Change one milestone row, refusing states the linked structured evidence does not support."""
    lab = resolve_lab(lab_path)
    canonical = state if state in STATES else STATE_ALIASES.get(state.strip().lower())
    if canonical is None:
        raise ValueError(f"state must be one of {', '.join(STATES)} or {', '.join(STATE_ALIASES)}")
    value = STATES[canonical]
    snapshot = get_snapshot(str(lab), as_of)
    rows = [m for m in snapshot["milestones"] if m["name"] == milestone and (scope is None or m["scopeKey"] == scope)]
    if not rows:
        raise ValueError(f"milestone not found in PROGRESS.md tables: {milestone}")
    if len(rows) > 1:
        raise ValueError("milestone exists in both tables; pass scope='goal' or scope='project'")
    row = rows[0]
    record = None
    if evidence_record:
        record = lab_file(lab, evidence_record, "learning-records")
        if not record.is_file():
            raise ValueError(f"learning record does not exist: {evidence_record}")
    if value > 0 and record is None and not row["evidencePaths"]:
        raise ValueError("a state above 0% needs a linked learning record")
    linked = set(row["evidencePaths"]) | ({record.relative_to(lab).as_posix()} if record else set())
    matching = [e for e in snapshot["evidence"] if e["recordPath"] in linked and e["milestone_id"] == milestone]
    if value >= 75:
        if not matching:
            raise ValueError(f"{canonical} needs structured learning-evidence with milestone_id '{milestone}'")
        latest = max(matching, key=lambda e: e["observed_at"])
        if latest["assistance_level"] not in allowed_assistance(value):
            raise ValueError(f"latest evidence is {latest['assistance_level']}; {canonical} needs {' or '.join(sorted(allowed_assistance(value)))}")
    path = lab / "PROGRESS.md"
    text = path.read_text(encoding="utf-8-sig")
    lines = text.splitlines()
    heading_names = SECTIONS["goal"] if row["scopeKey"] == "goal" else tuple(m.strip() for m in PROJECT_HEADING.findall(text))
    inside = False
    for index, line in enumerate(lines):
        if line.startswith("## "):
            inside = line[3:].strip() in heading_names
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")] if inside and line.lstrip().startswith("|") else []
        if len(cells) >= 5 and cells[0].strip("`") == milestone:
            cells[2] = state_label(canonical, snapshot["language"])
            if record and record.relative_to(lab).as_posix() not in row["evidencePaths"]:
                target = os.path.relpath(record, lab).replace(os.sep, "/")
                link = f"[{first_match(r'^#\s+(.+)$', record.read_text(encoding='utf-8-sig')) or record.stem}]({target})"
                cells[3] = f"{cells[3]}、{link}" if LINK.search(cells[3]) else link
            if next_evidence:
                cells[4] = " ".join(next_evidence.split())
            lines[index] = "| " + " | ".join(cells) + " |"
            break
    atomic_write(path, "\n".join(lines) + "\n")
    result = sync_progress(str(lab), as_of)
    return {"milestone": milestone, "scope": row["scopeKey"], "from": row["state"], "to": canonical, **result}
