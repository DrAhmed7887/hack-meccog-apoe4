#!/usr/bin/env python3
"""Verify deterministic docs/data/explorer_data.json against frozen Step 1 data and CIFs."""
import json
import re
import unittest

from scripts.build_explorer_data import H2_PATH, H5_PATH, OUT_PATH, ROOT, parse_cif_atoms

V2_DATA = ROOT / "video" / "remotion" / "src" / "v2" / "data.json"


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

        # the V2 film data must carry exactly the frozen totals (and nothing typed by hand)
        v2 = json.loads(V2_DATA.read_text(encoding="utf-8"))
        c = v2["counts"]
        self.assertEqual(c["H5"]["n_findings"], 67)
        self.assertEqual(c["H2"]["n_findings"], 53)
        self.assertEqual((c["H5"]["n_papers"], c["H2"]["n_papers"]), (19, 11))
        self.assertEqual((c["entries"], c["uniquePapers"], c["structures"]), (30, 28, 14))
        self.assertEqual((c["findings"], c["supporting"], c["contradicting"]), (120, 91, 29))
        self.assertEqual(c["supporting"] + c["contradicting"], c["H5"]["n_findings"] + c["H2"]["n_findings"])
        self.assertEqual(c["printedStats"], 126)
        self.assertEqual(c["H2"]["n_tier1"], 0)
        self.assertEqual((c["H5"]["n_unavailable"], c["H2"]["n_unavailable"], c["paywalled"]), (2, 2, 4))
        self.assertEqual(c["tier1Def"], "Human iPSC")
        for fid, keys in {"H5-P4.F1": ("cardTitle", "cardSub"), "H5-P6.F3": ("cardTitle", "cardSub"),
                          "H2-P2.F12": ("badge",), "H2-P3.F6": ("badge", "headline"), "H2-P5.F4": ("badge", "headline")}.items():
            for k in keys:
                val = v2["featured"][fid].get(k)
                self.assertTrue(isinstance(val, str) and val.strip(), f"{fid}.{k} must be a non-empty string")
        self.assertEqual(sorted(v2["featured"]), sorted(["H5-P4.F1", "H5-P6.F3", "H2-P2.F12", "H2-P3.F6", "H2-P5.F4"]))
        for fid, feat in v2["featured"].items():  # featured snippets are verbatim from explorer_data.json
            src = next(f for f in ex["findings"] if f["id"] == fid)
            self.assertEqual(feat["quote"], src["quote"])
            self.assertEqual(feat["pmid"], src["pmid"])
            self.assertEqual(feat["description"], src["description"])

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

        v2g = json.loads(V2_DATA.read_text(encoding="utf-8"))["geometry"]
        self.assertEqual((v2g["arg112"]["distance_A"], v2g["arg112"]["res1"], v2g["arg112"]["res2"]), (2.53, "ARG112.NH1", "GLU109.OE2"))
        self.assertEqual((v2g["arg61Apoe4"]["distance_A"], v2g["arg61Apoe4"]["res1"], v2g["arg61Apoe4"]["res2"]), (5.34, "ARG61.CG", "GLU109.OE2"))
        self.assertEqual((v2g["arg61Apoe3"]["distance_A"], v2g["arg61Apoe3"]["res1"], v2g["arg61Apoe3"]["res2"]), (3.53, "ARG61.NH2", "GLU109.CG"))
        self.assertEqual((v2g["arg112"]["struct"], v2g["arg61Apoe3"]["struct"]), ("1B68", "1NFN"))

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

        # V2: zero phonetic leftovers in scene words, captions and VTT file
        phonetic_v2 = (
            "a-p-o-e", "kep-ree", "h-two", "h-five", "c-five", "apo-e-r", "n-h-e-", "l-r-p", "v-a-t-p", "p-h ",
            "one-b", "one-n", "three-d", "three-fold", "one hundred", "two point", "sixty-one", "fifty-three",
            "forty-five", "seventy-four", "ninety-one", "twenty-", "thirty", "zero", "step one", "tier one",
            "angstrom", "arginine one", "arginine sixty", "glutamate one", "cysteine one", "l-t-p", "five point",
        )
        v2 = json.loads(V2_DATA.read_text(encoding="utf-8"))
        v2_texts = [w["w"] for sc in v2["scenes"] for w in sc["words"]] + [c["text"] for sc in v2["scenes"] for c in sc["captions"]]
        for name in ("captions.vtt",):
            vtt_path = ROOT / "docs" / "media" / name
            self.assertTrue(vtt_path.exists(), f"docs/media/{name} must exist")
            v2_texts.append(vtt_path.read_text(encoding="utf-8"))
        for text in v2_texts:
            for token in phonetic_v2:
                self.assertNotIn(token, text.lower(), f"phonetic token {token!r} in V2 caption: {text!r}")
        joined = " ".join(c["text"] for sc in v2["scenes"] for c in sc["captions"])
        for exact in ("APOE4", "APOE3", "Khepri", "Step 1", "Rule C5", "1B68", "1NFN", "Arg112", "Glu109", "Cys112", "Arg61",
                      "2.53 Å", "ApoER2", "NHE6", "pH", "LRP1", "3-fold", "53 of 84", "V-ATPases", "~45%", "0 Tier 1", "3D",
                      "LTP", "Arg61–Glu109", "3.53", "5.34 Å"):
            self.assertIn(exact, joined, f"{exact!r} missing from V2 captions")
        for sc in v2["scenes"]:
            for c in sc["captions"]:
                self.assertLessEqual(len(c["text"]), 64, f"V2 caption over 64 chars: {c['text']!r}")

        # scenes take featured numbers/PMIDs/card text from data.json, never as literals
        literals = ("35750033", "42182449", "29946028", "30375977", "34617884", "53 of 84", "3-fold", "45%")
        for tsx in (ROOT / "video" / "remotion" / "src" / "v2" / "scenes").glob("*.tsx"):
            src = tsx.read_text(encoding="utf-8")
            for lit in literals:
                self.assertNotIn(lit, src, f"hardcoded {lit!r} in {tsx.name}")

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

        # --- V2 pipeline: video/v2/build_data.py ---
        from video.v2.build_data import caption_chunks, normalize_aligned_words as norm2

        def texts(*ws):
            return [w["w"] for w in norm2(mk(*ws))]

        self.assertEqual(texts("one", "hundred", "twenty-six"), ["126"])
        self.assertEqual(texts("one", "hundred", "twenty"), ["120"])
        self.assertEqual(texts("arginine", "one", "hundred", "twelve,"), ["Arg112,"])
        self.assertEqual(texts("cysteine", "one", "hundred", "twelve"), ["Cys112"])
        self.assertEqual(texts("two", "point", "five", "three", "Angstrom"), ["2.53 Å"])
        self.assertEqual(texts("A-P-O-E-four's", "arginine", "sixty-one"), ["APOE4's", "Arg61"])
        self.assertEqual(texts("Team", "Kep-ree", "built", "Step", "one", "sheets"), ["Team", "Khepri", "built", "Step 1", "sheets"])
        self.assertEqual(texts("under", "Rule", "C-five,", "zero", "predicted"), ["under", "Rule C5,", "0 predicted"])
        self.assertEqual(texts("H-two", "holds", "zero", "Tier", "one", "papers,"), ["H2", "holds", "0 Tier 1", "papers,"])
        self.assertEqual(texts("drops", "about", "forty-five", "percent,"), ["drops", "~45%,"])
        self.assertEqual(texts("forty-five", "percent"), ["45%"])
        self.assertEqual(texts("fifty-three", "of", "eighty-four"), ["53 of 84"])
        self.assertEqual(texts("sets", "p-H."), ["sets", "pH."])
        self.assertEqual(texts("thirty", "entries;"), ["30 entries;"])
        self.assertEqual(texts("thirty", "days"), ["thirty", "days"])  # bare 'thirty' is untouched
        self.assertEqual(texts("restores", "Reelin-enhanced", "L-T-P."), ["restores", "Reelin-enhanced", "LTP."])
        self.assertEqual(texts("from", "three", "point", "five", "three", "to"), ["from", "3.53", "to"])
        self.assertEqual(texts("five", "point", "three", "four", "Angstroms."), ["5.34 Å."])
        self.assertEqual(texts("arginine", "sixty-one", "to", "glutamate", "one", "hundred", "nine"), ["Arg61–Glu109"])
        words = mk("two", "point", "five", "three", "Angstrom")
        merged = norm2(words)[0]
        self.assertEqual((merged["start"], merged["end"]), (words[0]["start"], words[-1]["end"]))
        plain2 = mk("the", "protein", "folds")
        self.assertEqual(norm2(plain2), plain2)

        # caption_chunks: sentence-aware, <= 64 chars, no words lost or reordered
        sent = mk(*("Meanwhile, H2 holds 0 Tier 1 papers, and 4 paywalled entries stay abstract-only. Short one.".split()))
        chunks = caption_chunks(sent)
        self.assertTrue(all(len(c["text"]) <= 64 for c in chunks))
        self.assertEqual(" ".join(c["text"] for c in chunks), " ".join(w["w"] for w in sent))
        self.assertEqual(chunks[-1]["text"], "Short one.")


if __name__ == "__main__":
    unittest.main()
