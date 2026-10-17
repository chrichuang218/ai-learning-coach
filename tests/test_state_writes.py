import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "plugins/ai-learning-coach/mcp"))
from learning_core import (get_resume_context, get_review_queue, get_snapshot, get_weekly_review, record_checkin,
                           record_evidence, set_milestone_state, sync_progress)


PROGRESS = """# Learning Progress

更新日期：2026-09-01
当前主线：真实缓存链路
进度起算日：2026-09-01

## 快照

| 维度 | 进度 | 当前判断 |
| --- | --- | --- |
| 目标能力 | `[--------------------] 0%` | 刚开始 |

## 目标能力进度

| 里程碑 | 权重 | 掌握状态 | 当前证据 | 下一次升级证据 |
| --- | ---: | --- | --- | --- |
| 缓存失效 | 60% | 未开始 0% | 尚无证据 | 解释缓存为何过期 |
| 异步顺序 | 40% | 未开始 0% | 尚无证据 | 预测日志顺序 |

原始加权进度：0%；展示进度：0%。

## 最近活动

| 日期 | 强度 | 真实动作 | 关联记录 |
| --- | --- | --- | --- |
| 2026-09-02 | `░` | 复习缓存笔记 | 无 |

## 下一检查点

- 运行缓存测试并解释结果。
"""

ENGLISH = """# Learning Progress

Updated: 2026-09-01
Current mainline: Cache invalidation
Tracking since: 2026-09-01

## Goal progress

| Milestone | Weight | State | Evidence | Next evidence |
| --- | ---: | --- | --- | --- |
| Cache | 100% | Prompted 50% | [run](learning-records/run.md) | Design a new test alone |

## Next checkpoint

- Predict the second discovery call.
"""


def evidence(**updates):
    data = {"id": "cache-1", "observed_at": "2026-09-03", "milestone_id": "缓存失效", "action": "运行提供的测试",
            "assistance_level": "guided", "result": "Green", "source_ref": {"commit": "a" * 40, "path": "src/cache.ts", "symbol": "reset"}}
    data.update(updates)
    return data


class StateWriteTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.lab = Path(self.temp.name)
        (self.lab / "MISSION.md").write_text("# Mission: 学会缓存\n", encoding="utf-8")
        (self.lab / "PROGRESS.md").write_text(PROGRESS, encoding="utf-8")

    def progress(self):
        return (self.lab / "PROGRESS.md").read_text(encoding="utf-8")

    def test_events_mode_derives_rhythm_from_activity_evidence_and_checkins(self):
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(), as_of="2026-09-04")
        record_checkin(str(self.lab), "2026-09-04", "explain", "解释了缓存键", as_of="2026-09-04")
        attendance = get_snapshot(str(self.lab), "2026-09-04")["attendance"]
        self.assertEqual(attendance["source"], "events")
        self.assertEqual([d["date"] for d in attendance["days"]], ["2026-09-02", "2026-09-03", "2026-09-04"])
        self.assertEqual(attendance["currentStreak"], 3)
        self.assertEqual(attendance["thisWeekDays"], 3)

    def test_record_evidence_validates_and_never_changes_mastery(self):
        result = record_evidence(str(self.lab), "learning-records/cache.md", evidence(), title="缓存观察", as_of="2026-09-04")
        self.assertFalse(result["masteryChanged"])
        text = (self.lab / "learning-records/cache.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("# 缓存观察\n\n日期：2026-09-03"))
        self.assertIn("未开始 0%", self.progress())
        with self.assertRaises(ValueError):
            record_evidence(str(self.lab), "learning-records/cache.md", evidence(), as_of="2026-09-04")
        with self.assertRaises(ValueError):
            record_evidence(str(self.lab), "../outside.md", evidence(id="x"), as_of="2026-09-04")
        with self.assertRaises(ValueError):
            record_evidence(str(self.lab), "learning-records/cache.md", evidence(id="y", observed_at="2026-12-01"), as_of="2026-09-04")

    def test_non_code_evidence_kinds_are_valid(self):
        for index, source in enumerate(({"kind": "url", "url": "https://example.com/essay"},
                                        {"kind": "document", "title": "雅思写作 Task 2 第 3 稿"},
                                        {"kind": "task", "description": "独立完成一次口语模拟"})):
            record_evidence(str(self.lab), "learning-records/other.md", evidence(id=f"n{index}", source_ref=source), as_of="2026-09-04")
        snapshot = get_snapshot(str(self.lab), "2026-09-04")
        self.assertEqual(len(snapshot["evidence"]), 3)
        with self.assertRaises(ValueError):
            record_evidence(str(self.lab), "learning-records/other.md", evidence(id="bad", source_ref={"title": "无 kind"}), as_of="2026-09-04")

    def test_milestone_state_requires_supporting_evidence(self):
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(), as_of="2026-09-04")
        with self.assertRaises(ValueError):
            set_milestone_state(str(self.lab), "缓存失效", "需提示")
        with self.assertRaises(ValueError):
            set_milestone_state(str(self.lab), "缓存失效", "独立", "learning-records/cache.md", as_of="2026-09-04")
        result = set_milestone_state(str(self.lab), "缓存失效", "需提示", "learning-records/cache.md", "独立设计反向测试", as_of="2026-09-04")
        self.assertEqual(result["progress"][0]["percent"], 30)
        text = self.progress()
        self.assertIn("| 缓存失效 | 60% | 需提示 50% | [缓存失效](learning-records/cache.md) | 独立设计反向测试 |", text)
        self.assertIn("`[######--------------] 30%`", text)
        self.assertIn("原始加权进度：30%；展示进度：30%。", text)
        self.assertEqual(result["status"], "pass", result["issues"])

    def test_independent_state_accepts_independent_evidence(self):
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(id="i", assistance_level="independent"), as_of="2026-09-04")
        result = set_milestone_state(str(self.lab), "缓存失效", "independent", "learning-records/cache.md", as_of="2026-09-04")
        self.assertEqual(result["to"], "独立")
        with self.assertRaises(ValueError):
            set_milestone_state(str(self.lab), "缓存失效", "迁移验证", as_of="2026-09-04")

    def test_sync_is_idempotent_and_writes_rhythm(self):
        first = sync_progress(str(self.lab), "2026-09-04")
        self.assertTrue(first["changed"])
        self.assertIn("累计有效学习日：1 天", self.progress())
        self.assertIn("| 2026-W36 | · | · | ░ | · | · | · | · |", self.progress())
        self.assertFalse(sync_progress(str(self.lab), "2026-09-04")["changed"])
        self.assertEqual(get_snapshot(str(self.lab), "2026-09-04")["status"], "pass")

    def test_review_queue_surfaces_due_items_until_newer_evidence(self):
        record_evidence(str(self.lab), "learning-records/cache.md",
                        evidence(review_after="2026-09-05", review_reason="不看提示重建缓存时间线"), as_of="2026-09-04")
        self.assertEqual(get_review_queue(str(self.lab), "2026-09-04")["upcoming"][0]["milestoneId"], "缓存失效")
        due = get_resume_context(str(self.lab), "2026-09-07")["reviewDue"]
        self.assertEqual(due[0]["overdueDays"], 2)
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(id="cache-2", observed_at="2026-09-07"), as_of="2026-09-07")
        self.assertEqual(get_review_queue(str(self.lab), "2026-09-07")["due"], [])
        with self.assertRaises(ValueError):
            record_evidence(str(self.lab), "learning-records/cache.md", evidence(id="z", review_after="2026-09-01"), as_of="2026-09-07")

    def test_weekly_review_summarizes_only_the_last_seven_days(self):
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(id="old", observed_at="2026-08-20"), as_of="2026-09-04")
        record_evidence(str(self.lab), "learning-records/cache.md", evidence(), as_of="2026-09-04")
        review = get_weekly_review(str(self.lab), "2026-09-04")
        self.assertEqual([e["id"] for e in review["evidence"]], ["cache-1"])
        self.assertIn("# 学习周复盘", review["markdown"])
        self.assertIn("运行缓存测试", review["markdown"])

    def test_english_lab_is_parsed_and_written_in_english(self):
        (self.lab / "PROGRESS.md").write_text(ENGLISH, encoding="utf-8")
        record_evidence(str(self.lab), "learning-records/run.md",
                        evidence(id="en", milestone_id="Cache", source_ref={"kind": "task", "description": "Run the cache test"}),
                        title="Cache run", as_of="2026-09-04")
        snapshot = get_snapshot(str(self.lab), "2026-09-04")
        self.assertEqual(snapshot["language"], "en")
        self.assertEqual(snapshot["currentMainline"], "Cache invalidation")
        self.assertEqual(snapshot["progress"][0]["percent"], 50)
        self.assertIn("Predict", snapshot["nextCheckpoint"])
        self.assertTrue((self.lab / "learning-records/run.md").read_text(encoding="utf-8").startswith("# Cache run\n\nDate: 2026-09-03"))
        sync_progress(str(self.lab), "2026-09-04")
        text = self.progress()
        self.assertIn("Raw weighted progress: 50%; shown: 50%.", text)
        self.assertIn("Total learning days: 1", text)
        self.assertIn("Updated: 2026-09-04", text)
        self.assertEqual(get_snapshot(str(self.lab), "2026-09-04")["status"], "pass")

    def test_future_checkin_is_rejected(self):
        with self.assertRaises(ValueError):
            record_checkin(str(self.lab), "2026-10-01", "run", "未来", as_of="2026-09-04")

    def test_legacy_prototype_checkins_still_count(self):
        legacy = self.lab / ".learning-coach-prototype/checkins.jsonl"
        legacy.parent.mkdir()
        legacy.write_text(json.dumps({"date": "2026-09-03", "level": "run"}) + "\n", encoding="utf-8")
        self.assertEqual(get_snapshot(str(self.lab), "2026-09-04")["checkinCount"], 1)


if __name__ == "__main__":
    unittest.main()
