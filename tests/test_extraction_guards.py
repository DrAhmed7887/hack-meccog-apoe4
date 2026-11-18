import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import extract  # noqa: E402
import to_template  # noqa: E402


with open(os.path.join(HERE, "fixtures", "rab5_rab7_sentence.txt"), encoding="utf-8") as f:
    RAB_SENTENCE = f.read().strip()


def finding(readout, directness_class=1, directness_strength=3, effect="d = 2.8", p_value="0.02"):
    return {
        "description": f"RAB{readout} endosome marker levels in APOE4 versus APOE3 microglia",
        "quote": RAB_SENTENCE,
        "summary": f"(APOE4 genotype) -> (RAB{readout} endosome marker levels)",
        "direction": "neutral",
        "relevance": 0.7,
        "experimental_system": "primary mouse microglia",
        "directness_class": directness_class,
        "directness_strength": directness_strength,
        "effect_size": {"value": effect, "quote": RAB_SENTENCE},
        "p_value": {"value": p_value, "quote": RAB_SENTENCE},
        "sample_size": {"value": None, "quote": None},
    }


class MultiReadout(unittest.TestCase):
    def test_keeps_only_the_named_readout_segment(self):
        c = extract.clean_finding(finding("7"), RAB_SENTENCE)
        self.assertEqual(c["effect_size"]["value"], "d = 2.8")
        self.assertEqual(c["p_value"]["value"], "0.02")
        self.assertTrue(c["effect_size"]["quote"].startswith("RAB7:"))
        self.assertNotIn("RAB5:", c["effect_size"]["quote"])
        self.assertFalse(c["physician_review"])

    def test_rejects_neighbor_readout_numbers_and_marks_review(self):
        c = extract.clean_finding(finding("5"), RAB_SENTENCE)
        self.assertIsNone(c["effect_size"]["value"])  # 2.8 is t, not d, in RAB5
        self.assertIsNone(c["p_value"]["value"])      # p = 0.02 belongs to RAB7
        self.assertTrue(c["physician_review"])
        self.assertIn("readout_stat_mismatch", c["physician_review_reasons"])

    def test_unmatched_readout_drops_numbers_and_marks_review(self):
        f = finding("7")
        f["description"] = "Endosome markers changed in APOE4 versus APOE3 microglia"
        f["summary"] = "(APOE4 genotype) -> (changed endosome markers)"
        c = extract.clean_finding(f, RAB_SENTENCE)
        self.assertIsNone(c["effect_size"]["value"])
        self.assertIsNone(c["p_value"]["value"])
        self.assertTrue(c["physician_review"])
        self.assertIn("ambiguous_readout", c["physician_review_reasons"])
        row = to_template.build_rows("HYP", [{"pmid": "35031484", "findings": [c]}])[3]
        self.assertTrue(row[5].startswith(to_template.REVIEW_MARKER))

    def test_numerically_equivalent_but_not_verbatim_is_refused(self):
        self.assertIsNone(extract.verify_stat("effect_size", "d = 2.80", "RAB7: d = 2.8", RAB_SENTENCE))
        self.assertIsNone(extract.verify_stat("p_value", "0.020", "RAB7: p = 0.02", RAB_SENTENCE))


class DirectnessPair(unittest.TestCase):
    def test_class_one_weak_strength_is_flagged_and_visible_in_template(self):
        c = extract.clean_finding(finding("7", directness_class=1, directness_strength=4), RAB_SENTENCE)
        self.assertTrue(c["physician_review"])
        self.assertIn("inconsistent_directness_pair", c["physician_review_reasons"])
        paper = {"pmid": "35031484", "findings": [c]}
        row = to_template.build_rows("HYP", [paper])[3]
        self.assertTrue(row[5].startswith(to_template.REVIEW_MARKER))
        self.assertEqual(row[17:19], ["1", "4 weak"])
        # Export also catches the bad pair in older JSON without the new flag.
        legacy = dict(c)
        legacy.pop("physician_review")
        row = to_template.build_rows("HYP", [{"pmid": "35031484", "findings": [legacy]}])[3]
        self.assertTrue(row[5].startswith(to_template.REVIEW_MARKER))

    def test_class_four_cannot_be_marked_strongest_without_review(self):
        c = extract.clean_finding(finding("7", directness_class=4, directness_strength=2), RAB_SENTENCE)
        self.assertTrue(c["physician_review"])
        self.assertIn("inconsistent_directness_pair", c["physician_review_reasons"])


if __name__ == "__main__":
    unittest.main()
