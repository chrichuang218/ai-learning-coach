#!/usr/bin/env python3
"""Run behavior evals end to end: an agent CLI answers each scenario with the skill, then a judge grades the assertions.

The agent and judge commands read the prompt on stdin and print the reply on stdout, e.g.
  codex exec --skip-git-repo-check --sandbox read-only --color never -
  claude -p
Results land in a new directory using the same grading.json layout as evals/results/2026-09-06.
"""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins/ai-learning-coach/skills/learning-coach/SKILL.md"
DEFAULT_CMD = "codex exec --skip-git-repo-check --sandbox read-only --color never -"

JUDGE = """You grade one reply from an AI learning coach. Judge only what the reply says or proposes; do not reward intentions it does not state.

Scenario context:
{context}

User message:
{prompt}

Coach reply:
<<<
{response}
>>>

For each assertion, decide passed true/false and quote at most 30 words of the reply as evidence.
Assertions:
{assertions}

Return only JSON: {{"expectations": [{{"text": "...", "passed": true, "evidence": "..."}}]}}"""


def run(command: str, prompt: str, timeout: int) -> str:
    completed = subprocess.run(shlex.split(command, posix=sys.platform != "win32"), input=prompt, capture_output=True, text=True,
                               encoding="utf-8", errors="replace", timeout=timeout, cwd=ROOT, check=False,
                               shell=sys.platform == "win32")
    if completed.returncode != 0:
        raise RuntimeError(f"command failed ({completed.returncode}): {completed.stderr.strip()[-500:]}")
    return completed.stdout.strip()


def parse_grading(text: str, assertions: list[str]) -> list[dict]:
    match = re.search(r"\{.*\}", text, re.S)
    try:
        items = json.loads(match.group(0))["expectations"] if match else None
    except (json.JSONDecodeError, KeyError, TypeError):
        items = None
    if not isinstance(items, list) or len(items) != len(assertions):
        return [{"text": a, "passed": False, "evidence": "judge output could not be parsed"} for a in assertions]
    return [{"text": a, "passed": item.get("passed") is True, "evidence": str(item.get("evidence", ""))[:300]}
            for a, item in zip(assertions, items)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--agent-cmd", default=DEFAULT_CMD, help="Command that answers a scenario (prompt on stdin)")
    parser.add_argument("--judge-cmd", help="Command that grades replies; defaults to --agent-cmd")
    parser.add_argument("--output", type=Path, default=ROOT / "evals/results" / f"{date.today()}-auto")
    parser.add_argument("--ids", nargs="+", type=int, help="Scenario IDs; default is all")
    parser.add_argument("--min-pass-rate", type=float, default=0.8, help="Exit 1 below this overall assertion pass rate")
    parser.add_argument("--timeout", type=int, default=600, help="Seconds per command")
    args = parser.parse_args()
    out = args.output.resolve()
    if out.exists():
        parser.error(f"{out} exists; choose a new directory to preserve previous evidence")
    catalog = json.loads((ROOT / "evals/scenarios.json").read_text(encoding="utf-8"))
    cases = [c for c in catalog["evals"] if not args.ids or c["id"] in args.ids]
    skill_text = SKILL.read_text(encoding="utf-8")
    summary = []
    for case in cases:
        run_dir = out / f"eval-{case['name']}" / "with_skill"
        (run_dir / "outputs").mkdir(parents=True)
        # Inline SKILL.md so a sandbox that cannot spawn file readers still sees the skill; references stay readable by path.
        prompt = (f"You are running with this skill (references live next to {SKILL.as_posix()}):\n<<<SKILL\n{skill_text}\nSKILL>>>\n\n"
                  f"Simulated context:\n{case['context']}\n\n"
                  f"User:\n{case['prompt']}\n\nReply exactly as the coach would to the user, then add a short section describing any "
                  "file or tool writes you would make. This is a context-only probe: do not claim source reads, tool runs or user "
                  "observations that the context does not give, and do not modify any files.")
        try:
            response = run(args.agent_cmd, prompt, args.timeout)
            graded = parse_grading(run(args.judge_cmd or args.agent_cmd, JUDGE.format(
                context=case["context"], prompt=case["prompt"], response=response,
                assertions="\n".join(f"- {a}" for a in case["assertions"])), args.timeout), case["assertions"])
        except (RuntimeError, subprocess.TimeoutExpired) as exc:
            response = f"ERROR: {exc}"
            graded = [{"text": a, "passed": False, "evidence": "run failed"} for a in case["assertions"]]
        (run_dir / "outputs/response.md").write_text(response + "\n", encoding="utf-8")
        passed = sum(g["passed"] for g in graded)
        grading = {"expectations": graded, "summary": {"passed": passed, "failed": len(graded) - passed, "total": len(graded),
                                                        "pass_rate": round(passed / len(graded), 3)}}
        (run_dir / "grading.json").write_text(json.dumps(grading, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary.append({"id": case["id"], "name": case["name"], **grading["summary"]})
        print(f"[{passed}/{len(graded)}] {case['name']}")
    total = sum(s["total"] for s in summary)
    rate = sum(s["passed"] for s in summary) / total if total else 0.0
    (out / "benchmark.json").write_text(json.dumps({"date": str(date.today()), "agent": args.agent_cmd, "judge": args.judge_cmd or args.agent_cmd,
                                                    "pass_rate": round(rate, 3), "cases": summary}, ensure_ascii=False, indent=2) + "\n",
                                        encoding="utf-8")
    print(f"Overall pass rate {rate:.0%} ({out})")
    return 0 if rate >= args.min_pass_rate else 1


if __name__ == "__main__":
    raise SystemExit(main())
