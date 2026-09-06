import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "plugins/ai-learning-coach/mcp"))
from learning_lab import write_output
from learning_core import get_snapshot
from progress_view import render, share_markdown


class ExportTests(unittest.TestCase):
    def test_force_cannot_overwrite_any_learning_fact(self):
        with tempfile.TemporaryDirectory() as directory:
            lab = Path(directory)
            for name in ("NOTES.md", "PROGRESS.md", "STUDY-PLAN.md", "GLOSSARY.md", "custom-facts.json", "learning-records/a.md"):
                target = lab / name
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text("evidence", encoding="utf-8")
                with self.assertRaises(ValueError):
                    write_output(target, "replacement", lab, True)
                self.assertEqual(target.read_text(), "evidence")
            export = lab / ".learning-coach-exports/progress.html"
            write_output(export, "first", lab, False)
            with self.assertRaises(FileExistsError):
                write_output(export, "second", lab, False)
            write_output(export, "second", lab, True)
            self.assertEqual(export.read_text(), "second")

    def test_html_content_is_escaped_and_offline(self):
        with tempfile.TemporaryDirectory() as directory:
            lab = Path(directory)
            (lab / "MISSION.md").write_text('# Mission: <script>alert(1)</script>', encoding="utf-8")
            snapshot = get_snapshot(directory)
            html = render(snapshot)
            self.assertNotIn("<script>", html)
            self.assertIn("&lt;script&gt;", html)
            self.assertIn("default-src 'none'", html)
            self.assertNotIn('src="http', html)

    def test_share_requires_selected_structured_evidence_and_redacts_local_paths(self):
        data = {"evidence": [{"recordPath": "learning-records/a.md", "observed_at": "2026-09-06", "assistance_level": "guided",
                             "action": "运行 C:/Users/person/private/code.ts", "result": "查看 https://private.example/result", "review_reason": "独立设计待验证"}]}
        with self.assertRaises(ValueError):
            share_markdown(data, "learning-records/b.md")
        text = share_markdown(data, "learning-records/a.md")
        self.assertNotIn("C:/Users", text)
        self.assertNotIn("private.example", text)
        self.assertIn("提示下完成", text)
        self.assertIn("独立设计待验证", text)


if __name__ == "__main__":
    unittest.main()
