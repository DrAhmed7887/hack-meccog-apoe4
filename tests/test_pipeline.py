import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)

import check_schema  # noqa: E402
import common  # noqa: E402
import extract  # noqa: E402
import fulltext  # noqa: E402
import parse_hypotheses  # noqa: E402
import screen  # noqa: E402
import search  # noqa: E402
import snowball  # noqa: E402
import to_template  # noqa: E402
import verify_sample  # noqa: E402


def fx(name):
    with open(os.path.join(HERE, "fixtures", name), encoding="utf-8") as f:
        return f.read()


ABS = "Cholesterol was 35% higher in APOE4 astrocytes (n = 6, P < 0.001). Lysosomes were enlarged."


class Search(unittest.TestCase):
    def test_esearch(self):
        self.assertEqual(search.parse_esearch(fx("esearch.json")), (71, ["111", "222", "333"]))

    def test_efetch(self):
        r = search.parse_efetch(fx("efetch.xml"))
        self.assertEqual([x["pmid"] for x in r], ["111", "222"])
        self.assertEqual(r[0]["doi"], "10.1016/j.x.2023.1")
        self.assertEqual(r[0]["pmcid"], "PMC999")
        self.assertEqual(r[0]["title"], "ApoE4 lysosomal cholesterol accumulation.")
        self.assertTrue(r[0]["abstract"].startswith("RESULTS: Cholesterol was 35% higher"))
        self.assertIn("Lysosomes were enlarged.", r[0]["abstract"])
        self.assertEqual(r[1]["abstract"], "")
        self.assertEqual(r[1]["year"], "2019")


class Snowball(unittest.TestCase):
    def test_refs_and_cites(self):
        r = snowball.parse_epmc_list(fx("epmc_refs.json"))
        self.assertEqual(r[0], {"pmid": "28000001", "doi": "10.1/a", "title": "Ref one.", "year": "2016"})
        self.assertEqual(r[1]["pmid"], "")
        c = snowball.parse_epmc_list(fx("epmc_cites.json"))
        self.assertEqual(c[0]["pmid"], "35000002")


class Json(unittest.TestCase):
    def test_extract_json(self):
        self.assertEqual(common.extract_json('```json\n{"a":1}\n```'), {"a": 1})
        self.assertEqual(common.extract_json('Sure! Here: [{"x": 2}] done'), [{"x": 2}])
        with self.assertRaises(ValueError):
            common.extract_json("no json here")


class Screen(unittest.TestCase):
    recs = [{"pmid": "1"}, {"pmid": "2"}, {"pmid": "3"}]

    def test_parse(self):
        reply = [{"pmid": "1", "include": True, "relevance": 1.7, "direction": "supports", "reason": "x"},
                 {"pmid": "2", "include": "yes"}]
        out = screen.parse_screen_reply(reply, self.recs)
        self.assertTrue(out["1"]["include"])
        self.assertEqual(out["1"]["relevance"], 1.0)
        self.assertFalse(out["2"]["include"])  # non-bool verdict is rejected
        self.assertFalse(out["3"]["include"])  # missing
        self.assertFalse(screen.parse_screen_reply(None, self.recs)["1"]["include"])


