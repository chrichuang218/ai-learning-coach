import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/ai-learning-coach/mcp"))
from learning_core import get_resume_context, get_snapshot


PROGRESS = """# Learning Progress
更新日期：2026-09-01
进度起算日：2026-09-01
当前主线：真实缓存链路

## 快照
| 维度 | 进度 |
| --- | --- |
| 目标能力 | 50% |

## 目标能力进度
| 里程碑 | 权重 | 掌握状态 | 当前证据 | 下一次升级证据 |
| --- | --- | --- | --- | --- |
| 缓存失效 | 100% | 需提示 50% | [记录](learning-records/ts/one.md) | 独立设计新场景测试 |

## 时间估算
缺少可靠时长，待校准。

## 学习节奏
- 累计有效学习日：1 天
| ISO 周 | 一 | 二 | 三 | 四 | 五 | 六 | 日 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 2026-W36 | · | ▓ | · | · | · | · | · |

## 下一检查点
- 修改已有 Skill，独立预测缓存读取结果。
"""


def evidence(**updates):
    data = {"schema_version": 1, "id": "cache-one", "observed_at": "2026-09-01", "milestone_id": "缓存失效",
            "action": "运行提供的测试", "assistance_level": "guided", "result": "目标 Green，独立设计待验证",
            "source_ref": {"commit": "a" * 40, "path": "src/skills.ts", "symbol": "resetSkillCache"},
            "review_reason": "尚未独立设计反向测试"}
    data.update(updates)
    return "# 缓存观察\n日期：2026-09-01\n\n```learning-evidence\n" + json.dumps(data, ensure_ascii=False) + "\n```\n"


class LearningCoreTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name)
        self.write("MISSION.md", "# Mission: 从真实代码学习\n")
        self.write("README.md", "# 工作区\n[当前状态](PROGRESS.md)\n")
        self.write("PROGRESS.md", PROGRESS)
        self.write("learning-records/ts/one.md", evidence())

    def write(self, path, content):
        target = self.lab / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")

    def snapshot(self, day="2026-09-06"):
        return get_snapshot(str(self.lab), day)

    def codes(self, result):
        return {i["code"] for i in result["issues"]}

    def test_projection_is_repeatable_read_only_and_counts_nested_records(self):
        before = {p.relative_to(self.lab): p.read_bytes() for p in self.lab.rglob("*") if p.is_file()}
        snapshot = self.snapshot()
        self.assertEqual(snapshot, self.snapshot())
        self.assertEqual(snapshot["status"], "pass")
        self.assertEqual(snapshot["learningRecordCount"], 1)
        self.assertEqual(snapshot["progress"][0]["percent"], 50)
        self.assertEqual(before, {p.relative_to(self.lab): p.read_bytes() for p in self.lab.rglob("*") if p.is_file()})

    def test_legacy_snapshot_never_uses_milestone_weight_as_progress(self):
        text = PROGRESS.split("## 快照")[0] + PROGRESS.split("## 目标能力进度")[1]
        self.write("PROGRESS.md", text)
        self.assertEqual(self.snapshot()["progress"], [])
        self.write("PROGRESS.md", "更新日期：2026-09-01\n## 快照\n| 维度 | 进度 |\n| --- | --- |\n| 目标能力 | 60% |\n")
        self.assertEqual(self.snapshot()["progress"][0]["basis"], "legacy_snapshot")

    def test_detects_real_readme_and_eta_drift(self):
        self.write("README.md", "下一次学习会话计划从 **2026-07-13 的新第 1 课**开始。")
        self.write("PROGRESS.md", PROGRESS.replace("缺少可靠时长，待校准。", "已累计 3 个有效学习日，缺少可靠时长。"))
        self.assertTrue({"stale_readme", "eta_attendance_drift"} <= self.codes(self.snapshot()))

    def test_guided_test_run_cannot_support_independent_state(self):
        self.write("PROGRESS.md", PROGRESS.replace("需提示 50%", "独立 75%"))
        self.assertTrue({"assistance_conflict", "snapshot_drift"} <= self.codes(self.snapshot()))

    def test_latest_guided_evidence_overrides_old_independent_evidence_for_warning(self):
        self.write("learning-records/ts/old.md", evidence(id="old", observed_at="2026-08-01", assistance_level="independent"))
        self.write("PROGRESS.md", PROGRESS.replace("[记录](learning-records/ts/one.md)", "[旧](learning-records/ts/old.md)、[新](learning-records/ts/one.md)").replace("需提示 50%", "独立 75%"))
        self.assertIn("assistance_conflict", self.codes(self.snapshot()))

    def test_bad_weights_do_not_produce_confident_percentage(self):
        self.write("PROGRESS.md", PROGRESS.replace("100% | 需提示", "20% | 需提示"))
        result = self.snapshot()
        self.assertIsNone(result["progress"][0]["percent"])
        self.assertIn("invalid_weights", self.codes(result))

    def test_missing_record_is_diagnosed_and_not_treated_as_evidence(self):
        (self.lab / "learning-records/ts/one.md").unlink()
        self.assertTrue({"broken_link", "missing_mastery_evidence"} <= self.codes(self.snapshot()))

    def test_legacy_records_are_preserved_without_invented_assistance(self):
        self.write("learning-records/ts/one.md", "# 旧证据\n日期：2026-09-01\n## 能力边界\n独立设计尚未证明\n")
        result = self.snapshot()
        self.assertEqual(result["evidence"], [])
        self.assertEqual(result["records"][0]["evidenceFormat"], "legacy")
        self.assertIn("尚未证明", result["records"][0]["boundary"])

    def test_invalid_json_and_duplicate_ids_are_diagnosed(self):
        self.write("learning-records/bad.md", "```learning-evidence\n[]\n```\n")
        self.write("learning-records/duplicate.md", evidence())
        self.assertTrue({"invalid_evidence", "duplicate_evidence"} <= self.codes(self.snapshot()))

    def test_empty_lab_reports_missing_files(self):
        with tempfile.TemporaryDirectory() as empty:
            self.assertEqual(self.codes(get_snapshot(empty)), {"missing_file"})

    def test_attendance_changes_rhythm_but_not_mastery(self):
        before = self.snapshot()
        self.write("PROGRESS.md", PROGRESS.replace("1 天", "2 天").replace("· | ▓ | · |", "· | ▓ | ░ |"))
        after = self.snapshot()
        self.assertEqual(before["progress"], after["progress"])
        self.assertEqual(after["attendance"]["calendarDays"], 2)
        self.assertEqual(after["attendance"]["currentStreak"], 0)

    def test_calendar_window_does_not_erase_older_attendance(self):
        self.write("PROGRESS.md", PROGRESS.replace("进度起算日：2026-09-01", "进度起算日：2026-01-01").replace("1 天", "16 天"))
        result = self.snapshot()
        self.assertFalse(result["attendance"]["calendarComplete"])
        self.assertNotIn("attendance_drift", self.codes(result))

    def test_invalid_date_and_calendar_are_visible(self):
        self.write("PROGRESS.md", PROGRESS.replace("更新日期：2026-09-01", "更新日期：2026-02-30").replace("2026-W36", "2026-W99"))
        self.assertTrue({"invalid_update_date", "invalid_calendar"} <= self.codes(self.snapshot()))
        with self.assertRaises(ValueError):
            self.snapshot("tomorrow")

    def test_resume_preserves_boundary_and_requires_code_verification(self):
        resume = get_resume_context(str(self.lab), "2026-09-06")
        self.assertIn("修改已有", resume["nextCheckpoint"])
        self.assertEqual(resume["recentEvidence"][0]["assistance_level"], "guided")
        self.assertEqual(resume["sourceVerification"], "not_checked")

    def test_future_evidence_is_not_silently_accepted(self):
        self.write("learning-records/ts/one.md", evidence(observed_at="2027-01-01"))
        self.assertIn("future_evidence", self.codes(self.snapshot()))

    def test_unclosed_evidence_is_invalid_not_legacy(self):
        self.write("learning-records/ts/one.md", "# Record\n```learning-evidence\n{bad json\n")
        result = self.snapshot()
        self.assertIn("invalid_evidence", self.codes(result))
        self.assertEqual(result["records"][0]["evidenceFormat"], "invalid")

    def test_missing_current_week_is_unknown_not_zero(self):
        self.write("PROGRESS.md", PROGRESS.replace("2026-W36", "2026-W01").replace("进度起算日：2026-09-01", "进度起算日：2026-01-01"))
        result = self.snapshot()
        self.assertFalse(result["attendance"]["calendarComplete"])
        self.assertIsNone(result["attendance"]["thisWeekDays"])
        self.assertIsNone(result["attendance"]["currentStreak"])
        self.assertIn("calendar_gap", self.codes(result))

    def test_incomplete_progress_does_not_pass_health_check(self):
        self.write("PROGRESS.md", "更新日期：2026-09-01\n")
        self.assertIn("incomplete_state", self.codes(self.snapshot()))

    def test_compact_date_is_not_accepted_as_iso_day(self):
        self.write("learning-records/ts/one.md", evidence(observed_at="20260101"))
        self.assertIn("invalid_evidence", self.codes(self.snapshot()))

    def test_named_project_scope_and_amended_record_date(self):
        self.write("PROGRESS.md", PROGRESS.replace("目标能力进度", "mini-claude 学习范围进度"))
        self.write("learning-records/ts/one.md", "# 旧记录\n日期：2026-08-07（2026-09-01 复验）\n")
        result = self.snapshot()
        self.assertEqual(result["milestones"][0]["scope"], "项目学习范围")
        self.assertEqual(result["records"][0]["date"], "2026-09-01")


if __name__ == "__main__":
    unittest.main()
