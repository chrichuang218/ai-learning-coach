#!/usr/bin/env python3
"""Prepare a new, isolated real-source checkout or verify the pinned cache test."""

import argparse
import shutil
import subprocess
import sys
from pathlib import Path

REPOSITORY = "https://github.com/chrichuang218/claude-code-from-scratch.git"
COMMIT = "bdb7e858ff9be8fbed82d0488e13a63b9b0e3288"
TEST_NAME = "^cache reset makes a newly created skill discoverable$"


def run(args: list[str], cwd: Path) -> str:
    print("$ " + subprocess.list2cmdline(args), flush=True)
    result = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=600)
    if result.stdout:
        print(result.stdout, end="", flush=True)
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr, flush=True)
    if result.returncode:
        raise RuntimeError(f"Command failed (exit {result.returncode}). Keep the checkout to diagnose; nothing was reset.")
    return result.stdout.strip()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("prepare", "check"))
    parser.add_argument("source", type=Path, help="Independent source directory; prepare requires a NEW path")
    args = parser.parse_args()
    source = args.source.expanduser().resolve()
    try:
        git, node = shutil.which("git"), shutil.which("node")
        if not git or not node:
            raise ValueError("Install Git and Node.js 24 first.")
        if args.command == "prepare":
            if source.exists():
                raise ValueError("prepare requires a new directory. Existing checkouts are never replaced; use check to verify.")
            source.parent.mkdir(parents=True, exist_ok=True)
            run([git, "clone", "--no-checkout", REPOSITORY, str(source)], source.parent)
            run([git, "checkout", "--detach", COMMIT], source)
            # Use npm's JS entry point when installed with Node, avoiding shell-built commands.
            npm = shutil.which("npm.cmd" if sys.platform == "win32" else "npm")
            if not npm:
                raise ValueError("npm is not on PATH; install dependencies in this checkout before check.")
            npm_cli = Path(npm).resolve().parent / "node_modules/npm/bin/npm-cli.js"
            npm_args = [node, str(npm_cli)] if npm_cli.is_file() else [npm]
            run([*npm_args, "ci", "--ignore-scripts", "--no-audit", "--no-fund"], source)
        if not source.is_dir():
            raise ValueError("Source directory does not exist. Use prepare with a new path.")
        head = run([git, "rev-parse", "HEAD"], source)
        if head != COMMIT:
            raise ValueError(f"Expected {COMMIT}; got {head}. No branch changes were made.")
        if not (source / "node_modules/typescript/bin/tsc").is_file():
            raise ValueError("Missing TypeScript. Run npm ci --ignore-scripts --no-audit --no-fund in the source checkout.")
        run([node, "node_modules/typescript/bin/tsc", "-p", "tsconfig.test.json"], source)
        run([node, "--test", f"--test-name-pattern={TEST_NAME}", "dist-test/test/skills.test.js"], source)
        print("Environment verified. This test result is not learner mastery evidence.")
        print("Start with test/skills.test.ts and src/skills.ts; ask your coach for one prediction before explanation.")
        return 0
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as exc:
        print(f"First session: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