class Extract(unittest.TestCase):
    def test_quote(self):
        self.assertTrue(extract.quote_in_text("Cholesterol was 35%  higher in APOE4", ABS))
        self.assertFalse(extract.quote_in_text("Cholesterol was 40% higher", ABS))

    def test_verify(self):
        q = "Cholesterol was 35% higher in APOE4 astrocytes (n = 6, P < 0.001)"
        self.assertEqual(extract.verify_stat("effect_size", "35%", q, ABS), "35%")
        self.assertIsNone(extract.verify_stat("effect_size", "~35%", q, ABS))       # estimates refused
        self.assertIsNone(extract.verify_stat("effect_size", "40%", q, ABS))        # number not in quote
        self.assertIsNone(extract.verify_stat("effect_size", "35%", "invented sentence here", ABS))
        self.assertEqual(extract.verify_stat("p_value", "<0.001", q, ABS), "<0.001")
        self.assertEqual(extract.verify_stat("sample_size", "6", q, ABS), "6")
        self.assertIsNone(extract.verify_stat("sample_size", "six", q, ABS))
        self.assertIsNone(extract.verify_stat("p_value", None, None, ABS))
        self.assertIsNone(extract.verify_stat("p_value", "null", q, ABS))

    def test_clean_finding(self):
        f = {"description": "More cholesterol", "quote": "Cholesterol was 35% higher in APOE4 astrocytes",
             "summary": "(E4) -> (more chol)", "direction": "supports", "relevance": 0.8,
             "experimental_system": "astrocytes", "directness_class": 1, "directness_strength": "2",
             "effect_size": {"value": "35%", "quote": "Cholesterol was 35% higher in APOE4 astrocytes"},
             "p_value": {"value": "0.05", "quote": "made up quote not in abstract"},
             "sample_size": {"value": None, "quote": None}}
        c = extract.clean_finding(f, ABS)
        self.assertEqual(c["effect_size"]["value"], "35%")
        self.assertIsNone(c["p_value"]["value"])
        self.assertEqual(c["directness_strength"], 2)
        f["quote"] = "fabricated finding sentence"
        self.assertIsNone(extract.clean_finding(f, ABS))


class Fulltext(unittest.TestCase):
    def test_jats_blocks(self):
        b = fulltext.parse_jats(fx("pmc_article.xml"))
        locs = [x["loc"] for x in b]
        self.assertIn("Results > Lysosomal cholesterol", locs)
        self.assertIn("Table 2", locs)
        self.assertIn("Figure 3 legend", locs)       # figure in floats-group, outside body
        t = next(x for x in b if x["loc"] == "Table 2")
        self.assertIn("CE | 2.5x", t["text"])
        p = next(x for x in b if x["loc"].startswith("Results >"))
        self.assertIn("35% increase in APOE4 astrocytes (n = 6, P < 0.001)", p["text"])  # entities decoded, italics merged
        self.assertEqual(fulltext.parse_jats("<article><front/></article>"), [])
        self.assertEqual(fulltext.parse_jats("not xml"), [])

    def test_real_body(self):
        b = fulltext.parse_jats(fx("pmc_article.xml"))
        self.assertFalse(fulltext.has_real_body(b))  # tiny: front matter / non-OA record
        big = [{"loc": "Results > A", "kind": "text", "text": "x" * 9000}]
        self.assertTrue(fulltext.has_real_body(big))
        landing = [{"loc": "SUMMARY", "kind": "text", "text": "y" * 9000}]
        self.assertFalse(fulltext.has_real_body(landing))  # long but no Results heading and under 20k
        dup = [{"loc": "Results", "kind": "text", "text": "z" * 9000}] * 5
        self.assertTrue(fulltext.has_real_body(dup))      # duplicates counted once, still >= 8000

    def test_id_routes(self):
        self.assertEqual(fulltext.parse_idconv(fx("idconv.json"))["pmcid"], "PMC999")
        self.assertEqual(fulltext.parse_idconv(fx("idconv_missing.json"))["pmcid"], "")
        self.assertEqual(fulltext.parse_idconv("garbage")["pmcid"], "")
        self.assertEqual(fulltext.parse_epmc_lookup(fx("epmc_lookup.json")), {"pmcid": "PMC999", "open": True})
        self.assertEqual(fulltext.parse_epmc_lookup('{"resultList":{"result":[]}}')["pmcid"], "")

    def test_unpaywall(self):
        c = fulltext.parse_unpaywall(fx("unpaywall.json"))
        self.assertEqual(c[0][0], "html")
        self.assertIn(("pdf", "https://repo.example.org/a.pdf"), c)
        self.assertEqual(fulltext.parse_unpaywall(fx("unpaywall_closed.json")), [])
        self.assertEqual(fulltext.parse_unpaywall("nope"), [])

    def test_contact_is_not_personal(self):
        self.assertTrue(fulltext.CONTACT.endswith("users.noreply.github.com"))

    def test_html_blocks(self):
        b = fulltext.parse_html(fx("oa_page.html"))
        self.assertEqual([x["loc"] for x in b], ["Results", "Methods"])
        self.assertIn("35% more cholesterol", b[0]["text"])
        self.assertNotIn("menu", " ".join(x["text"] for x in b))


