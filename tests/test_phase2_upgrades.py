#!/usr/bin/env python3
"""Offline unit tests for Phase 2 pipeline upgrades (PR 2)."""
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts"))

import check_schema  # noqa: E402
import common  # noqa: E402
import datadecision  # noqa: E402
import extract  # noqa: E402
import fulltext  # noqa: E402
import pr_review_bundle  # noqa: E402
import to_template  # noqa: E402
import verify  # noqa: E402


class Phase2FulltextAndExtractTests(unittest.TestCase):
    def test_fulltext_parses_supplementary_and_chunks_large_table(self):
        big_rows = "".join(
            f"<tr><td>Gene{i}</td><td>{i}x fold change in APOE4</td></tr>" for i in range(400)
        )
        xml = (
            "<article><body><sec><title>Results</title><p>Lysosomal defect observed.</p>"
            f"<table-wrap><label>Table 1</label><caption><p>Big table</p></caption>"
            f"<table><tr><th>Gene</th><th>Effect</th></tr>{big_rows}</table></table-wrap>"
            "</sec></body>"
            "<back><app-group><app><title>Appendix</title><fig><label>Fig S3</label>"
            "<caption><p>Panel D shows lysosomal degradation.</p></caption></fig></app></app-group></back>"
            "</article>"
        )
        blocks = fulltext.parse_jats(xml)
        tblocks = [b for b in blocks if b["kind"] == "table"]
        self.assertGreater(len(tblocks), 1)
        self.assertTrue(all("Gene | Effect" in b["text"] for b in tblocks))
        self.assertTrue(any("Fig S3" in b["loc"] for b in blocks))

    def test_uncapped_chunks_and_fold_and_visual_only_and_panel_loc(self):
        long_blocks = [
            {"loc": f"Results > Sec {i}", "kind": "text", "text": f"APOE4 cholesterol lysosome block {i} " + ("a " * 2400)}
            for i in range(5)
        ]
        chunks = extract.select_chunks(long_blocks, budget=None, size=6000)
        self.assertGreater(sum(len(b["text"]) for c in chunks for b in c), 9000)

        q = "Filipin and TRITC-Dextran co-localization was significantly increased (3-fold, p<0.001) in APOE4 astrocytes (Figure 6H)."
        self.assertEqual(extract.verify_stat("effect_size", "3-fold", q, q), "3x")
        self.assertEqual(extract.verify_stat("effect_size", "3x", q, q), "3x")

        leg = "Data represent mean +/- SD (*p < 0.05; **p < 0.01, ANOVA) in Figures 4D and 4E."
        self.assertEqual(extract.verify_stat("p_value", "<0.05", leg, leg, provenance="visual_only"), "<0.05")
        self.assertIsNone(extract.verify_stat("p_value", "<0.05", "mean diameter < 0.05 um in cells", "mean diameter < 0.05 um in cells", provenance="visual_only"))
        self.assertEqual(extract.extract_panel_location(q, "Results > Cholesterol"), "Fig 6H")
        self.assertEqual(extract.extract_panel_location(leg, "Figure 4 legend"), "Fig 4D-E")
        self.assertEqual(extract.extract_panel_location("Representative images of filipin.", "Figure 6 legend"), "Fig 6")
        self.assertEqual(extract.extract_panel_location("Figure 4 shows decreased LAMP2.", "Results"), "Fig 4")
        self.assertEqual(extract.extract_panel_location("In Figure 2 a decrease in LAMP1 was seen.", "Results"), "Fig 2")
        self.assertEqual(extract.extract_panel_location("Panel (F) shows lysosomal activity.", "Figure 6 legend"), "Fig 6F")
        self.assertEqual(extract.extract_panel_location("Fig 4D and Fig 5E compared.", "Results"), "Fig 4D")
        self.assertEqual(extract.extract_panel_location("Figures 4D and 5E compared.", "Results"), "Fig 4D")
        self.assertEqual(extract.extract_panel_location("No fig here.", "Results", proposed_loc="Fig 99Z"), "Results")
        self.assertEqual(extract.extract_panel_location("Figure 6 legend shows filipin.", "Figure 6 legend", proposed_loc="Fig 6Z"), "Fig 6")
        self.assertEqual(extract.extract_panel_location("See Figures 6D-F.", "Figure 6 legend", proposed_loc="Fig 6E"), "Fig 6E")

        # merge_figure_estimates requires human_verified=True and full_text status
        p_unverified = [{"pmid": "1", "fulltext": {"status": "full_text"}, "findings": [{"quote": q, "effect_size": {"value": None}}]}]
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False) as tf:
            json.dump([{"pmid": "1", "quote": q, "human_verified": False, "effect_size": {"value": "~30%", "quote": q}}], tf)
            tf_path = tf.name
        try:
            extract.merge_figure_estimates(p_unverified, tf_path)
            self.assertIsNone(p_unverified[0]["findings"][0]["effect_size"]["value"])
        finally:
            os.unlink(tf_path)

    def test_tier1_ordered_before_tier2_and_review_purged(self):
        self.assertTrue(datadecision.is_review_record({"pubType": "Journal Article; Review"}))
        self.assertFalse(datadecision.is_review_record({"pubType": "Journal Article"}))
        self.assertEqual(datadecision.classify_c1_tier("human iPSC-derived astrocytes", {"v": "yes"}), 1)
        self.assertEqual(datadecision.classify_c1_tier("APOE4-TR mouse primary astrocytes", {"v": "yes"}), 2)

        recs = [
            {"pmid": "20", "tier": 2, "screen": {"include": True, "relevance": 0.99, "direction": "supports"}},
            {"pmid": "10", "tier": 1, "screen": {"include": True, "relevance": 0.80, "direction": "supports"}},
        ]
        picked = extract.select_papers(recs, max_papers=50)
        self.assertEqual([r["pmid"] for r in picked], ["10", "20"])


