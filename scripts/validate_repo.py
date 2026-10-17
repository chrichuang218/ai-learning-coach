#!/usr/bin/env python3
"""Validate plugin manifests, skill metadata, links, and v2 contracts."""

from __future__ import annotations

import json
import re
import sys
import subprocess
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "ai-learning-coach"
SKILLS_ROOT = PLUGIN_ROOT / "skills"
SKILLS = ("learning-coach", "focus-coach")
REQUIRED_FILES = (
    "plugins/ai-learning-coach/skills/learning-coach/LESSONS.md",
    "plugins/ai-learning-coach/skills/learning-coach/COACHING-MODES.md",
    "plugins/ai-learning-coach/skills/learning-coach/LEARNING-SCIENCE.md",
    "plugins/ai-learning-coach/skills/learning-coach/REFERENCE-FORMAT.md",
    "plugins/ai-learning-coach/skills/learning-coach/LEARNER-BACKGROUND-FORMAT.md",
    "plugins/ai-learning-coach/skills/learning-coach/PROGRESS-FORMAT.md",
    "plugins/ai-learning-coach/.mcp.json",
    "plugins/ai-learning-coach/.codex-mcp.json",
    "plugins/ai-learning-coach/.claude-plugin/plugin.json",
    ".claude-plugin/marketplace.json",
    "plugins/ai-learning-coach/mcp/server.py",
    "plugins/ai-learning-coach/skills/learning-coach/STARTER-TRACKS.md",
    "plugins/ai-learning-coach/mcp/README.md",
    "plugins/ai-learning-coach/mcp/learning_core.py",
    "plugins/ai-learning-coach/mcp/progress_view.py",
    "plugins/ai-learning-coach/skills/learning-coach/RESUME.md",
    "plugins/ai-learning-coach/skills/learning-coach/EVIDENCE-FORMAT.md",
    "examples/first-session/README.md",
    "scripts/first_session.py",
    "scripts/learning_lab.py",
    "examples/workspaces/minimal-multitrack/PROGRESS.md",
    "examples/workspaces/minimal-multitrack/learning-records/typescript-agent/ts-agent-0000-foundation-baseline.md",
    "scripts/release_smoke.py",
    "evals/release-checklist.md",
    "evals/learning-coach-smoke-prompts.md",
    "evals/cross-domain-smoke-prompts.md",
    "evals/focus-coach-smoke-prompts.md",
)
FORBIDDEN_IN_LEARNING_SKILL = (
    "30-90 分钟",
    "小课是主要交付物",
    "每次练习必须包含",
    "`exercises/`",
)
NO_EXERCISE_PATH_DOCS = (
    "plugins/ai-learning-coach/skills/learning-coach/WORKSPACE-FORMAT.md",
    "plugins/ai-learning-coach/skills/learning-coach/TRACKS-FORMAT.md",
    "plugins/ai-learning-coach/skills/learning-coach/LESSONS.md",
    "README.md",
)


def repository_files() -> list[Path]:
    """Honor ignored verification runs and dependency caches, including new source files."""
    result = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard", "-z"],
                            cwd=ROOT, capture_output=True, check=True)
    return [ROOT / name for name in result.stdout.decode("utf-8").split("\0") if name and (ROOT / name).is_file()]


def read_yaml(path: Path, errors: list[str]) -> object | None:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, yaml.YAMLError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid YAML: {exc}")
        return None


def read_json(path: Path, errors: list[str]) -> object | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(ROOT)}: invalid JSON: {exc}")
        return None


