import unittest
from analysis import analyze_results_for_report, extract_iocs, clean_data_for_mandiant_report, prepare_mandiant_chart_data

class TestAnalysis(unittest.TestCase):
    def setUp(self):
        self.sample_data = [
            {
                "systemid": "1",
                "name": "Leak DB 2024",
                "bucket": "leaks",
                "media": 1,
                "date": "2024-01-15T12:00:00",
                "added": "2024-01-15T12:00:00",
                "score": 100,
                "detail": "user@example.com connected to 192.168.1.1 and https://malicious.test"
            },
            {
                "systemid": "2",
                "name": "Pastebin Entry",
                "bucket": "pastes",
                "media": 2,
                "date": "2024-02-10T10:30:00",
                "added": "2024-02-10T10:30:00",
                "score": 50,
                "detail": "test@test.org admin@domain.com"
            },
            {
                "systemid": "3",
                "name": "unknown",
                "bucket": "",
                "media": 0
            }
        ]

    def test_extract_iocs(self):
        iocs = extract_iocs(self.sample_data)
        self.assertIn("user@example.com", iocs["emails"])
        self.assertIn("192.168.1.1", iocs["ips"])
        self.assertIn("https://malicious.test", iocs["urls"])

    def test_analyze_results_for_report(self):
        analysis = analyze_results_for_report(self.sample_data)
        self.assertEqual(analysis["total_records"], 3)
        self.assertEqual(analysis["source_distribution"]["leaks"], 1)
        self.assertEqual(analysis["source_distribution"]["pastes"], 1)

    def test_clean_data_for_mandiant_report(self):
        cleaned = clean_data_for_mandiant_report(self.sample_data)
        self.assertEqual(len(cleaned), 2)
        names = [item["name"] for item in cleaned]
        self.assertNotIn("unknown", names)

    def test_prepare_mandiant_chart_data(self):
        cleaned = clean_data_for_mandiant_report(self.sample_data)
        chart_data = prepare_mandiant_chart_data(cleaned, {})
        self.assertEqual(chart_data["total_records"], 2)
        self.assertEqual(chart_data["sources"]["leaks"], 1)

if __name__ == "__main__":
    unittest.main()
