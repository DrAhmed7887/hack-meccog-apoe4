#!/usr/bin/env python3
"""Deterministic PMID/DOI existence check (Rule C4: official/rules.html:543-544).

Verifies every paper's PMID and DOI against local caches and (unless --offline)
PubMed efetch + Europe PMC REST, writing a verification log JSON.
Usage: python3 verify_ids.py --in out/extracted.json --out out/id_verification.json [--offline]
"""
import argparse
import datetime
import json
import os
import re
import sys
import urllib.parse

import common
import search

EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"
RE_PMID = re.compile(r"^\d+$")
RE_DOI = re.compile(r"^10\.\d{4,9}/\S+$", re.I)


def _norm_title(s):
    return re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).strip()


def _title_match(a, b):
    na, nb = _norm_title(a), _norm_title(b)
    if not na or not nb:
        return True
    return na[:40] == nb[:40] or na in nb or nb in na


def load_cache_records(cache_paths, fulltext_dir):
    by_pmid = {}
    for p in cache_paths:
        if p and os.path.exists(p):
            d = common.load_json(p)
            for r in d.get("records", d.get("papers", [])):
                pmid = str(r.get("pmid") or "").strip()
                if pmid and pmid not in by_pmid:
                    by_pmid[pmid] = r
    if fulltext_dir and os.path.isdir(fulltext_dir):
        for name in os.listdir(fulltext_dir):
            if name.endswith(".json"):
                pmid = name[:-5]
                ft = common.load_json(os.path.join(fulltext_dir, name))
                if pmid not in by_pmid:
                    by_pmid[pmid] = ft
    return by_pmid


def fetch_epmc_by_pmid(pmid):
    raw = common.http_get(
        EPMC_SEARCH,
        {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "lite"},
        min_interval=0.2,
    )
    hits = json.loads(raw).get("resultList", {}).get("result", [])
    for h in hits:
        if str(h.get("pmid") or h.get("id") or "").strip() == str(pmid):
            return {"pmid": str(pmid), "doi": (h.get("doi") or "").strip(), "title": (h.get("title") or "").strip()}
    return None


def verify_papers(papers, offline=False, cache_paths=(), fulltext_dir="out/fulltext"):
    """Verify PMID/DOI format, uniqueness, cache match, and (when online) PubMed + Europe PMC existence."""
    cache = load_cache_records(cache_paths, fulltext_dir)
    valid_pmids = [str(p.get("pmid") or "").strip() for p in papers if RE_PMID.match(str(p.get("pmid") or "").strip())]
    pubmed_map = {}
    if not offline and valid_pmids:
        for rec in search.efetch(valid_pmids, common.ncbi_key()):
            pubmed_map[str(rec.get("pmid") or "").strip()] = rec

    seen_pmids, seen_dois = {}, {}
    results = []
    for p in papers:
        pmid = str(p.get("pmid") or "").strip()
        doi = str(p.get("doi") or "").strip()
        title = str(p.get("title") or "").strip()
        errs = []

        pmid_ok = bool(RE_PMID.match(pmid))
        if not pmid_ok:
            errs.append(f"invalid PMID {pmid!r}")
        elif pmid in seen_pmids:
            errs.append(f"duplicate PMID {pmid}")
        else:
            seen_pmids[pmid] = True

        doi_is_na = doi.lower() in ("", "n/a")
        doi_ok = (not doi_is_na) and bool(RE_DOI.match(doi))
        if not doi_ok:
            errs.append(f"missing or invalid DOI {doi!r}")
        else:
            dl = doi.lower()
            if dl in seen_dois:
                errs.append(f"duplicate DOI {doi}")
            else:
                seen_dois[dl] = pmid

        c_rec = cache.get(pmid)
        cache_match = False
        if c_rec is not None:
            c_doi = str(c_rec.get("doi") or "").strip()
            cache_match = (not c_doi or not doi or c_doi.lower() == doi.lower()) and _title_match(title, c_rec.get("title", ""))
            if not cache_match:
                errs.append(f"cache metadata mismatch for PMID {pmid}")

        pm_exists = pm_doi_match = False
        ep_exists = ep_doi_match = False
        if not offline and pmid_ok:
            pm = pubmed_map.get(pmid)
            if pm:
                pm_exists = True
                pm_doi = str(pm.get("doi") or "").strip()
                pm_doi_match = (not pm_doi or not doi or pm_doi.lower() == doi.lower())
                if not pm_doi_match:
                    errs.append(f"PubMed DOI {pm_doi!r} != {doi!r}")
                if not _title_match(title, pm.get("title", "")):
                    errs.append("PubMed title mismatch")
            else:
                errs.append(f"PMID {pmid} not found in PubMed")

            ep = fetch_epmc_by_pmid(pmid)
            if ep:
                ep_exists = True
                ep_doi = str(ep.get("doi") or "").strip()
                ep_doi_match = (not ep_doi or not doi or ep_doi.lower() == doi.lower())
                if not ep_doi_match:
                    errs.append(f"Europe PMC DOI {ep_doi!r} != {doi!r}")
            else:
                errs.append(f"PMID {pmid} not found in Europe PMC")
        elif offline and c_rec is None:
            errs.append(f"PMID {pmid} absent from local cache in offline mode")

        results.append({
            "pmid": pmid,
            "doi": doi,
            "title": title,
            "pmid_valid_format": pmid_ok,
            "doi_valid_format": doi_ok,
            "cache_match": cache_match,
            "pubmed_exists": pm_exists,
            "pubmed_doi_match": pm_doi_match,
            "epmc_exists": ep_exists,
            "epmc_doi_match": ep_doi_match,
            "verified": not errs,
            "errors": errs,
        })

    n_ok = sum(1 for r in results if r["verified"])
    return {
        "checked_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "mode": "offline_cache" if offline else "live_pubmed_epmc",
        "n_papers": len(results),
        "n_verified": n_ok,
        "n_failed": len(results) - n_ok,
        "verified_all": len(results) > 0 and n_ok == len(results),
        "papers": results,
    }


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--in", dest="inp", default="out/extracted.json")
    ap.add_argument("--out", default="out/id_verification.json")
    ap.add_argument("--offline", action="store_true")
    ap.add_argument("--cache-json", action="append", default=["out/dd/pool_H5.json", "out/screened.json"])
    ap.add_argument("--fulltext", default="out/fulltext")
    a = ap.parse_args()
    d = common.load_json(a.inp)
    papers = d.get("papers", d.get("records", []))
    log = verify_papers(papers, offline=a.offline, cache_paths=a.cache_json, fulltext_dir=a.fulltext)
    common.save_json(log, a.out)
    print(f"id_verification ({log['mode']}): {log['n_verified']}/{log['n_papers']} verified -> {a.out}")
    if not log["verified_all"]:
        for r in log["papers"]:
            if not r["verified"]:
                print(f"  FAIL PMID {r['pmid']}: {'; '.join(r['errors'])}")
        sys.exit(1)


if __name__ == "__main__":
    main()
