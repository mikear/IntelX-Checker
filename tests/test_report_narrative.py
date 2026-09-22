import unittest
from report_narrative import (
    compute_severity, severity_counts, severity_label,
    score_of, build_executive_summary, top_findings,
    collect_iocs, build_recommendations, build_methodology,
    get_glossary, build_report_narrative, escape_html,
    SEVERITY_CRITICAL, SEVERITY_HIGH, SEVERITY_MEDIUM,
    SEVERITY_LOW, SEVERITY_UNKNOWN,
)


def _rec(name, **kw):
    base = {"systemid": "id-" + name, "name": name, "bucket": "leaks",
            "media": 15, "date": "2024-03-10 12:00:00", "xscore": 0}
    base.update(kw)
    return base


class TestSeverity(unittest.TestCase):
    def test_thresholds(self):
        self.assertEqual(compute_severity(_rec("a", xscore=95)), SEVERITY_CRITICAL)
        self.assertEqual(compute_severity(_rec("a", xscore=80)), SEVERITY_CRITICAL)
        self.assertEqual(compute_severity(_rec("a", xscore=79)), SEVERITY_HIGH)
        self.assertEqual(compute_severity(_rec("a", xscore=50)), SEVERITY_HIGH)
        self.assertEqual(compute_severity(_rec("a", xscore=20)), SEVERITY_MEDIUM)
        self.assertEqual(compute_severity(_rec("a", xscore=1)), SEVERITY_LOW)
        self.assertEqual(compute_severity(_rec("a", xscore=0)), SEVERITY_UNKNOWN)
        self.assertEqual(compute_severity(_rec("a")), SEVERITY_UNKNOWN)

    def test_score_fallback(self):
        # fixtures with `score` instead of `xscore` must work too
        self.assertEqual(score_of({"score": 80}), 80)
        self.assertEqual(score_of({"xscore": 0, "score": 40}), 40)
        self.assertEqual(compute_severity({"score": 90}), SEVERITY_CRITICAL)
        self.assertEqual(score_of({}), 0)
        self.assertEqual(score_of(None), 0)

    def test_counts_all_keys(self):
        counts = severity_counts([_rec("a", xscore=90), _rec("b", xscore=10), _rec("c")])
        self.assertEqual(counts[SEVERITY_CRITICAL], 1)
        self.assertEqual(counts[SEVERITY_LOW], 1)
        self.assertEqual(counts[SEVERITY_UNKNOWN], 1)
        self.assertEqual(counts[SEVERITY_HIGH], 0)
        self.assertEqual(counts[SEVERITY_MEDIUM], 0)

    def test_labels(self):
        self.assertEqual(severity_label("critical", "es"), "Crítica")
        self.assertEqual(severity_label("critical", "en"), "Critical")
        self.assertEqual(severity_label("unknown", "es"), "Sin datos")


class TestSummary(unittest.TestCase):
    def test_summary_with_results(self):
        records = [_rec("db.sql", xscore=90), _rec("paste.txt", bucket="pastes", xscore=30)]
        paragraphs = build_executive_summary(records, "example.com", "es")
        self.assertGreaterEqual(len(paragraphs), 3)
        blob = " ".join(paragraphs)
        self.assertIn("example.com", blob)
        self.assertIn("2", blob)

    def test_summary_empty(self):
        paragraphs = build_executive_summary([], "nothing.xyz", "es")
        self.assertTrue(any("No se encontraron" in p for p in paragraphs))

    def test_summary_english(self):
        paragraphs = build_executive_summary([_rec("a", xscore=90)], "example.com", "en")
        self.assertTrue(any("returned" in p for p in paragraphs))


class TestFindings(unittest.TestCase):
    def test_order_and_reasons(self):
        records = [_rec("low.txt", xscore=10), _rec("crit.sql", xscore=95),
                   _rec("mid.doc", xscore=60)]
        findings = top_findings(records, n=2, lang="es")
        self.assertEqual(len(findings), 2)
        self.assertEqual(findings[0]["name"], "crit.sql")
        self.assertEqual(findings[0]["severity"], SEVERITY_CRITICAL)
        self.assertTrue(findings[0]["reason"])
        self.assertIn("systemid", findings[0])

    def test_empty(self):
        self.assertEqual(top_findings([], n=5), [])


class TestIocsRecommendations(unittest.TestCase):
    def test_iocs_sorted_deterministic(self):
        records = [{"name": "a", "data": "contact admin@example.com 1.2.3.4 https://evil.test/x"}]
        iocs = collect_iocs(records)
        self.assertIn("admin@example.com", iocs["emails"])
        self.assertIn("1.2.3.4", iocs["ips"])
        self.assertEqual(iocs["emails"], sorted(iocs["emails"]))
        for key in ("domains", "ips", "emails", "urls"):
            self.assertIn(key, iocs)

    def test_recommendations_conditional(self):
        critical = [_rec("a", xscore=90, tags="public, sensitive", media=15)]
        recs = build_recommendations(critical, "es")
        blob = " ".join(recs).lower()
        self.assertIn("rote", blob)  # rotar credenciales
        self.assertIn("multifactor", blob)
        plain = build_recommendations([], "es")
        self.assertTrue(any("Monitoree" in r for r in plain))


class TestMethodologyGlossary(unittest.TestCase):
    def test_methodology_rows(self):
        rows = build_methodology("example.com", search_id="sid-1", lang="es")
        blob = " ".join(r["value"] for r in rows)
        self.assertIn("example.com", blob)
        self.assertIn("sid-1", blob)
        self.assertTrue(any("Limitaciones" in r["item"] for r in rows))

    def test_glossary(self):
        glossary = get_glossary("es")
        terms = [g["term"] for g in glossary]
        self.assertIn("xscore", terms)
        self.assertIn("Bucket", terms)
        self.assertTrue(all(g["definition"] for g in glossary))

    def test_escape(self):
        self.assertEqual(escape_html('<script>alert("x")</script>'),
                         '&lt;script&gt;alert(&quot;x&quot;)&lt;/script&gt;')


class TestFullNarrative(unittest.TestCase):
    def test_build_report_narrative(self):
        records = [_rec("db.sql", xscore=90), _rec("paste.txt", bucket="pastes", xscore=30)]
        narration = build_report_narrative(records, "example.com", search_id="sid-9", lang="es")
        for key in ("summary", "severity_counts", "findings", "iocs",
                    "recommendations", "methodology", "glossary", "lang"):
            self.assertIn(key, narration)
        self.assertEqual(narration["lang"], "es")
        self.assertEqual(narration["severity_counts"][SEVERITY_CRITICAL], 1)


if __name__ == "__main__":
    unittest.main()
