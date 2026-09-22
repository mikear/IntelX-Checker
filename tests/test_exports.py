import unittest
import os
import tempfile
import json
import csv
from exports import (export_to_csv, export_to_json, export_to_interactive_html,
                     generate_pdf_report)

class TestExports(unittest.TestCase):
    def setUp(self):
        self.sample_records = [
            {
                "systemid": "sys-01",
                "name": "Leak File 1",
                "bucket": "leaks",
                "media": 1,
                "date": "2024-01-01 12:00:00",
                "score": 90
            },
            {
                "systemid": "sys-02",
                "name": "Paste File 2",
                "bucket": "pastes",
                "media": 2,
                "date": "2024-02-01 12:00:00",
                "score": 30
            }
        ]

    def test_export_to_csv(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "test.csv")
            res = export_to_csv(self.sample_records, out_file)
            self.assertTrue(os.path.exists(res))
            with open(res, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                rows = list(reader)
            self.assertGreater(len(rows), 1)
            self.assertEqual(rows[1][0], "sys-01")

    def test_export_to_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "test.json")
            res = export_to_json(self.sample_records, out_file)
            self.assertTrue(os.path.exists(res))
            with open(res, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.assertEqual(len(data), 2)

    def test_export_to_interactive_html(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "test.html")
            res = export_to_interactive_html(self.sample_records, out_file, search_term="test_query")
            self.assertTrue(os.path.exists(res))

    def test_generate_pdf_report(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = generate_pdf_report(self.sample_records, title="IntelX Test",
                                      exports_dir=tmpdir, search_term="test_query",
                                      search_id="sid-test")
            self.assertTrue(os.path.exists(res))
            self.assertTrue(res.endswith(".pdf"))
            self.assertGreater(os.path.getsize(res), 5000)
            with open(res, "rb") as f:
                raw = f.read()
            self.assertEqual(raw[:5], b"%PDF-")
            import re
            pages = len(re.findall(rb"/Type\s*/Page[^s]", raw))
            self.assertGreaterEqual(pages, 3)  # portada + índice + contenido
            self.assertIn("IntelX Checker".encode("latin-1"), raw)

    def test_generate_pdf_report_empty(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res = generate_pdf_report([], title="IntelX Empty",
                                      exports_dir=tmpdir, search_term="nothing.xyz")
            self.assertTrue(os.path.exists(res))
            with open(res, "rb") as f:
                self.assertEqual(f.read(5), b"%PDF-")

    def test_generate_pdf_report_charts_empty(self):
        from pdf_report import _severity_drawing, _sources_drawing
        self.assertIsNone(_severity_drawing({k: 0 for k in
                                             ("critical", "high", "medium", "low", "unknown")}))
        self.assertIsNone(_sources_drawing([]))

    def test_export_sanitized_filenames(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            res_csv = export_to_csv(self.sample_records, filename="user@domain.com/test", exports_dir=tmpdir)
            self.assertTrue(os.path.exists(res_csv))
            self.assertIn("user_at_domain_dot_comtest", os.path.basename(res_csv))
            self.assertTrue(res_csv.endswith(".csv"))

            res_json = export_to_json(self.sample_records, filename="user@domain.com/test", exports_dir=tmpdir)
            self.assertTrue(os.path.exists(res_json))
            self.assertIn("user_at_domain_dot_comtest", os.path.basename(res_json))
            self.assertTrue(res_json.endswith(".json"))

if __name__ == "__main__":
    unittest.main()
