#!/usr/bin/env python3
"""Offline unit tests for scripts/pr_review_bundle.py."""
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts import pr_review_bundle


class TestPrReviewBundle(unittest.TestCase):
    def test_audit_passes_valid_single_block_and_figure_estimate(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ft = root / "ft"
            ft.mkdir()
            (ft / "12345.json").write_text(json.dumps({
                "pmid": "12345",
                "status": "full_text",
                "blocks": [{
                    "loc": "Figure 6 legend",
                    "kind": "legend",
                    "text": "Filipin increased 3x (p < 0.001) in Fig 6H across APOE4 astrocytes.",
                }],
            }), encoding="utf-8")
            ext = root / "extracted.json"
            ext.write_text(json.dumps({
                "hyp": "H5",
                "papers": [{
                    "pmid": "12345",
                    "doi": "10.1000/test",
                    "fulltext": {"status": "full_text"},
                    "findings": [
                        {
                            "description": "Cholesterol increased in lysosomes.",
                            "quote": "Filipin increased 3x (p < 0.001) in Fig 6H across APOE4 astrocytes.",
                            "direction": "supports",
                            "location": "Fig 6H",
                            "source": "full_text",
                            "effect_size": {"value": "3x", "quote": "Filipin increased 3x (p < 0.001)", "provenance": "printed_in_text"},
                            "p_value": {"value": "<0.001", "quote": "p < 0.001", "provenance": "printed_in_text"},
                            "sample_size": {"value": "~12", "quote": "Filipin increased 3x (p < 0.001) in Fig 6H across APOE4 astrocytes.", "provenance": "estimated_from_figure"},
                        },
                    ],
                }],
            }), encoding="utf-8")
            rep = pr_review_bundle.audit_extracted_file(ext, ft, require_fulltext_cache=True)
            self.assertEqual(rep["issues"], [])
            self.assertEqual(rep["warnings"], [])
            self.assertEqual(rep["n_stats"], 3)

    def test_audit_blocks_estimated_p_value_and_missing_cache_flag(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ft = root / "ft"
            ft.mkdir()
            ext = root / "extracted.json"
            ext.write_text(json.dumps({
                "hyp": "H5",
                "papers": [{
                    "pmid": "99999",
                    "abstract": "Abstract only.",
                    "fulltext": {"status": "full_text"},
                    "findings": [{
                        "description": "Test finding.",
                        "quote": "Abstract only.",
                        "direction": "supports",
                        "location": "Fig 4",
                        "source": "full_text",
                        "effect_size": {"value": None, "quote": None},
                        "p_value": {"value": "~0.01", "quote": "Abstract only.", "provenance": "estimated_from_figure"},
                        "sample_size": {"value": None, "quote": None},
                    }],
                }],
            }), encoding="utf-8")
            rep_ci = pr_review_bundle.audit_extracted_file(ext, ft, require_fulltext_cache=False)
            self.assertTrue(any("P value cannot use" in i for i in rep_ci["issues"]))
            self.assertTrue(any("fulltext cache missing" in w for w in rep_ci["warnings"]))
            self.assertTrue(any("whole-figure" in w for w in rep_ci["warnings"]))

            rep_strict = pr_review_bundle.audit_extracted_file(ext, ft, require_fulltext_cache=True)
            self.assertTrue(any("fulltext cache missing" in i for i in rep_strict["issues"]))

    def test_audit_catches_rule_c5_leak(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ft = root / "ft"
            ft.mkdir()
            (ft / "77777.json").write_text(json.dumps({
                "pmid": "77777",
                "status": "full_text",
                "blocks": [{"loc": "Results", "kind": "text", "text": "APOE4 astrocytes had higher AlphaFold pLDDT scores in Fig 4."}],
            }), encoding="utf-8")
            ext = root / "extracted.json"
            ext.write_text(json.dumps({
                "hyp": "H5",
                "papers": [{
                    "pmid": "77777",
                    "fulltext": {"status": "full_text"},
                    "findings": [{
                        "description": "AlphaFold pLDDT score noted.",
                        "quote": "APOE4 astrocytes had higher AlphaFold pLDDT scores in Fig 4.",
                        "direction": "supports",
                        "location": "Fig 4",
                        "source": "full_text",
                        "effect_size": {"value": None, "quote": None},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                    }],
                }],
            }), encoding="utf-8")
            rep = pr_review_bundle.audit_extracted_file(ext, ft, require_fulltext_cache=True)
            self.assertTrue(any("Rule C5" in i for i in rep["issues"]))

    def test_check_live_ids_catches_review_article_and_missing_doicheck(self):
        fake_epmc = json.dumps({
            "resultList": {
                "result": [{
                    "title": "APOE4 lipid review",
                    "pubTypeList": {"pubType": ["Journal Article", "Review"]},
                }],
            },
        })
        papers = [{"pmid": "42927732", "doi": "10.1000/rev", "title": "APOE4 lipid review"}]
        with mock.patch("common.http_get", return_value=fake_epmc), \
             mock.patch("shutil.which", return_value=None), \
             mock.patch("os.path.exists", return_value=False):
            issues = pr_review_bundle.check_live_ids(papers)
        self.assertTrue(any("review article" in i for i in issues))
        self.assertTrue(any("doi-check binary missing" in i for i in issues))


if __name__ == "__main__":
    unittest.main()
