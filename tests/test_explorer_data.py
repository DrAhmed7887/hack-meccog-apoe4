#!/usr/bin/env python3
"""Verify deterministic docs/data/explorer_data.json against frozen Step 1 data and CIFs."""
import json
import re
import unittest

from scripts.build_explorer_data import H2_PATH, H5_PATH, OUT_PATH, ROOT, parse_cif_atoms


class TestExplorerData(unittest.TestCase):
    def test_explorer_counts_match_frozen_step1(self):
        h5 = json.loads(H5_PATH.read_text(encoding="utf-8"))
        h2 = json.loads(H2_PATH.read_text(encoding="utf-8"))
        ex = json.loads(OUT_PATH.read_text(encoding="utf-8"))

        self.assertEqual(ex["totals"]["n_papers_total"], len(h5["papers"]) + len(h2["papers"]))
        self.assertEqual(ex["totals"]["n_papers_total"], 30)
        self.assertEqual(ex["totals"]["n_unique_papers"], 28)
        self.assertEqual(ex["totals"]["n_structures"], 14)
        self.assertEqual(len(ex["structures"]), 14)
        self.assertEqual(ex["hypotheses"]["H5"]["n_papers"], 19)
        self.assertEqual(ex["hypotheses"]["H5"]["n_findings"], 67)
        self.assertEqual(ex["hypotheses"]["H5"]["n_contradicting"], 14)
        self.assertEqual(ex["hypotheses"]["H5"]["n_printed_stats"], 62)
        self.assertEqual(ex["hypotheses"]["H2"]["n_papers"], 11)
        self.assertEqual(ex["hypotheses"]["H2"]["n_findings"], 53)
        self.assertEqual(ex["hypotheses"]["H2"]["n_contradicting"], 15)
        self.assertEqual(ex["hypotheses"]["H2"]["n_printed_stats"], 64)
        self.assertEqual(len(ex["findings"]), 120)

    def test_explorer_fulltext_routes_and_pmids_valid(self):
        h5 = json.loads(H5_PATH.read_text(encoding="utf-8"))
        h2 = json.loads(H2_PATH.read_text(encoding="utf-8"))
        valid_pmids = {str(p["pmid"]) for p in h5["papers"] + h2["papers"] if str(p.get("pmid") or "").isdigit()}

        raw = OUT_PATH.read_text(encoding="utf-8")
        ex = json.loads(raw)
        routes = {f["fulltext_source"] for f in ex["findings"]}
        self.assertIn("pmc_oa", routes)
        self.assertIn("unpaywall", routes)

        for f in ex["findings"]:
            self.assertIn(f["directness_class"], {"1", "2", "3", "4", "5"})

        # Every 8-digit PMID cited anywhere in explorer_data.json must exist in frozen Step 1 data
        cited_8_digit = set(re.findall(r"(?<![0-9.])\b(\d{8})\b(?![0-9.])", raw))
        self.assertTrue(
            cited_8_digit.issubset(valid_pmids),
            f"Explorer cites unknown 8-digit PMIDs not in H5/H2: {sorted(cited_8_digit - valid_pmids)}",
        )

    def test_explorer_structures_and_residues_valid(self):
        ex = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        for st in ex["structures"]:
            p = ROOT / "docs" / st["file"]
            self.assertTrue(p.exists(), f"Missing structure {p}")
            self.assertLess(p.stat().st_size, 2 * 1024 * 1024, f"Oversized structure {p}")
            atoms, _, _ = parse_cif_atoms(p)
            present = {(a["asym"], a["seq"]) for a in atoms}
            for res in st["residues"]:
                self.assertIn(
                    (res["auth_asym_id"], res["auth_seq_id"]),
                    present,
                    f"{st['id']} missing auth residue {res}",
                )

    def test_explorer_apoe4_salt_bridge_geometry(self):
        ex = json.loads(OUT_PATH.read_text(encoding="utf-8"))
        g = ex["geometry"]
        self.assertGreaterEqual(g["1b68_Arg112_Glu109"]["distance_A"], 2.3)
        self.assertLessEqual(g["1b68_Arg112_Glu109"]["distance_A"], 3.2)
        self.assertGreater(g["1b68_Arg61_Glu109"]["distance_A"], g["1nfn_Arg61_Glu109"]["distance_A"])

    def test_video_captions_use_scientific_notation(self):
        tl_path = ROOT / "video" / "remotion" / "src" / "timeline.json"
        tl = json.loads(tl_path.read_text(encoding="utf-8"))
        phonetic = (
            "one-b-six-eight", "one-n-f-n", "one hundred", "two point five", "three point five",
            "five point three", "molstar", "three-d", "twenty-eight", "twenty-nine", "tier two", "step one",
        )
        texts = [c["text"] for s in tl["scenes"] for c in s["captions"]]
        vtt = ROOT / "docs" / "media" / "captions.vtt"
        self.assertTrue(vtt.exists(), "docs/media/captions.vtt must exist")
        texts.append(vtt.read_text(encoding="utf-8"))
        for text in texts:
            for token in phonetic:
                self.assertNotIn(token, text.lower(), f"phonetic token {token!r} in caption: {text!r}")

    def test_normalize_aligned_words(self):
        from video.build_timeline import normalize_aligned_words

        def mk(*ws):
            return [{"w": w, "start": float(i), "end": float(i) + 0.5} for i, w in enumerate(ws)]

        # (a) longest match wins
        self.assertEqual([w["w"] for w in normalize_aligned_words(mk("one", "hundred", "twenty-six"))], ["126"])
        self.assertEqual([w["w"] for w in normalize_aligned_words(mk("one", "hundred", "twenty"))], ["120"])
        # (b) trailing punctuation kept
        self.assertEqual(
            [w["w"] for w in normalize_aligned_words(mk("position", "one", "hundred", "twelve,"))],
            ["position 112,"],
        )
        # (c) merged span timing
        words = mk("one", "hundred", "twenty-six")
        out = normalize_aligned_words(words)
        self.assertEqual(out[0]["start"], words[0]["start"])
        self.assertEqual(out[0]["end"], words[-1]["end"])
        # (d) bare 'thirty' unchanged; 'thirty entries.' merged
        self.assertEqual([w["w"] for w in normalize_aligned_words(mk("thirty", "days"))], ["thirty", "days"])
        self.assertEqual([w["w"] for w in normalize_aligned_words(mk("thirty", "entries."))], ["30 entries."])
        # (e) ordinary words pass through
        plain = mk("the", "protein", "folds")
        self.assertEqual(normalize_aligned_words(plain), plain)


if __name__ == "__main__":
    unittest.main()
