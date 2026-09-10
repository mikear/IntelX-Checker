import unittest
import os
import tempfile
import json
from interactive_report import InteractiveReportGenerator, generate_interactive_html_report

class TestInteractiveReport(unittest.TestCase):
    def setUp(self):
        self.sample_records = [
            {
                "systemid": "1111-2222-3333-4444",
                "name": "Database Leak 2023.txt",
                "bucket": "leaks",
                "media": 1,
                "date": "2023-05-10 14:00:00",
                "added": "2023-05-10 14:00:00",
                "score": 80
            },
            {
                "systemid": "5555-6666-7777-8888",
                "name": "Pastebin Dump",
                "bucket": "pastes",
                "media": 2,
                "date": "2024-01-20 09:15:00",
                "added": "2024-01-20 09:15:00",
                "score": 40
            }
        ]

    def test_generate_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "report.html")
            generator = InteractiveReportGenerator()
            result_path = generator.generate_report(self.sample_records, out_file, "test_search")

            self.assertTrue(os.path.exists(result_path))
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()

            self.assertIn("<html", content.lower())
            self.assertIn("test_search", content)
            self.assertIn("Database Leak 2023.txt", content)
            self.assertIn("<svg", content)

    def test_generate_interactive_html_report_helper(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "interactive_report.html")
            res = generate_interactive_html_report(self.sample_records, out_file, "target_term")
            self.assertTrue(os.path.exists(res))

if __name__ == "__main__":
    unittest.main()
