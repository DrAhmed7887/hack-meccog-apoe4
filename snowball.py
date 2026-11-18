#!/usr/bin/env python3
"""Citation snowballing with Europe PMC REST: references and citations of seed PMIDs.
Usage: python3 snowball.py --seed 29946028 --max 20 --out out/snowball.json
Seeds: --seed PMID (repeatable) and/or --from out/screened.json (included papers)."""
import argparse
import json

import common

EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"


def parse_epmc_list(text):
    """Europe PMC references/citations JSON -> list of {pmid, doi, title, year}. Items without a PMID are kept
    (doi may be present) since not everything is in PubMed."""
    d = json.loads(text)
    items = d.get("referenceList", {}).get("reference") or d.get("citationList", {}).get("citation") or []
    out = []
    for it in items:
        pmid = str(it.get("id") or "") if it.get("source") == "MED" else str(it.get("pmid") or "")
        out.append({"pmid": pmid, "doi": it.get("doi") or "", "title": (it.get("title") or it.get("tit") or "").strip(),
                    "year": str(it.get("pubYear") or it.get("pubyear") or "")})
    return out


def fetch(kind, pmid, cap):
    out, page = [], 1
    while len(out) < cap:
        txt = common.http_get(f"{EPMC}MED/{pmid}/{kind}", {"format": "json", "pageSize": min(100, cap), "page": page},
                              min_interval=0.2)
        got = parse_epmc_list(txt)
        if not got:
            break
        out += got
        if len(got) < min(100, cap):
            break
        page += 1
    return out[:cap]


def snowball(seeds, cap):
    found = {}
    for s in seeds:
        for kind in ("references", "citations"):
            for it in fetch(kind, s, cap):
                k = it["pmid"] or it["doi"] or it["title"]
                if k and k not in found:
                    found[k] = dict(it, via=f"{kind}:{s}")
    return list(found.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", action="append", default=[])
    ap.add_argument("--from", dest="frm")
    ap.add_argument("--max", type=int, default=20, help="cap per seed per direction")
    ap.add_argument("--out", default="out/snowball.json")
    a = ap.parse_args()
    seeds = list(a.seed)
    if a.frm:
        seeds += [r["pmid"] for r in common.load_json(a.frm)["records"] if r.get("screen", {}).get("include")]
    res = snowball(seeds, a.max)
    common.save_json({"seeds": seeds, "n": len(res), "candidates": res}, a.out)
    print(f"snowball: {len(seeds)} seed(s) -> {len(res)} unique candidates ({sum(1 for r in res if r['pmid'])} with PMID) -> {a.out}")


if __name__ == "__main__":
    main()