def validate_skill(skill_name: str, errors: list[str]) -> None:
    skill_dir = SKILLS_ROOT / skill_name
    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"{skill_name}: SKILL.md is missing")
        return

    content = skill_file.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", content, re.DOTALL)
    if not match:
        errors.append(f"{skill_name}: invalid YAML frontmatter")
        return

    try:
        metadata = yaml.safe_load(match.group(1))
    except yaml.YAMLError as exc:
        errors.append(f"{skill_name}: invalid frontmatter YAML: {exc}")
        return

    if not isinstance(metadata, dict):
        errors.append(f"{skill_name}: frontmatter must be a mapping")
        return
    if metadata.get("name") != skill_name:
        errors.append(f"{skill_name}: frontmatter name must match directory")
    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{skill_name}: description is required")
    elif len(description) > 1024:
        errors.append(f"{skill_name}: description exceeds 1024 characters")

    line_count = len(content.splitlines())
    if line_count > 500:
        errors.append(f"{skill_name}: SKILL.md has {line_count} lines; keep it under 500")

    agent_file = skill_dir / "agents" / "openai.yaml"
    agent = read_yaml(agent_file, errors)
    if isinstance(agent, dict):
        interface = agent.get("interface")
        if not isinstance(interface, dict):
            errors.append(f"{skill_name}: agents/openai.yaml needs interface mapping")
        else:
            short_description = interface.get("short_description")
            if not isinstance(short_description, str) or not 25 <= len(short_description) <= 64:
                errors.append(
                    f"{skill_name}: short_description must contain 25 to 64 characters",
                )
        policy = agent.get("policy")
        if not isinstance(policy, dict) or policy.get("allow_implicit_invocation") is not True:
            errors.append(f"{skill_name}: implicit invocation must be enabled")

    for reference in skill_dir.glob("*.md"):
        if reference.name == "SKILL.md":
            continue
        reference_content = reference.read_text(encoding="utf-8")
        if len(reference_content.splitlines()) > 100 and "## 目录" not in reference_content:
            errors.append(f"{skill_name}/{reference.name}: references over 100 lines need a TOC")


def validate_plugin_manifests(errors: list[str]) -> None:
    manifest_path = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
    manifest = read_json(manifest_path, errors)
    if isinstance(manifest, dict):
        if manifest.get("name") != "ai-learning-coach":
            errors.append("plugin.json: name must be ai-learning-coach")
        version = manifest.get("version")
        if not isinstance(version, str) or not re.fullmatch(
            r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?(?:\+[0-9A-Za-z.-]+)?",
            version,
        ):
            errors.append("plugin.json: version must be valid SemVer")
        else:
            changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
            release_version = version.split("+", 1)[0]
            release_heading = rf"^## {re.escape(release_version)} - \d{{4}}-\d{{2}}-\d{{2}}$"
            if not re.search(release_heading, changelog, re.MULTILINE):
                errors.append(
                    f"CHANGELOG.md: missing dated release heading for {release_version}",
                )
        if manifest.get("skills") != "./skills/":
            errors.append("plugin.json: skills must point to ./skills/")
        # Codex reads only the declared file; Claude Code auto-loads .mcp.json with ${CLAUDE_PLUGIN_ROOT}.
        if manifest.get("mcpServers") != "./.codex-mcp.json":
            errors.append("plugin.json: mcpServers must point to ./.codex-mcp.json")
        for name, needle in ((".codex-mcp.json", "mcp/server.py"), (".mcp.json", "${CLAUDE_PLUGIN_ROOT}/mcp/server.py")):
            mcp_config = read_json(PLUGIN_ROOT / name, errors)
            servers = mcp_config.get("mcpServers") if isinstance(mcp_config, dict) else None
            if not isinstance(servers, dict) or set(servers) != {"learning-lab"}:
                errors.append(f"{name}: expected exactly the learning-lab server")
            elif servers["learning-lab"].get("command") != "uv" or needle not in servers["learning-lab"].get("args", []):
                errors.append(f"{name}: learning-lab must launch {needle} through uv")

        claude_manifest = read_json(PLUGIN_ROOT / ".claude-plugin" / "plugin.json", errors)
        if isinstance(claude_manifest, dict):
            if claude_manifest.get("name") != "ai-learning-coach" or claude_manifest.get("version") != version:
                errors.append(".claude-plugin/plugin.json: name and version must match the Codex manifest")
        claude_marketplace = read_json(ROOT / ".claude-plugin" / "marketplace.json", errors)
        if isinstance(claude_marketplace, dict):
            entries = claude_marketplace.get("plugins")
            if not isinstance(entries, list) or [p.get("source") for p in entries if isinstance(p, dict)] != ["./plugins/ai-learning-coach"]:
                errors.append(".claude-plugin/marketplace.json: expected one plugin sourced from ./plugins/ai-learning-coach")

        interface = manifest.get("interface")
        if not isinstance(interface, dict):
            errors.append("plugin.json: interface mapping is required")
        else:
            prompts = interface.get("defaultPrompt")
            if not isinstance(prompts, list) or not 1 <= len(prompts) <= 3:
                errors.append("plugin.json: defaultPrompt must contain 1 to 3 prompts")
            elif any(not isinstance(item, str) or len(item) > 128 for item in prompts):
                errors.append("plugin.json: every defaultPrompt must be a string up to 128 characters")

    marketplace_path = ROOT / ".agents" / "plugins" / "marketplace.json"
    marketplace = read_json(marketplace_path, errors)
    if not isinstance(marketplace, dict):
        return
    if marketplace.get("name") != "ai-learning-coach":
        errors.append("marketplace.json: name must be ai-learning-coach")

    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append("marketplace.json: exactly one plugin entry is required")
        return

    plugin = plugins[0]
    if not isinstance(plugin, dict) or plugin.get("name") != "ai-learning-coach":
        errors.append("marketplace.json: plugin name must be ai-learning-coach")
        return
    if plugin.get("source") != {
        "source": "local",
        "path": "./plugins/ai-learning-coach",
    }:
        errors.append("marketplace.json: plugin source path is invalid")
    if plugin.get("policy") != {
        "installation": "AVAILABLE",
        "authentication": "ON_INSTALL",
    }:
        errors.append("marketplace.json: plugin policy is invalid")


