import json
import os
import tempfile
import unittest
from unittest.mock import patch

import datadecision
import fulltext


class WidenTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dd = os.path.join(self.tmp.name, "dd")
        os.makedirs(self.dd)
        self.dd_patch = patch.object(datadecision, "DD", self.dd)
        self.dd_patch.start()
        self.addCleanup(self.dd_patch.stop)

    def write_json(self, path, value):
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f)

    def read_json(self, path):
        with open(path, encoding="utf-8") as f:
            return json.load(f)

    def test_widen_dedupes_filters_caps_and_backs_up(self):
        original = {
            "hyp": "H5", "query": "existing query", "total_hits": 1, "n_query": 1,
            "records": [{"pmid": "9000", "title": "Existing APOE paper", "abstract": "APOE4", "via": "query"}],
        }
        pool_path = os.path.join(self.dd, "pool_H5.json")
        self.write_json(pool_path, original)
        ids = ["9000", "titlehit", "abstracthit", "noapoe"] + [f"good{i:02}" for i in range(81)]

        def fetch(kind, seed, cap):
            self.assertEqual(cap, 60)
            return [{"pmid": p} for p in ids]

        def efetch(pmids, key):
            self.assertEqual(len(pmids), len(set(pmids)))
            records = []
            for p in pmids:
                title, abstract = "Study", ""
                if p == "titlehit":
                    title = "APOE4 title match"
                elif p == "abstracthit":
                    abstract = "APOE appears in abstract"
                elif p != "noapoe":
                    title = f"APOE study {p}"
                records.append({"pmid": p, "title": title, "abstract": abstract, "year": "2025"})
            return records

        with patch.object(datadecision.snowball, "fetch", side_effect=fetch) as snowfetch, \
                patch.object(datadecision.search, "efetch", side_effect=efetch), \
                patch.object(datadecision.common, "ncbi_key", return_value="test-key"):
            datadecision.build_pool("H5", widen=True)

        self.assertEqual(snowfetch.call_count, 10)  # five seeds, references and citations
        merged = self.read_json(pool_path)
        backup = self.read_json(os.path.join(self.dd, "pool_H5.before_widen.json"))
        self.assertEqual(backup, original)
        new_records = merged["records"][1:]
        self.assertEqual(len(new_records), 80)
        self.assertEqual(len({r["pmid"] for r in merged["records"]}), 81)
        self.assertNotIn("9000", [r["pmid"] for r in new_records])
        self.assertNotIn("noapoe", [r["pmid"] for r in new_records])
        self.assertEqual({r["pmid"] for r in new_records[:2]}, {"titlehit", "abstracthit"})
        self.assertTrue(all(r["via"] == "widen:references:37777962" for r in new_records))

    def test_report_uses_c1_to_c4_pass_set_and_cap(self):
        records, screen, ft = [], {}, {}
        for i in range(51):
            pmid = str(1000 + i)
            records.append({"pmid": pmid, "title": f"Study {i}", "abstract": "Human iPSC lysosomal degradation.",
                            "year": "2025", "via": "query"})
            screen[pmid] = {
                "C1": {"v": "yes", "q": "iPSC"}, "C2": {"v": "yes", "q": "APOE4 vs APOE3"},
                "C3": {"v": "yes", "q": "lysosomal degradation"},
                "C5": {"v": "yes" if i % 2 == 0 else "no", "q": None},
            }
            ft[pmid] = {"status": "full_text", "chars": 10, "route": "test", "effects": []}
        self.write_json(os.path.join(self.dd, "pool_H5.json"), {"records": records})
        self.write_json(os.path.join(self.dd, "screen_H5.json"), screen)
        self.write_json(os.path.join(self.dd, "ft_H5.json"), ft)

        with patch.object(fulltext, "MIN_BODY_CHARS", 1):
            datadecision.report(["H5"])

        result = self.read_json(os.path.join(self.dd, "report.json"))["H5"]
        self.assertEqual(result["pass_C1_C4"], 51)
        self.assertEqual(result["n_pass_C1_C4_cap50"], 50)
        self.assertEqual(result["contrary_C5_yes_among_pass"], 26)
        self.assertEqual(result["contrary_C5_yes_all"], 26)
        self.assertNotIn("pass_C1_C5", result)

    def test_screen_and_ft_skip_cached_pmids(self):
        record = {"pmid": 123, "title": "Already done", "abstract": "text"}
        pool = {"records": [record]}
        cached = {"123": {"C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "yes"}}}
        files = {
            f"{self.dd}/pool_H5.json": pool,
            f"{self.dd}/screen_H5.json": cached,
            f"{self.dd}/ft_H5.json": {"123": {"status": "full_text"}},
            "hypotheses.json": {"H5": {"statement": "test"}},
        }
        for name in ("screen_H5.json", "ft_H5.json"):
            open(os.path.join(self.dd, name), "w").close()
        with patch.object(datadecision.common, "load_json", side_effect=lambda path: files[path]), \
                patch.object(datadecision.common, "save_json") as save_json, \
                patch.object(datadecision, "ask") as ask, \
                patch.object(datadecision.fulltext, "fetch_one") as fetch_one:
            datadecision.screen("H5")
            datadecision.ft("H5")
        ask.assert_not_called()
        fetch_one.assert_not_called()
        save_json.assert_called()


if __name__ == "__main__":
    unittest.main()