class FulltextExtract(unittest.TestCase):
    blocks = [{"loc": "Results > Lysosomal cholesterol", "kind": "text",
               "text": "Filipin staining showed a 35% increase in APOE4 astrocytes (n = 6, P < 0.001). Lysosomes were enlarged."},
              {"loc": "Table 2", "kind": "table", "text": "Lipid species.\nCE | 2.5x"},
              {"loc": "Results > Other", "kind": "text", "text": "Mitochondrial respiration fell in APOE4 cells (P = 0.02)."}]

    def finding(self, **kw):
        f = {"description": "More cholesterol", "quote": "Filipin staining showed a 35% increase in APOE4 astrocytes",
             "summary": "(E4) -> (more chol)", "direction": "supports", "relevance": 0.9, "experimental_system": "astrocytes",
             "directness_class": 1, "directness_strength": 2,
             "effect_size": {"value": "35%", "quote": "a 35% increase in APOE4 astrocytes"},
             "p_value": {"value": "<0.001", "quote": "(n = 6, P < 0.001)"},
             "sample_size": {"value": "6", "quote": "(n = 6, P < 0.001)"}}
        f.update(kw)
        return f

    def test_verbatim_and_location(self):
        c = extract.clean_ft_finding(self.finding(), self.blocks)
        self.assertEqual(c["location"], "Results > Lysosomal cholesterol")
        self.assertEqual((c["effect_size"]["value"], c["p_value"]["value"], c["sample_size"]["value"]), ("35%", "<0.001", "6"))
        self.assertEqual(c["source"], "full_text")

    def test_invented_finding_rejected(self):
        self.assertIsNone(extract.clean_ft_finding(self.finding(quote="Cholesterol doubled in APOE4 astrocytes."), self.blocks))

    def test_numbers_must_be_in_same_block(self):
        # P value quote exists in the paper, but in another block: refused (null), finding kept
        f = self.finding(p_value={"value": "0.02", "quote": "fell in APOE4 cells (P = 0.02)"})
        c = extract.clean_ft_finding(f, self.blocks)
        self.assertIsNone(c["p_value"]["value"])
        self.assertEqual(c["effect_size"]["value"], "35%")

    def test_never_estimated_or_computed(self):
        f = self.finding(p_value={"value": "0.0005", "quote": "(n = 6, P < 0.001)"},     # not the printed digits
                         effect_size={"value": "~35%", "quote": "a 35% increase in APOE4 astrocytes"},  # estimate marker
                         sample_size={"value": "6", "quote": "an invented clause about n = 6 mice"})    # quote not in source
        c = extract.clean_ft_finding(f, self.blocks)
        for k in ("p_value", "effect_size", "sample_size"):
            self.assertIsNone(c[k]["value"], k)

    def test_table_location(self):
        f = self.finding(quote="CE | 2.5x", effect_size={"value": "2.5x", "quote": "CE | 2.5x"},
                         p_value={"value": None, "quote": None}, sample_size={"value": None, "quote": None})
        c = extract.clean_ft_finding(f, self.blocks)
        self.assertEqual(c["location"], "Table 2")
        self.assertEqual(c["effect_size"]["value"], "2.5x")

    def test_chunking(self):
        blocks = [{"loc": "Introduction", "kind": "text", "text": "APOE4 cholesterol lysosome. " * 20},
                  {"loc": "Methods", "kind": "text", "text": "APOE4 cholesterol. " * 20},
                  {"loc": "Results > A", "kind": "text", "text": "APOE4 cholesterol lysosome. " * 100},
                  {"loc": "Results > B", "kind": "text", "text": "APOE4 lipid droplet. " * 100},
                  {"loc": "Results > C", "kind": "text", "text": "nothing relevant here at all. " * 50}]
        ch = extract.select_chunks(blocks, budget=6000, size=3000)
        locs = [b["loc"] for c in ch for b in c]
        self.assertEqual(locs, ["Results > A", "Results > B"])   # only Results, only relevant, document order
        self.assertTrue(all(sum(len(b["text"]) for b in c) <= 3000 for c in ch))
        self.assertIn("[[Results > A]]", extract.format_chunk(ch[0]))

    def test_template_full_text_provenance(self):
        c = extract.clean_ft_finding(self.finding(p_value={"value": None, "quote": None}), self.blocks)
        paper = {"pmid": "1", "doi": "10.1/x", "findings": [c]}
        row = to_template.build_rows("HYP", [paper])[3]
        self.assertEqual(row[10], "Results > Lysosomal cholesterol")
        self.assertEqual(row[13:15], ["N/A", "not_found_in_source"])
        self.assertEqual(row[11:13], ["35%", "printed_in_text"])


