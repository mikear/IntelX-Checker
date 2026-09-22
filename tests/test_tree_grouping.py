import unittest
from utils import group_records, GROUP_MODES


def _rec(name, **kw):
    base = {"systemid": "id-" + name, "name": name, "bucket": "leaks",
            "type": 1, "media": 15, "date": "2024-03-10 12:00:00", "xscore": 0}
    base.update(kw)
    return base


class TestGroupRecords(unittest.TestCase):
    def test_modes_declared(self):
        self.assertEqual(tuple(GROUP_MODES), ("source", "severity", "type", "date"))

    def test_group_by_source(self):
        records = [_rec("a", bucket="leaks"), _rec("b", bucket="pastes"),
                   _rec("c", bucket="leaks")]
        groups = group_records(records, "source")
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0][0], "leaks")  # mayor cantidad primero
        self.assertEqual(len(groups[0][1]), 2)
        self.assertEqual(len(groups[1][1]), 1)

    def test_source_prefers_bucketh(self):
        records = [_rec("a", bucket="leaks", bucketh="Leaks DB")]
        groups = group_records(records, "source")
        self.assertEqual(groups[0][0], "Leaks DB")

    def test_group_by_severity(self):
        records = [_rec("a", xscore=90), _rec("b", xscore=10), _rec("c")]
        groups = dict(group_records(records, "severity"))
        self.assertEqual(len(groups["critical"]), 1)
        self.assertEqual(len(groups["low"]), 1)
        self.assertEqual(len(groups["unknown"]), 1)

    def test_group_by_type(self):
        records = [_rec("a", type=1, media=15), _rec("b", type=1, media=15),
                   _rec("c", type=2, media=19)]
        groups = group_records(records, "type")
        self.assertEqual(len(groups), 2)
        self.assertEqual(groups[0][0], "1||15")
        self.assertEqual(len(groups[0][1]), 2)

    def test_group_by_date(self):
        records = [_rec("a", date="2024-03-10 12:00:00"),
                   _rec("b", date="2024-01-20 09:15:00"),
                   _rec("c", date="")]
        groups = dict(group_records(records, "date"))
        self.assertEqual(len(groups["2024-03"]), 1)
        self.assertEqual(len(groups["2024-01"]), 1)
        self.assertEqual(len(groups[""]), 1)

    def test_unknown_mode_falls_back_to_source(self):
        records = [_rec("a", bucket="leaks")]
        groups = group_records(records, "bogus")
        self.assertEqual(groups[0][0], "leaks")

    def test_empty_and_str_records(self):
        self.assertEqual(group_records([], "source"), [])
        self.assertEqual(group_records(None, "source"), [])
        groups = group_records(["texto plano"], "source")
        self.assertEqual(groups[0][0], "unknown")
        groups = group_records(["texto plano"], "severity")
        self.assertEqual(groups[0][0], "unknown")

    def test_total_preserved(self):
        records = [_rec(f"r{i}", bucket="b%d" % (i % 3), xscore=i * 10) for i in range(10)]
        for mode in GROUP_MODES:
            total = sum(len(members) for _, members in group_records(records, mode))
            self.assertEqual(total, 10)


if __name__ == "__main__":
    unittest.main()
