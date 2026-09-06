#!/usr/bin/env python3
"""Read, check, resume or render a Learning Lab without modifying its facts."""

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/ai-learning-coach/mcp"))
from learning_core import get_resume_context, get_snapshot
from progress_view import render, share_markdown


def write_output(path: Path, content: str, lab: Path, force: bool) -> None:
    path = path.expanduser().resolve()
    if path.is_relative_to(lab) and not path.is_relative_to(lab / ".learning-coach-exports"):
        raise ValueError("Output must not overwrite Learning Lab facts; choose a separate export path.")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w" if force else "x", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("snapshot", "doctor", "resume", "view", "share"))
    parser.add_argument("lab", help="Learning Lab directory")
    parser.add_argument("--as-of", help="YYYY-MM-DD; defaults to local today")
    parser.add_argument("--output", type=Path, help="Required for view/share; no upload or browser launch")
    parser.add_argument("--record", help="Record path relative to the lab, for opt-in share")
    parser.add_argument("--force", action="store_true", help="Replace an existing export, never a fact file")
    args = parser.parse_args()
    try:
        snapshot = get_snapshot(args.lab, args.as_of)
        if args.command in {"view", "share"}:
            if args.output is None or args.command == "share" and not args.record:
                parser.error("view/share need --output; share also needs --record")
            content = render(snapshot) if args.command == "view" else share_markdown(snapshot, args.record)
            write_output(args.output, content, Path(snapshot["labPath"]), args.force)
            print(f"Saved local {args.command}: {args.output.resolve()}")
        else:
            data = get_resume_context(args.lab, args.as_of) if args.command == "resume" else snapshot
            if args.command == "doctor":
                data = {k: snapshot[k] for k in ("status", "asOf", "issues", "sourceVerification")}
            print(json.dumps(data, ensure_ascii=False, indent=2))
            if args.command == "doctor" and snapshot["issues"]:
                return 1
        return 0
    except (OSError, ValueError) as exc:
        print(f"Learning Lab: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