class Verify(unittest.TestCase):
    blocks = [{"loc": "Results > A", "kind": "text", "text": "Cells grew. Filipin staining showed a 35% increase in APOE4 astrocytes (n = 6, P < 0.001). Done."}]

    def test_found_and_sentence(self):
        ok, sent, loc = verify_sample.check_field("effect_size", {"value": "35%", "quote": "a 35% increase in APOE4 astrocytes"}, self.blocks)
        self.assertTrue(ok)
        self.assertEqual(loc, "Results > A")
        self.assertEqual(sent, "Filipin staining showed a 35% increase in APOE4 astrocytes (n = 6, P < 0.001).")

    def test_not_found(self):
        self.assertFalse(verify_sample.check_field("p_value", {"value": "0.05", "quote": "P = 0.05 in all groups"}, self.blocks)[0])
        # quote present but digits not in it
        self.assertFalse(verify_sample.check_field("effect_size", {"value": "40%", "quote": "a 35% increase in APOE4 astrocytes"}, self.blocks)[0])


class Hypotheses(unittest.TestCase):
    def test_official(self):
        h = parse_hypotheses.parse_hypotheses(open(os.path.join(ROOT, "official", "hypotheses.html"), encoding="utf-8").read())
        self.assertEqual(sorted(h), ["H1", "H2", "H3", "H4", "H5"])
        self.assertTrue(h["H1"]["statement"].startswith("In some types of non-Alzheimer's"))
        self.assertEqual(h["H5"]["start_pmid"], "37777962")


class Template(unittest.TestCase):
    papers = [{"pmid": "111", "doi": "10.1016/j.x.2023.1", "findings": [{
        "description": "d", "quote": "q" * 10, "summary": "(a) -> (b)", "direction": "contradicts", "relevance": 0.5,
        "experimental_system": "cells", "directness_class": 1, "directness_strength": 2,
        "effect_size": {"value": "35%", "quote": "x"}, "p_value": {"value": None, "quote": None},
        "sample_size": {"value": "6", "quote": "x"}}]}, {"pmid": "9", "findings": []}]

    def test_rows_and_roundtrip(self):
        rows = to_template.build_rows("HYP", self.papers)
        self.assertEqual(len(rows), 4)  # header, hypothesis, paper, finding (empty paper skipped)
        self.assertEqual(rows[3][4], "P1.F1")
        self.assertTrue(rows[3][5].startswith("CONTRADICTING: "))
        self.assertEqual(rows[3][11:19], ["35%", "printed_in_text", "N/A", "full_text_unavailable", "6", "printed_in_text", "1", "2 strong"])
        with tempfile.TemporaryDirectory() as t:
            p = os.path.join(t, "x.xlsx")
            to_template.write_xlsx(p, [("Submission", rows), ("Method", to_template.build_method(to_template.DRY_METHOD))])
            self.assertEqual(check_schema.check(p), [])

    def test_header_matches_official_template(self):
        sh = check_schema.read_rows(os.path.join(ROOT, "official", "resources", "submission_template.xlsx"))
        self.assertEqual(sh["Submission"][0], to_template.COLUMNS)
        self.assertEqual([r[0] for r in sh["Method"]], to_template.METHOD_ROWS)

    def test_xml_escaping(self):
        rows = [["a<b&c\x01"]]
        x = to_template.sheet_xml(rows)
        self.assertIn("a&lt;b&amp;c", x)
        self.assertNotIn("\x01", x)


if __name__ == "__main__":
    unittest.main()
