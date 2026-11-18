#!/usr/bin/env python3
"""PubMed E-utilities search: esearch (PMIDs + total count) then efetch (title, abstract, DOI).
Usage: python3 search.py --hyp H5 --max 20 --out out/search.json [--count-only]
NCBI key from Keychain (NCBI_API_KEY); at most ~8 requests/second."""
import argparse
import json
import xml.etree.ElementTree as ET

import common

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"


def parse_esearch(text):
    """esearch JSON -> (total_count, [pmid])."""
    r = json.loads(text)["esearchresult"]
    return int(r["count"]), list(r.get("idlist", []))


def _txt(el):
    return "".join(el.itertext()).strip() if el is not None else ""


def parse_efetch(xml_text):
    """efetch PubmedArticleSet XML -> list of records. Abstract sections keep their labels."""
    root = ET.fromstring(xml_text)
    out = []
    for art in root.findall("PubmedArticle"):
        cit = art.find("MedlineCitation")
        pmid = _txt(cit.find("PMID"))
        a = cit.find("Article")
        title = _txt(a.find("ArticleTitle"))
        parts = []
        for ab in a.findall("Abstract/AbstractText"):
            label = ab.get("Label")
            t = _txt(ab)
            if t:
                parts.append(f"{label}: {t}" if label else t)
        doi = ""
        for aid in art.findall("PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "doi":
                doi = _txt(aid)
        pmc = ""
        for aid in art.findall("PubmedData/ArticleIdList/ArticleId"):
            if aid.get("IdType") == "pmc":
                pmc = _txt(aid)
        year = _txt(a.find("Journal/JournalIssue/PubDate/Year")) or _txt(a.find("Journal/JournalIssue/PubDate/MedlineDate"))[:4]
        ptypes = [_txt(p) for p in a.findall("PublicationTypeList/PublicationType")]
        out.append({"pmid": pmid, "title": title, "abstract": " ".join(parts), "doi": doi, "pmcid": pmc,
                    "year": year, "journal": _txt(a.find("Journal/Title")), "pub_types": ptypes})
    return out


def esearch(query, retmax, key=None):
    p = {"db": "pubmed", "term": query, "retmax": retmax, "retmode": "json", "sort": "relevance"}
    if key:
        p["api_key"] = key
    return parse_esearch(common.http_get(EUTILS + "esearch.fcgi", p))


def efetch(pmids, key=None):
    recs = []
    for i in range(0, len(pmids), 100):
        p = {"db": "pubmed", "id": ",".join(pmids[i:i + 100]), "retmode": "xml"}
        if key:
            p["api_key"] = key
        recs += parse_efetch(common.http_get(EUTILS + "efetch.fcgi", p))
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hyp", required=True)
    ap.add_argument("--max", type=int, default=20)
    ap.add_argument("--out", default="out/search.json")
    ap.add_argument("--query", help="override the query in queries.json")
    ap.add_argument("--count-only", action="store_true")
    a = ap.parse_args()
    query = a.query or common.load_json("queries.json")[a.hyp]
    key = common.ncbi_key()
    count, pmids = esearch(query, 0 if a.count_only else a.max, key)
    if a.count_only:
        print(f"{a.hyp}: {count} PubMed hits")
        return
    recs = efetch(pmids, key)
    common.save_json({"hyp": a.hyp, "query": query, "total_hits": count, "n_fetched": len(recs), "records": recs}, a.out)
    print(f"{a.hyp}: {count} hits total, fetched {len(recs)} ({sum(1 for r in recs if r['abstract'])} with abstract) -> {a.out}")


if __name__ == "__main__":
    main()