def validate_markdown_links(errors: list[str]) -> None:
    link_pattern = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
    ignored_prefixes = ("http://", "https://", "mailto:", "#", "~/")

    for path in (p for p in repository_files() if p.suffix == ".md"):
        content = path.read_text(encoding="utf-8")
        for target in link_pattern.findall(content):
            target = target.strip().strip("<>")
            if not target or target.startswith(ignored_prefixes) or target.startswith("{"):
                continue
            target = target.split("#", 1)[0]
            if re.match(r"^[A-Za-z]:[\\/]", target):
                continue
            resolved = (path.parent / target).resolve()
            if not resolved.exists():
                errors.append(
                    f"{path.relative_to(ROOT)}: broken local link -> {target}",
                )


def validate_contracts(errors: list[str]) -> None:
    for relative in REQUIRED_FILES:
        if not (ROOT / relative).exists():
            errors.append(f"required file missing: {relative}")

    learning_skill = (SKILLS_ROOT / "learning-coach" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    for phrase in FORBIDDEN_IN_LEARNING_SKILL:
        if phrase in learning_skill:
            errors.append(f"learning-coach/SKILL.md contains legacy rule: {phrase}")

    for relative in NO_EXERCISE_PATH_DOCS:
        content = (ROOT / relative).read_text(encoding="utf-8")
        if "exercises/" in content:
            errors.append(f"{relative} contains legacy exercises directory")

    promotion_contracts = {
        "SKILL.md": (
            "每次创建或更新 learning record 后",
            "记录总数本身不能作为创建理由",
            "优先更新已有 reference",
        ),
        "LEARNING-RECORD-FORMAT.md": (
            "## Reference 状态",
            "候选主题和缺失证据",
        ),
        "REFERENCE-FORMAT.md": (
            "## Promotion 检查",
            "不要要求两类文件数量一一对应",
            "仓库相对路径",
        ),
    }
    for filename, phrases in promotion_contracts.items():
        content = (SKILLS_ROOT / "learning-coach" / filename).read_text(encoding="utf-8")
        for phrase in phrases:
            if phrase not in content:
                errors.append(f"learning-coach/{filename} missing promotion contract: {phrase}")


def validate_progress_contract(errors: list[str]) -> None:
    progress_format = (
        SKILLS_ROOT / "learning-coach" / "PROGRESS-FORMAT.md"
    ).read_text(encoding="utf-8")
    required_rules = (
        "出勤不等于掌握",
        "目标能力进度",
        "项目学习范围进度",
        "sum(权重 x 掌握状态) / 100",
        "少于 3 个有效学习日",
    )
    for phrase in required_rules:
        if phrase not in progress_format:
            errors.append(f"PROGRESS-FORMAT.md missing contract: {phrase}")

    example = (
        ROOT / "examples" / "workspaces" / "minimal-multitrack" / "PROGRESS.md"
    ).read_text(encoding="utf-8")
    for heading in ("## 目标能力进度", "## 项目学习范围进度", "## 学习节奏"):
        if heading not in example:
            errors.append(f"example PROGRESS.md missing section: {heading}")
    for line in example.splitlines():
        if re.search(r"\| (?:接触|需提示|独立|迁移验证) \d+% \|", line):
            if "learning-records/" not in line:
                errors.append(f"example PROGRESS.md has unsupported mastery row: {line}")

    learning_skill = (SKILLS_ROOT / "learning-coach" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    focus_skill = (SKILLS_ROOT / "focus-coach" / "SKILL.md").read_text(
        encoding="utf-8"
    )
    if "只有低强度出勤时只更新 progress" not in learning_skill:
        errors.append("learning-coach must keep attendance-only activity out of learning records")
    if "不代替 `learning-coach` 做日常进度维护" not in focus_skill:
        errors.append("focus-coach must not own daily progress maintenance")
    if "## 何时触发" in focus_skill:
        errors.append("focus-coach trigger rules must live in frontmatter, not a duplicate body section")


def validate_release_contract(errors: list[str]) -> None:
    source = (
        ROOT / "examples" / "workspaces" / "minimal-multitrack" / "sources" / "mini-claude.md"
    ).read_text(encoding="utf-8")
    for field in ("- URL：", "- 本机路径：", "- 版本：", "- 核验日期：", "## 启动方式"):
        if field not in source:
            errors.append(f"example mini-claude source missing field: {field}")

    readme = (ROOT / "docs" / "install.md").read_text(encoding="utf-8")
    expected_list_command = "codex plugin list --json --marketplace ai-learning-coach --available"
    if expected_list_command not in readme:
        errors.append("docs/install.md: marketplace list smoke must use --json with --available")

    checklist = (ROOT / "evals" / "release-checklist.md").read_text(encoding="utf-8")
    version = json.loads((PLUGIN_ROOT / ".codex-plugin/plugin.json").read_text(encoding="utf-8"))["version"].split("+", 1)[0]
    if "-" in version:
        # A development candidate can be validated without pretending its human release gate passed.
        return
    if f"当前候选版本：`{version}`" not in checklist:
        errors.append("evals/release-checklist.md: stable release must have matching acceptance version")
    if "状态：PASS" not in checklist or "待执行" in checklist:
        errors.append("evals/release-checklist.md: release acceptance is not complete")


def validate_trailing_whitespace(errors: list[str]) -> None:
    checked_suffixes = {".json", ".md", ".py", ".yaml", ".yml"}
    for path in repository_files():
        if not path.is_file() or path.suffix not in checked_suffixes:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if line.endswith((" ", "\t")):
                errors.append(f"{path.relative_to(ROOT)}:{number}: trailing whitespace")


def main() -> int:
    errors: list[str] = []
    validate_plugin_manifests(errors)
    for skill in SKILLS:
        validate_skill(skill, errors)
    validate_markdown_links(errors)
    validate_contracts(errors)
    validate_progress_contract(errors)
    validate_release_contract(errors)
    validate_trailing_whitespace(errors)

    if errors:
        print("Validation failed:")
        for item in errors:
            print(f"- {item}")
        return 1

    print(
        "Validation passed: plugin manifests, 2 skills, metadata, links, "
        "progress and release contracts, and whitespace are valid."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
