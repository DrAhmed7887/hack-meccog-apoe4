#!/usr/bin/env python3
"""Offline unit tests for scripts/pr_review_bundle.py."""
import json
import tempfile
import unittest
from pathlib import Path

from scripts import pr_review_bundle


class TestPrReviewBundle(unittest.TestCase):
    def test_audit_passes_valid_single_block_finding(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ft = root / "ft"
            ft.mkdir()
            (ft / "12345.json").write_text(json.dumps({
                "pmid": "12345",
                "status": "full_text",
                "blocks": [{"loc": "Results > Cholesterol", "kind": "text", "text": "Filipin increased 3x (p < 0.001) in Fig 6H."}],
            }), encoding="utf-8")
            ext = root / "extracted.json"
            ext.write_text(json.dumps({
                "hyp": "H5",
                "papers": [{
                    "pmid": "12345",
                    "doi": "10.1000/test",
                    "fulltext": {"status": "full_text"},
                    "findings": [{
                        "description": "Cholesterol increased in lysosomes.",
                        "quote": "Filipin increased 3x (p < 0.001) in Fig 6H.",
                        "direction": "supports",
                        "location": "Fig 6H",
                        "source": "full_text",
                        "effect_size": {"value": "3x", "quote": "Filipin increased 3x (p < 0.001)", "provenance": "printed_in_text"},
                        "p_value": {"value": "<0.001", "quote": "p < 0.001", "provenance": "printed_in_text"},
                        "sample_size": {"value": None, "quote": None},
                    }],
                }],
            }), encoding="utf-8")
            rep = pr_review_bundle.audit_extracted_file(ext, ft)
            self.assertEqual(rep["issues"], [])
            self.assertEqual(rep["warnings"], [])
            self.assertEqual(rep["n_stats"], 2)

    def test_audit_catches_rule_c5_leak_and_whole_fig_warning(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            ft = root / "ft"
            ft.mkdir()
            ext = root / "extracted.json"
            ext.write_text(json.dumps({
                "hyp": "H5",
                "papers": [{
                    "pmid": "99999",
                    "abstract": "APOE4 astrocytes had higher AlphaFold pLDDT scores.",
                    "fulltext": {"status": "unavailable"},
                    "findings": [{
                        "description": "AlphaFold pLDDT score noted.",
                        "quote": "APOE4 astrocytes had higher AlphaFold pLDDT scores.",
                        "direction": "supports",
                        "location": "Fig 4",
                        "source": "full_text",
                        "effect_size": {"value": None, "quote": None},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                    }],
                }],
            }), encoding="utf-8")
            rep = pr_review_bundle.audit_extracted_file(ext, ft)
            self.assertTrue(any("Rule C5" in i for i in rep["issues"]))
            self.assertTrue(any("whole-figure" in w for w in rep["warnings"]))


if __name__ == "__main__":
    unittest.main()
