#!/usr/bin/env python3
"""Install the local marketplace in an isolated CODEX_HOME and verify the plugin."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "plugins" / "ai-learning-coach" / ".codex-plugin" / "plugin.json"
MARKETPLACE = "ai-learning-coach"
PLUGIN_ID = "ai-learning-coach@ai-learning-coach"


def run_codex(codex: str, args: list[str], env: dict[str, str]) -> str:
    command = [codex, *args]
    printable = subprocess.list2cmdline(command)
    print(f"$ {printable}")

    if os.name == "nt" and codex.lower().endswith((".cmd", ".bat")):
        completed = subprocess.run(
            printable,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            shell=True,
            check=False,
        )
    else:
        completed = subprocess.run(
            command,
            cwd=ROOT,
            env=env,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )

    if completed.stdout.strip():
        print(completed.stdout.strip())
    if completed.stderr.strip():
        print(completed.stderr.strip(), file=sys.stderr)
    if completed.returncode != 0:
        raise RuntimeError(f"Codex command failed with exit code {completed.returncode}: {printable}")
    return completed.stdout


def find_plugin(items: list[object]) -> dict[str, object] | None:
    for item in items:
        if isinstance(item, dict) and item.get("pluginId") == PLUGIN_ID:
            return item
    return None


def main() -> int:
    codex = shutil.which("codex")
    if codex is None:
        print("Codex CLI is not available on PATH.", file=sys.stderr)
        return 1

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest["version"]

    with tempfile.TemporaryDirectory(
        prefix="ai-learning-coach-release-smoke-",
        dir=ROOT.parent,
    ) as home:
        env = os.environ.copy()
        env["CODEX_HOME"] = home

        run_codex(codex, ["plugin", "marketplace", "add", str(ROOT)], env)

        available_output = run_codex(
            codex,
            ["plugin", "list", "--json", "--marketplace", MARKETPLACE, "--available"],
            env,
        )
        available_data = json.loads(available_output)
        available = find_plugin(available_data.get("available", []))
        if available is None or available.get("version") != version:
            raise RuntimeError(f"Expected available plugin {PLUGIN_ID} at version {version}")

        run_codex(codex, ["plugin", "add", PLUGIN_ID], env)

        installed_output = run_codex(codex, ["plugin", "list", "--json"], env)
        installed_data = json.loads(installed_output)
        installed = find_plugin(installed_data.get("installed", []))
        if installed is None:
            raise RuntimeError(f"Installed plugin {PLUGIN_ID} was not listed")
        if installed.get("version") != version or installed.get("enabled") is not True:
            raise RuntimeError(f"Installed plugin {PLUGIN_ID} has unexpected state: {installed}")

        cache_root = (
            Path(home)
            / "plugins"
            / "cache"
            / MARKETPLACE
            / "ai-learning-coach"
            / version
        )
        required_cache_files = (
            cache_root / "skills" / "learning-coach" / "SKILL.md",
            cache_root / "skills" / "learning-coach" / "PROGRESS-FORMAT.md",
            cache_root / "skills" / "focus-coach" / "SKILL.md",
        )
        missing = [str(path) for path in required_cache_files if not path.is_file()]
        if missing:
            raise RuntimeError(f"Installed plugin cache is missing files: {missing}")

    print(f"Release smoke passed: {PLUGIN_ID} {version} installed with both skills.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Release smoke failed: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc
