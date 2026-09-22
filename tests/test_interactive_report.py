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

    def test_report_contains_narrative_sections(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "report.html")
            generator = InteractiveReportGenerator()
            result_path = generator.generate_report(self.sample_records, out_file, "test_search")
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()
            for section in ("Resumen Ejecutivo", "Hallazgos Destacados", "Indicadores de Compromiso",
                            "Metodología y Alcance", "Recomendaciones", "Glosario",
                            "Distribución por Severidad", "Severidad"):
                self.assertIn(section, content)
            # i18n KPI bug fixed: no raw keys rendered
            self.assertNotIn("downloadable_docs", content)
            self.assertNotIn("possible_leaks", content)

    def test_report_escapes_search_term(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "report.html")
            generator = InteractiveReportGenerator()
            result_path = generator.generate_report(self.sample_records, out_file,
                                                    '<script>alert("x")</script>')
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.assertNotIn('<script>alert("x")</script>', content)
            self.assertIn('&lt;script&gt;', content)

    def test_report_html_improvements(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "report.html")
            generator = InteractiveReportGenerator()
            result_path = generator.generate_report(self.sample_records, out_file,
                                                    "test_search", search_id="sid-1")
            with open(result_path, "r", encoding="utf-8") as f:
                content = f.read()
            # Severity filter in table
            self.assertIn('id="severityFilter"', content)
            self.assertIn('record.severity !== severityFilter', content)
            # IOC copy buttons + data
            self.assertIn('class="btn-copy"', content)
            self.assertIn('const iocData =', content)
            self.assertIn('navigator.clipboard', content)
            # TLP banner + doc control + nav
            self.assertIn('TLP:CLEAR', content)
            self.assertIn('Control del Documento', content)
            self.assertIn('sid-1', content)
            self.assertIn('class="toc-nav"', content)
            for anchor in ("sec-resumen", "sec-visual", "sec-hallazgos", "sec-datos",
                           "sec-iocs", "sec-metodo", "sec-recs", "sec-glosario"):
                self.assertIn(f'id="{anchor}"', content)
                self.assertIn(f'href="#{anchor}"', content)
            # Print stylesheet (light theme)
            self.assertIn('@media print', content)
            self.assertIn('.btn-copy', content)

    def test_generate_interactive_html_report_helper(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            out_file = os.path.join(tmpdir, "interactive_report.html")
            res = generate_interactive_html_report(self.sample_records, out_file, "target_term")
            self.assertTrue(os.path.exists(res))

if __name__ == "__main__":
    unittest.main()