class Phase2TemplateAndSchemaTests(unittest.TestCase):
    def test_ambiguous_panel_source_type_and_release_method_guards(self):
        papers = [{
            "pmid": "42182449",
            "doi": "10.64898/2026.05.12.724612",
            "source_type": "PubMed preprint",
            "findings": [{
                "description": "Lysosomal acidification impaired.",
                "quote": "APOE4 microglia had impaired lysosomal acidification (Fig 2B).",
                "summary": "(APOE4) -> (impaired acidification)",
                "direction": "supports",
                "relevance": 0.9,
                "experimental_system": "human iPSC microglia",
                "location": "Fig 2B",
                "source": "full_text",
                "directness_class": 1,
                "directness_strength": 2,
                "effect_size": {"value": None, "quote": None, "provenance": "ambiguous_panel"},
                "p_value": {"value": None, "quote": None},
                "sample_size": {"value": None, "quote": None},
            }],
        }]
        rows = to_template.build_rows("HYP", papers)
        self.assertEqual(rows[2][2], "PubMed preprint")
        self.assertEqual(rows[3][11:13], ["N/A", "ambiguous_panel"])

        with tempfile.TemporaryDirectory() as td:
            xlsx = os.path.join(td, "preprint.xlsx")
            good_method = {
                "Team": "Khepri",
                "Team leader": "Alex Example",
                "Team leader email": "leader@example.org",
                "Method URL": "https://github.com/DrAhmed7887/hack-meccog-apoe4",
                "Commit SHA": "d315874",
                "Who did the work": "collab",
                "Model and version": "qwen3.8-27b, gemini-4-neon-high",
            }
            to_template.write_xlsx(xlsx, [("Submission", rows), ("Method", to_template.build_method(good_method, release=True))])
            self.assertEqual(check_schema.check(xlsx), [])
            self.assertEqual(check_schema.check_warnings(xlsx), [])

        with self.assertRaises(ValueError):
            to_template.build_method(to_template.DRY_METHOD, release=True)

    def test_pr_bundle_catches_retracted_epmc_and_dedups_dois(self):
        fake_epmc = json.dumps({
            "resultList": {
                "result": [{
                    "pmid": "111",
                    "title": "Retracted study",
                    "pubTypeList": {"pubType": ["Journal Article", "Retracted Publication"]},
                }],
            },
        })
        papers = [
            {"pmid": "111", "doi": "10.1000/dup", "title": "Retracted study"},
            {"pmid": "N/A", "source_type": "Other", "doi": "10.1000/dup", "title": "Preprint copy"},
        ]
        seen_cmds = []

        def fake_run(cmd, **kw):
            seen_cmds.append(cmd)
            import subprocess
            return subprocess.CompletedProcess(cmd, 0, stdout=json.dumps([{"doi": "10.1000/dup", "retracted": False}]), stderr="")

        with mock.patch.object(common, "http_get", return_value=fake_epmc), \
             mock.patch.object(pr_review_bundle.shutil, "which", return_value="/usr/bin/doi-check"), \
             mock.patch.object(pr_review_bundle.os.path, "exists", return_value=True), \
             mock.patch.object(pr_review_bundle.subprocess, "run", side_effect=fake_run):
            issues = pr_review_bundle.check_live_ids(papers)
        self.assertTrue(any("retracted publication" in i for i in issues))
        self.assertEqual(seen_cmds[0].count("10.1000/dup"), 1)

    def test_single_row_table_c2_rescue_ambiguous_panel_warnings_and_verify_doi(self):
        one_row = fulltext._emit_table_blocks("Table 2", "Cap", ["Sentence one. " * 25], limit=180)
        self.assertGreater(len(one_row), 1)
        multi_row = fulltext._emit_table_blocks("Table 3", "Cap", ["ColA | ColB", "Sentence one. " * 25], limit=180)
        self.assertGreater(len(multi_row), 1)

        c_rescue = {"C1": {"v": "yes", "q": "x"}, "C2": {"v": "yes", "q": "x"}, "C3": {"v": "yes", "q": "x"}}
        self.assertEqual(datadecision.rule_downgrade("H5", dict(c_rescue), "APOE4 astrocytes with cyclodextrin rescue showed restored lysosome pH")["C2"]["v"], "yes")
        c_no_e3 = {"C1": {"v": "yes", "q": "x"}, "C2": {"v": "yes", "q": "x"}, "C3": {"v": "yes", "q": "x"}}
        self.assertEqual(datadecision.rule_downgrade("H5", dict(c_no_e3), "APOE4 astrocytes with ABCA1 pathway lysosome measurement")["C2"]["v"], "unclear")

        leg = "APOE4 astrocytes showed lower LAMP2 (*p < 0.05; **p < 0.01) across 3 independent cultures (Fig S3)."
        cleaned = extract.clean_finding({
            "description": "LAMP2 reduced in APOE4 astrocytes.",
            "quote": leg,
            "summary": "(APOE4) -> (reduced LAMP2)",
            "direction": "supports",
            "relevance": 0.85,
            "experimental_system": "human iPSC astrocytes",
            "effect_size": {"value": None, "quote": None, "provenance": "ambiguous_panel"},
            "p_value": {"value": "<0.05", "quote": leg, "provenance": "visual_only"},
            "sample_size": {"value": "3", "quote": leg, "provenance": "printed_in_text"},
            "directness_class": 1,
            "directness_strength": 2,
        }, leg)
        self.assertEqual(cleaned["effect_size"]["provenance"], "ambiguous_panel")
        self.assertIn("visual_only_star_check", cleaned["physician_review_reasons"])

        with tempfile.TemporaryDirectory() as td:
            xlsx = os.path.join(td, "whole_sfig.xlsx")
            cleaned["location"] = "Fig S3"
            cleaned["source"] = "full_text"
            rows = to_template.build_rows("HYP", [{"pmid": "123", "doi": "10.1000/test", "findings": [cleaned]}])
            good_method = {
                "Team": "Khepri", "Team leader": "Alex Example", "Team leader email": "leader@example.org",
                "Method URL": "https://github.com/DrAhmed7887/hack-meccog-apoe4", "Commit SHA": "d315874",
                "Who did the work": "collab", "Model and version": "qwen3.8-27b, gemini-4-neon-high",
            }
            to_template.write_xlsx(xlsx, [("Submission", rows), ("Method", to_template.build_method(good_method, release=True))])
            self.assertEqual(check_schema.check(xlsx), [])
            self.assertTrue(any("Fig S3" in w for w in check_schema.check_warnings(xlsx)))

            dp = Path(td)
            (dp / "id_verification.json").write_text(json.dumps({
                "verified_all": True, "n_failed": 0, "n_verified": 1, "n_papers": 1,
                "papers": [{"pmid": None, "doi": "10.64898/2026.09.01.748585", "verified": True}],
            }))
            (dp / "extracted.json").write_text(json.dumps({
                "papers": [{"pmid": "N/A", "source_type": "Other", "doi": "10.64898/2026.09.01.748585", "findings": []}],
            }))
            verify.FAILS.clear()
            verify.check_id_verification(dp)
            self.assertEqual(verify.FAILS, [])

            (dp / "id_verification.json").write_text(json.dumps({
                "verified_all": True, "n_failed": 0, "n_verified": 1, "n_papers": 1,
                "papers": [{"pmid": "123", "doi": "10.1000/expected", "verified": True}],
            }))
            (dp / "extracted.json").write_text(json.dumps({
                "papers": [{"pmid": "123", "doi": "", "findings": []}],
            }))
            verify.FAILS.clear()
            verify.check_id_verification(dp)
            self.assertEqual(len(verify.FAILS), 1)
            verify.FAILS.clear()


if __name__ == "__main__":
    unittest.main()
