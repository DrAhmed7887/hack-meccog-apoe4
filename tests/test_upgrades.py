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
import datadecision  # noqa: E402
import extract  # noqa: E402
import to_template  # noqa: E402
import verify  # noqa: E402
import verify_ids  # noqa: E402


FIG_BLOCK = {
    "loc": "Figure 4 legend",
    "kind": "legend",
    "text": "Bar chart of lysosomal degradation in APOE4 vs APOE3 iAstrocytes; individual plotted points shown.",
}


class RuleC1SelectionTests(unittest.TestCase):
    def test_orders_by_relevance_caps_at_50_and_preserves_contrary(self):
        recs = []
        for i in range(60):
            recs.append({
                "pmid": str(1000 + i),
                "screen": {"include": True, "relevance": 0.9 - i * 0.005, "direction": "supports"},
            })
        recs.append({
            "pmid": "40457456",
            "c5": "yes",
            "screen": {"include": True, "relevance": 0.2, "direction": "contradicts"},
        })
        recs.append({
            "pmid": "9999",
            "screen": {"include": False, "relevance": 1.0, "direction": "supports"},
        })
        picked = extract.select_papers(recs, max_papers=80)
        self.assertEqual(len(picked), 50)
        pmids = [r["pmid"] for r in picked]
        self.assertIn("40457456", pmids)
        self.assertNotIn("9999", pmids)
        rels = [r["screen"]["relevance"] for r in picked]
        self.assertEqual(rels, sorted(rels, reverse=True))

    def test_39532095_constraints_enforce_exogenous_system_and_lower_directness(self):
        block_text = "In human NGN2 iNeurons, CE(20:4)-lipidated ApoE4 induced lipofuscin accumulation."
        finding = {
            "description": "Exogenous ApoE4 increased lipofuscin in iNeurons.",
            "quote": block_text,
            "summary": "(ApoE4) -> (lipofuscin)",
            "direction": "supports",
            "relevance": 0.8,
            "experimental_system": "human NGN2 iNeurons, ApoE4 vs ApoE3",
            "directness_class": 1,
            "directness_strength": 1,
            "effect_size": {"value": None, "quote": None},
            "p_value": {"value": None, "quote": None},
            "sample_size": {"value": None, "quote": None},
        }
        constraints = datadecision.DEFAULT_CONSTRAINTS["39532095"]
        cleaned = extract.clean_finding(finding, block_text, constraints=constraints)
        self.assertEqual(cleaned["directness_class"], 2)
        self.assertEqual(cleaned["directness_strength"], 3)
        self.assertIn("exogenous", cleaned["experimental_system"].lower())
        self.assertTrue(cleaned["physician_review"])

    def test_datadecision_select_signed_pool(self):
        with tempfile.TemporaryDirectory() as td:
            dd = Path(td) / "dd"
            dd.mkdir()
            pool = {"records": [
                {"pmid": "34919811", "doi": "10.1/a", "title": "A", "year": "2022", "journal": "J", "abstract": "x"},
                {"pmid": "40457456", "doi": "10.1/b", "title": "B", "year": "2025", "journal": "J", "abstract": "x"},
                {"pmid": "39532095", "doi": "10.1/c", "title": "C", "year": "2025", "journal": "J", "abstract": "x"},
                {"pmid": "37777962", "doi": "10.1/d", "title": "D", "year": "2023", "journal": "J", "abstract": "x"},
                {"pmid": "99999999", "doi": "10.1/e", "title": "E", "year": "2023", "journal": "J", "abstract": "x"},
            ]}
            rep = {"H5": {"rows": [
                {"pmid": "34919811", "C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "yes"}, "C4": "yes", "C5": {"v": "unclear"}},
                {"pmid": "40457456", "C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "yes"}, "C4": "yes", "C5": {"v": "yes"}},
                {"pmid": "39532095", "C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "yes"}, "C4": "yes", "C5": {"v": "unclear"}},
                {"pmid": "37777962", "C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "yes"}, "C4": "no", "C5": {"v": "unclear"}},
                {"pmid": "99999999", "C1": {"v": "yes"}, "C2": {"v": "yes"}, "C3": {"v": "no"}, "C4": "yes", "C5": {"v": "no"}},
            ]}}
            (dd / "pool_H5.json").write_text(json.dumps(pool), encoding="utf-8")
            (dd / "report.json").write_text(json.dumps(rep), encoding="utf-8")
            out_path = str(Path(td) / "signed.json")
            with mock.patch.object(datadecision, "DD", str(dd)):
                picked = datadecision.select_signed_pool("H5", out_path, include_anchor=True, screened_path="")
            pmids = {r["pmid"] for r in picked}
            self.assertEqual(pmids, {"34919811", "40457456", "39532095", "37777962"})
            r_contra = next(r for r in picked if r["pmid"] == "40457456")
            self.assertEqual(r_contra["screen"]["direction"], "contradicts")
            r_exo = next(r for r in picked if r["pmid"] == "39532095")
            self.assertEqual(r_exo["constraints"]["min_directness_class"], 2)


class RuleC4IdVerificationTests(unittest.TestCase):
    def test_verify_papers_online_pass_and_reject(self):
        papers = [
            {"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "title": "APOE2, E3, and E4"},
            {"pmid": "99999999", "doi": "10.1000/fake", "title": "Nonexistent paper"},
        ]

        def fake_efetch(pmids, key):
            return [{"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "title": "APOE2, E3, and E4"}]

        def fake_epmc(pmid):
            if pmid == "34919811":
                return {"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "title": "APOE2, E3, and E4"}
            return None

        with mock.patch.object(verify_ids.search, "efetch", side_effect=fake_efetch), \
                mock.patch.object(verify_ids, "fetch_epmc_by_pmid", side_effect=fake_epmc):
            log = verify_ids.verify_papers(papers, offline=False, cache_paths=(), fulltext_dir="")
        self.assertFalse(log["verified_all"])
        self.assertEqual(log["n_verified"], 1)
        self.assertEqual(log["n_failed"], 1)
        self.assertTrue(log["papers"][0]["verified"])
        self.assertFalse(log["papers"][1]["verified"])

    def test_verify_papers_doi_mismatch_and_duplicate_rejected(self):
        papers = [
            {"pmid": "34919811", "doi": "10.1016/j.wrong.2021", "title": "APOE2, E3, and E4"},
            {"pmid": "35750033", "doi": "10.1016/j.wrong.2021", "title": "Cholesterol"},
        ]

        def fake_efetch(pmids, key):
            return [
                {"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "title": "APOE2, E3, and E4"},
                {"pmid": "35750033", "doi": "10.1016/j.cell.2022.05.017", "title": "Cholesterol"},
            ]

        def fake_epmc(pmid):
            return {"pmid": pmid, "doi": "10.1016/j.stemcr.2021.11.007" if pmid == "34919811" else "10.1016/j.cell.2022.05.017"}

        with mock.patch.object(verify_ids.search, "efetch", side_effect=fake_efetch), \
                mock.patch.object(verify_ids, "fetch_epmc_by_pmid", side_effect=fake_epmc):
            log = verify_ids.verify_papers(papers, offline=False, cache_paths=(), fulltext_dir="")
        self.assertEqual(log["n_failed"], 2)
        self.assertTrue(any("DOI" in e for e in log["papers"][0]["errors"]))
        self.assertTrue(any("duplicate DOI" in e for e in log["papers"][1]["errors"]))

    def test_scripts_verify_checks_id_verification(self):
        verify.FAILS.clear()
        verify.WARNS.clear()
        with tempfile.TemporaryDirectory() as td:
            d = Path(td)
            (d / "extracted.json").write_text(json.dumps({
                "papers": [{"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "findings": []}]
            }), encoding="utf-8")
            (d / "id_verification.json").write_text(json.dumps({
                "verified_all": True, "n_papers": 1, "n_verified": 1, "n_failed": 0,
                "papers": [{"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "verified": True}],
            }), encoding="utf-8")
            verify.check_id_verification(d, strict=True)
            self.assertEqual(verify.FAILS, [])

            (d / "id_verification.json").write_text(json.dumps({
                "verified_all": False, "n_papers": 1, "n_verified": 0, "n_failed": 1, "papers": [],
            }), encoding="utf-8")
            verify.check_id_verification(d, strict=True)
            self.assertTrue(verify.FAILS)


class RuleC3FigureEstimateTests(unittest.TestCase):
    def _base_finding(self, **kw):
        f = {
            "description": "APOE4 reduced lysosomal degradation in iAstrocytes.",
            "quote": FIG_BLOCK["text"],
            "summary": "(APOE4) -> (impaired lysosomal degradation)",
            "direction": "supports",
            "relevance": 0.9,
            "experimental_system": "human iPSC-derived astrocytes, APOE4 vs APOE3",
            "directness_class": 1,
            "directness_strength": 2,
            "effect_size": {"value": "~40%", "quote": "Bar chart of lysosomal degradation", "provenance": "estimated_from_figure"},
            "p_value": {"value": None, "quote": None},
            "sample_size": {"value": "~12", "quote": "individual plotted points shown", "provenance": "estimated_from_figure"},
        }
        f.update(kw)
        return f

    def test_valid_estimated_from_figure_effect_and_sample_roundtrip(self):
        c = extract.clean_ft_finding(self._base_finding(), [FIG_BLOCK])
        self.assertEqual(c["effect_size"]["value"], "~40%")
        self.assertEqual(c["effect_size"]["provenance"], "estimated_from_figure")
        self.assertEqual(c["sample_size"]["value"], "~12")
        self.assertEqual(c["sample_size"]["provenance"], "estimated_from_figure")
        self.assertIsNone(c["p_value"]["value"])

        rows = to_template.build_rows("HYP", [{"pmid": "34919811", "doi": "10.1016/j.stemcr.2021.11.007", "findings": [c]}])
        self.assertEqual(rows[3][11:17], ["~40%", "estimated_from_figure", "N/A", "not_found_in_source", "~12", "estimated_from_figure"])
        with tempfile.TemporaryDirectory() as td:
            xlsx = os.path.join(td, "ok.xlsx")
            to_template.write_xlsx(xlsx, [("Submission", rows), ("Method", to_template.build_method(to_template.DRY_METHOD))])
            self.assertEqual(check_schema.check(xlsx), [])

    def test_rejected_p_value_estimated_from_figure_in_extract_template_and_schema(self):
        f = self._base_finding(p_value={"value": "~0.03", "quote": "Bar chart of lysosomal degradation", "provenance": "estimated_from_figure"})
        c = extract.clean_ft_finding(f, [FIG_BLOCK])
        self.assertIsNone(c["p_value"]["value"])
        self.assertIn("estimated_p_value_rejected", c["physician_review_reasons"])

        self.assertIsNone(extract.verify_stat("p_value", "~0.03", FIG_BLOCK["text"], FIG_BLOCK["text"], provenance="estimated_from_figure"))
        self.assertIsNone(extract.verify_stat("p_value", "0.03", FIG_BLOCK["text"], FIG_BLOCK["text"], provenance="estimated_from_figure"))

        bad_finding = dict(c, p_value={"value": "~0.03", "quote": "x", "provenance": "estimated_from_figure"})
        with self.assertRaises(ValueError):
            to_template.build_rows("HYP", [{"pmid": "1", "doi": "10.1/x", "findings": [bad_finding]}])

        rows = [
            to_template.COLUMNS,
            ["HYP"] + [None] * 18,
            [None, "10.1/x", "PubMed published", "1", "P1"] + [None] * 14,
            [None, None, None, None, "P1.F1", "desc", "q" * 10, "(a)->(b)", "0.8", "cells", "Figure 4 legend",
             "~40%", "estimated_from_figure", "~0.03", "estimated_from_figure", "~12", "estimated_from_figure", "1", "2 strong"],
        ]
        with tempfile.TemporaryDirectory() as td:
            xlsx = os.path.join(td, "bad_p.xlsx")
            to_template.write_xlsx(xlsx, [("Submission", rows), ("Method", to_template.build_method(to_template.DRY_METHOD))])
            errs = check_schema.check(xlsx)
            self.assertTrue(any("P value" in e for e in errs))

    def test_rejected_tilde_and_provenance_mismatches(self):
        # Missing ~ with estimated_from_figure
        self.assertIsNone(extract.verify_stat("effect_size", "40%", FIG_BLOCK["text"], FIG_BLOCK["text"], provenance="estimated_from_figure"))
        # ~qualitative forbidden
        self.assertIsNone(extract.verify_stat("effect_size", "~qualitative", FIG_BLOCK["text"], FIG_BLOCK["text"], provenance="estimated_from_figure"))
        # ~ without estimated_from_figure
        self.assertIsNone(extract.verify_stat("sample_size", "~12", FIG_BLOCK["text"], FIG_BLOCK["text"], provenance="printed_in_text"))

        for bad_eff in (
            {"value": "40%", "quote": "x", "provenance": "estimated_from_figure"},
            {"value": "~40%", "quote": "x", "provenance": "printed_in_text"},
            {"value": "~qualitative", "quote": "x", "provenance": "estimated_from_figure"},
        ):
            f = {
                "description": "d", "quote": "q" * 10, "summary": "(a)->(b)", "direction": "supports",
                "relevance": 0.8, "experimental_system": "cells", "directness_class": 1, "directness_strength": 2,
                "effect_size": bad_eff, "p_value": {"value": None, "quote": None}, "sample_size": {"value": None, "quote": None},
            }
            with self.assertRaises(ValueError):
                to_template.build_rows("HYP", [{"pmid": "1", "doi": "10.1/x", "findings": [f]}])

        rows = [
            to_template.COLUMNS,
            ["HYP"] + [None] * 18,
            [None, "10.1/x", "PubMed published", "1", "P1"] + [None] * 14,
            [None, None, None, None, "P1.F1", "desc", "q" * 10, "(a)->(b)", "0.8", "cells", "Figure 4 legend",
             "40%", "estimated_from_figure", "N/A", "not_found_in_source", "~12", "printed_in_text", "1", "2 strong"],
        ]
        with tempfile.TemporaryDirectory() as td:
            xlsx = os.path.join(td, "bad_prov.xlsx")
            to_template.write_xlsx(xlsx, [("Submission", rows), ("Method", to_template.build_method(to_template.DRY_METHOD))])
            errs = check_schema.check(xlsx)
            self.assertTrue(any("requires leading ~" in e for e in errs))
            self.assertTrue(any("starts with ~ without estimated_from_figure" in e for e in errs))


class PhysicianAuditPostRulesTests(unittest.TestCase):
    def test_apply_h5_physician_audit_cleanups(self):
        papers = [
            {
                "pmid": "34919811",
                "doi": "10.1016/j.stemcr.2021.11.007",
                "findings": [
                    {
                        "description": "Lysosomal cholesterol colocalization.",
                        "quote": "Further colocalization of Filipin III with Dextran-Alexa 555 was highest in APOE4 iAstrocytes.",
                        "summary": "(APOE4) -> (lysosomal cholesterol)",
                        "direction": "supports",
                        "relevance": 0.82,
                        "experimental_system": "iAstrocytes",
                        "directness_class": 3,
                        "directness_strength": 3,
                        "effect_size": {"value": "qualitative", "quote": "highest in APOE4 iAstrocytes", "provenance": "printed_in_text"},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                    },
                    {
                        "description": "Lipid GSEA only.",
                        "quote": "Total cholesterol and CE were lowest in APOE4 and highest in APOE3 iAstrocytes.",
                        "summary": "(APOE4) -> (total cholesterol)",
                        "direction": "neutral",
                        "relevance": 0.4,
                        "experimental_system": "iAstrocytes",
                        "directness_class": 5,
                        "directness_strength": 5,
                        "effect_size": {"value": None, "quote": None},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                    },
                ],
            },
            {
                "pmid": "39532095",
                "doi": "10.1016/j.cell.2024.10.027",
                "findings": [
                    {
                        "description": "LDL inhibition in H4.",
                        "quote": "both lipApoE3 and lipApoE4 led to 60-65% inhibition of DiI-LDL uptake",
                        "summary": "(lipApoE3/4) -> (inhibited LDL uptake)",
                        "direction": "neutral",
                        "relevance": 0.45,
                        "experimental_system": "exogenous PUFA-CE-lipidated ApoE in human neurons/cells; H4 cells (human iPSC-derived neurons); APOE3/APOE4 grouped vs APOE2",
                        "directness_class": 4,
                        "directness_strength": 4,
                        "effect_size": {"value": None, "quote": None},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                        "physician_review": True,
                    }
                ],
            },
            {
                "pmid": "40457456",
                "doi": "10.1186/s12974-025-03470-y",
                "findings": [
                    {
                        "description": "Lower lysosomal degradation.",
                        "quote": "E4/E4 iMGs exhibited significantly lower lysosomal degradation activity compared to E3/E3 cells",
                        "summary": "(E4/E4) -> (lower lysosomal degradation)",
                        "direction": "supports",
                        "relevance": 0.92,
                        "experimental_system": "iMGs",
                        "directness_class": 2,
                        "directness_strength": 2,
                        "effect_size": {"value": "qualitative", "quote": "significantly lower", "provenance": "printed_in_text"},
                        "p_value": {"value": None, "quote": None},
                        "sample_size": {"value": None, "quote": None},
                    }
                ],
            },
        ]
        extract.apply_h5_physician_audit(papers)
        self.assertEqual(len(papers[0]["findings"]), 2)
        self.assertIn("LAMP2", papers[0]["findings"][1]["quote"])
        self.assertIn("H4 human neuroblastoma cells", papers[1]["findings"][0]["experimental_system"])
        self.assertFalse(papers[1]["findings"][0]["physician_review"])
        self.assertEqual(len(papers[2]["findings"]), 2)
        self.assertEqual(papers[2]["findings"][1]["direction"], "contradicts")

        rows = to_template.build_rows("HYP", papers)
        descs = [r[5] for r in rows[2:] if r[5]]
        self.assertFalse(any(to_template.REVIEW_MARKER in d for d in descs))
        self.assertTrue(any(d.startswith("CONTRADICTING: ") for d in descs))


if __name__ == "__main__":
    unittest.main()
