#!/usr/bin/env python3
"""Create isolated prompt packets for a selected skill and optional old baseline."""

import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True, help="New directory; existing runs are never replaced")
    parser.add_argument("--baseline", type=Path, help="Old skill directory captured before editing")
    parser.add_argument("--ids", nargs="+", type=int, help="Run packet IDs; default is all eight")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        parser.error("Choose a new output directory to preserve previous evidence.")
    catalog = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
    out.mkdir(parents=True)
    skills = {"with_skill": ROOT / "plugins/ai-learning-coach/skills/learning-coach"}
    if args.baseline:
        skills["old_skill"] = args.baseline.resolve()
    for variant, source in skills.items():
        shutil.copytree(source, out / "skills" / variant)
    for case in catalog["evals"]:
        if args.ids and case["id"] not in args.ids:
            continue
        case_dir = out / ("eval-" + case["name"])
        case_dir.mkdir()
        metadata = {"eval_id": case["id"], "eval_name": case["name"], "prompt": case["prompt"], "assertions": case["assertions"]}
        (case_dir / "eval_metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")
        for variant in skills:
            run = case_dir / variant
            (run / "outputs").mkdir(parents=True)
            prompt = f"Read this skill and relevant references: {(out / 'skills' / variant / 'SKILL.md').as_posix()}\n\nSimulated context:\n{case['context']}\n\nUser:\n{case['prompt']}\n\nReturn the user-facing response and a concise description of any proposed file changes. This is a context-only behavior probe, not a real lesson: do not invent source reads, tool execution or user observations. Do not modify any real learning workspace. Save the response to {(run / 'outputs/response.md').as_posix()}.\n"
            (run / "prompt.txt").write_text(prompt, encoding="utf-8")
    print(out)


if __name__ == "__main__":
    main()
