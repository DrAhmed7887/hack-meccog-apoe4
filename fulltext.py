#!/usr/bin/env python3
"""Free full-text fetcher for the included papers. Standard library only (+ `pdftotext` if installed).
Usage: python3 fulltext.py --in out/screened.json --out out/fulltext_report.json [--max 13]

Routes, tried in this order per paper, stopping at the first that returns a real body:
  pmc_oa      NCBI idconv (PMID -> PMCID, only if the record has none) then efetch db=pmc (JATS XML)
  europepmc   Europe PMC REST fullTextXML for the PMCID (resolved from the PMID by a Europe PMC search)
  unpaywall   Unpaywall by DOI, open-access location only: HTML parsed, PDF via `pdftotext` if installed
Not used, by rule: institutional proxy, Sci-Hub, any login. Cache: out/fulltext/<pmid>.json (git-ignored) with
the text blocks and the route log. A paper is 'unavailable' only if every route was tried and failed; that log
is what makes full_text_unavailable legitimate (official rules, 'Paywalls').
NCBI_API_KEY comes from the Keychain inside common.ncbi_key() and is never printed (<= 10 requests/s)."""
import argparse
import html
from html.parser import HTMLParser
import json
import os
import re
import shutil
import subprocess
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET

import common

CONTACT = "meccog-pipeline@users.noreply.github.com"  # project address, not a person's
NCBI = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
EPMC = "https://www.ebi.ac.uk/europepmc/webservices/rest/"
IDCONV = "https://pmc.ncbi.nlm.nih.gov/tools/idconv/api/v1/articles/"
UNPAYWALL = "https://api.unpaywall.org/v2/"
MAX_BLOCK = 3500  # characters per block (long paragraphs are split on sentence ends)
MIN_BODY_CHARS = 8000  # below this a "full text" is front matter only (e.g. non-OA PMC record)


# ---------- text blocks ----------

def _itertext(el):
    """All text under an element (nested tags and tails included), whitespace collapsed."""
    return re.sub(r"\s+", " ", "".join(el.itertext())).strip()


def _split_long(text, limit=MAX_BLOCK):
    if len(text) <= limit:
        return [text]
    out, cur = [], ""
    for s in re.split(r"(?<=[.!?])\s+", text):
        if cur and len(cur) + len(s) + 1 > limit:
            out.append(cur)
            cur = s
        else:
            cur = (cur + " " + s).strip()
    if cur:
        out.append(cur)
    return out


def _table_text(tw):
    label = _itertext(tw.find("label")) if tw.find("label") is not None else ""
    cap = tw.find("caption")
    caption = _itertext(cap) if cap is not None else ""
    rows = []
    for tr in tw.iter("tr"):
        cells = [_itertext(c) for c in tr if c.tag in ("td", "th")]
        if any(cells):
            rows.append(" | ".join(cells))
    return label, caption, rows


def parse_jats(xml_text):
    """JATS XML -> list of blocks {loc, kind, text}. loc = 'Results > subsection title', 'Table 2', 'Figure 3 legend'.
    Returns [] if the XML has no body."""
    xml_text = re.sub(r"<!DOCTYPE[^>]*>", "", xml_text)
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return []
    body = next(root.iter("body"), None)
    if body is None:
        return []
    blocks = []

    def walk(sec, path):
        title_el = sec.find("title")
        title = _itertext(title_el) if title_el is not None else ""
        here = path + ([title] if title else [])
        loc = " > ".join(here) or "Body"
        for ch in sec:
            if ch.tag == "p":
                t = _itertext(ch)
                for piece in _split_long(t):
                    if piece:
                        blocks.append({"loc": loc, "kind": "text", "text": piece})
            elif ch.tag == "sec":
                walk(ch, here)
            elif ch.tag == "table-wrap":
                label, caption, rows = _table_text(ch)
                tl = label or "Table"
                blocks.append({"loc": tl, "kind": "table",
                               "text": (caption + "\n" + "\n".join(rows)).strip()[:MAX_BLOCK * 2]})
            elif ch.tag == "fig":
                label = _itertext(ch.find("label")) if ch.find("label") is not None else "Figure"
                cap = ch.find("caption")
                if cap is not None:
                    blocks.append({"loc": f"{label} legend", "kind": "legend", "text": _itertext(cap)})

    walk(body, [])
    # PMC XML often keeps figures and tables in <floats-group> or <back>, outside <body>: sweep the whole article
    have = {(b["kind"], b["loc"]) for b in blocks}
    for tw in root.iter("table-wrap"):
        label, caption, rows = _table_text(tw)
        key = ("table", label or "Table")
        if key not in have and (rows or caption):
            have.add(key)
            blocks.append({"loc": label or "Table", "kind": "table",
                           "text": (caption + "\n" + "\n".join(rows)).strip()[:MAX_BLOCK * 2]})
    for fg in root.iter("fig"):
        lab = fg.find("label")
        label = _itertext(lab) if lab is not None else "Figure"
        cap = fg.find("caption")
        key = ("legend", f"{label} legend")
        if cap is not None and key not in have:
            have.add(key)
            blocks.append({"loc": f"{label} legend", "kind": "legend", "text": _itertext(cap)})
    return blocks


class _Strip(HTMLParser):
    SKIP = {"script", "style", "nav", "header", "footer", "noscript", "svg", "form"}

    def __init__(self):
        super().__init__()
        self.skip = 0
        self.cur = []
        self.paras = []
        self.heading = "Body"

    def handle_starttag(self, tag, attrs):
        if tag in self.SKIP:
            self.skip += 1
        if tag in ("p", "div", "li", "h1", "h2", "h3", "h4", "tr", "br"):
            self._flush()

    def handle_endtag(self, tag):
        if tag in self.SKIP and self.skip:
            self.skip -= 1
        if tag in ("h1", "h2", "h3", "h4"):
            t = " ".join("".join(self.cur).split())
            self.cur = []
            if t:
                self.heading = t[:120]
        elif tag in ("p", "div", "li", "tr"):
            self._flush()

    def handle_data(self, data):
        if not self.skip:
            self.cur.append(data)

    def _flush(self):
        t = " ".join("".join(self.cur).split())
        self.cur = []
        if len(t) > 60:
            self.paras.append((self.heading, t))


def parse_html(page):
    """Open-access HTML page -> blocks (heading text as location). Paragraphs under 60 chars are dropped."""
    p = _Strip()
    try:
        p.feed(page)
        p._flush()
    except Exception:
        return []
    blocks = []
    for heading, t in p.paras:
        for piece in _split_long(html.unescape(t)):
            blocks.append({"loc": heading, "kind": "text", "text": piece})
    return blocks


def parse_pdf_text(text):
    """pdftotext output -> blocks. Locations are the nearest preceding short heading-like line."""
    blocks, heading, buf = [], "Body", []

    def flush():
        t = " ".join(" ".join(buf).split())
        buf.clear()
        for piece in _split_long(t):
            if len(piece) > 60:
                blocks.append({"loc": heading, "kind": "text", "text": piece})

    for line in text.splitlines():
        s = line.strip()
        if not s:
            flush()
            continue
        if len(s) < 70 and re.match(r"^(\d+\.?\s+)?[A-Z][A-Za-z ,&/-]{2,}$", s) and not s.endswith("."):
            flush()
            heading = s
        else:
            buf.append(s)
    flush()
    return blocks


def body_chars(blocks):
    return sum(len(b["text"]) for b in blocks)


def has_real_body(blocks):
    """Enough text, and it looks like an article (a Results heading, or a lot of distinct text), not a landing page."""
    uniq = {b["text"]: b for b in blocks}.values()
    n = sum(len(b["text"]) for b in uniq)
    return n >= MIN_BODY_CHARS and (n >= 20000 or any(re.search(r"result", b["loc"], re.I) for b in uniq))


# ---------- id resolution ----------

def parse_idconv(text):
    """idconv JSON -> {'pmcid':..., 'doi':...} (empty strings if none)."""
    try:
        recs = json.loads(text).get("records", [])
    except ValueError:
        return {"pmcid": "", "doi": ""}
    if recs and isinstance(recs[0], dict) and recs[0].get("status") != "error":
        return {"pmcid": recs[0].get("pmcid", "") or "", "doi": recs[0].get("doi", "") or ""}
    return {"pmcid": "", "doi": ""}


def parse_epmc_lookup(text):
    """Europe PMC search JSON -> {'pmcid','isOpenAccess'} for the first hit."""
    try:
        hits = json.loads(text).get("resultList", {}).get("result", [])
    except ValueError:
        return {"pmcid": "", "open": False}
    if not hits:
        return {"pmcid": "", "open": False}
    return {"pmcid": hits[0].get("pmcid", "") or "", "open": hits[0].get("isOpenAccess") == "Y"}


def parse_unpaywall(text):
    """Unpaywall JSON -> list of (kind, url) candidates, best first. Only OA locations are listed."""
    try:
        d = json.loads(text)
    except ValueError:
        return []
    if not isinstance(d, dict) or not d.get("is_oa"):
        return []
    locs = [d.get("best_oa_location")] + list(d.get("oa_locations") or [])
    out, seen = [], set()
    for loc in locs:
        if not isinstance(loc, dict):
            continue
        for kind, key in (("html", "url_for_landing_page"), ("pdf", "url_for_pdf")):
            u = loc.get(key)
            if u and (kind, u) not in seen:
                seen.add((kind, u))
                out.append((kind, u))
    # prefer PDF/landing pages of repositories and publishers alike; HTML first (no pdftotext needed)
    return sorted(out, key=lambda x: 0 if x[0] == "html" else 1)


# ---------- routes ----------

def _ncbi_params(extra):
    p = dict(extra)
    k = common.ncbi_key()
    if k:
        p["api_key"] = k
    return p


def route_pmc(rec, log):
    pmcid = rec.get("pmcid") or ""
    if not pmcid:
        try:
            r = common.http_get(IDCONV, {"ids": rec["pmid"], "format": "json", "tool": "meccog-pipeline", "email": CONTACT},
                                min_interval=0.12)
            pmcid = parse_idconv(r)["pmcid"]
        except Exception as e:  # noqa
            log.append({"route": "pmc_idconv", "ok": False, "why": str(e)[:80]})
    if not pmcid:
        log.append({"route": "pmc_oa", "ok": False, "why": "no PMCID"})
        return None, None
    try:
        xml = common.http_get(NCBI + "efetch.fcgi", _ncbi_params({"db": "pmc", "id": pmcid.replace("PMC", ""), "retmode": "xml"}),
                              min_interval=0.11)
        blocks = parse_jats(xml)
    except Exception as e:  # noqa
        log.append({"route": "pmc_oa", "ok": False, "why": str(e)[:80], "pmcid": pmcid})
        return None, pmcid
    ok = has_real_body(blocks)
    log.append({"route": "pmc_oa", "ok": ok, "pmcid": pmcid, "chars": body_chars(blocks),
                "why": "" if ok else "no full body (not in PMC open-access subset)"})
    return (blocks if ok else None), pmcid


def route_epmc(rec, pmcid, log):
    try:
        if not pmcid:
            r = common.http_get(EPMC + "search", {"query": f"EXT_ID:{rec['pmid']} AND SRC:MED", "format": "json",
                                                  "resultType": "lite"}, min_interval=0.2)
            look = parse_epmc_lookup(r)
            pmcid = look["pmcid"]
            if not pmcid:
                log.append({"route": "europepmc", "ok": False, "why": "no PMCID at Europe PMC"})
                return None
        xml = common.http_get(EPMC + f"{pmcid}/fullTextXML", min_interval=0.2)
        blocks = parse_jats(xml)
    except Exception as e:  # noqa
        log.append({"route": "europepmc", "ok": False, "why": str(e)[:80]})
        return None
    ok = has_real_body(blocks)
    log.append({"route": "europepmc", "ok": ok, "pmcid": pmcid, "chars": body_chars(blocks),
                "why": "" if ok else "no full body"})
    return blocks if ok else None


def _get_bytes(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; meccog-pipeline; open-access fetch)"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read(), r.headers.get("Content-Type", "")


def route_unpaywall(rec, log):
    doi = rec.get("doi") or ""
    if not doi:
        log.append({"route": "unpaywall", "ok": False, "why": "no DOI"})
        return None
    try:
        r = common.http_get(UNPAYWALL + urllib.parse.quote(doi, safe="/"), {"email": CONTACT}, min_interval=0.2, retries=2)
    except Exception as e:  # noqa
        log.append({"route": "unpaywall", "ok": False, "why": str(e)[:80]})
        return None
    cands = parse_unpaywall(r)
    if not cands:
        log.append({"route": "unpaywall", "ok": False, "why": "no open-access location"})
        return None
    return _try_urls(cands[:4], log)


def _try_urls(cands, log, prefix="unpaywall"):
    pdf_only = False
    for kind, url in cands:
        try:
            data, ctype = _get_bytes(url)
        except Exception as e:  # noqa
            log.append({"route": prefix + "_" + kind, "ok": False, "why": str(e)[:60]})
            continue
        is_pdf = data[:5] == b"%PDF-" or "pdf" in ctype.lower()
        if is_pdf:
            if not shutil.which("pdftotext"):
                pdf_only = True
                log.append({"route": prefix + "_pdf", "ok": False, "why": "pdf_only (pdftotext not installed)"})
                continue
            with tempfile.TemporaryDirectory() as t:
                p = os.path.join(t, "x.pdf")
                with open(p, "wb") as f:
                    f.write(data)
                res = subprocess.run(["pdftotext", "-layout", "-enc", "UTF-8", p, "-"], capture_output=True, text=True, timeout=120)
            blocks = parse_pdf_text(res.stdout)
        else:
            blocks = parse_html(data.decode("utf-8", errors="replace"))
        ok = has_real_body(blocks)
        log.append({"route": prefix + "_" + ("pdf" if is_pdf else "html"), "ok": ok, "chars": body_chars(blocks),
                    "why": "" if ok else "page had no readable article body (landing page or paywall)"})
        if ok:
            return blocks
    return {"pdf_only": True} if pdf_only else None


def route_doi(rec, log):
    """The DOI link itself (the publisher's own page), HTML or PDF, no login."""
    if not rec.get("doi"):
        log.append({"route": "doi_direct", "ok": False, "why": "no DOI"})
        return None
    return _try_urls([("html", "https://doi.org/" + rec["doi"])], log, prefix="doi_direct")


def fetch_one(rec):
    """Try every route. Returns dict: pmid, status (full_text | pdf_only | unavailable), route, log, blocks."""
    log = []
    blocks, pmcid = route_pmc(rec, log)
    route = "pmc_oa" if blocks else None
    if not blocks:
        blocks = route_epmc(rec, pmcid, log)
        route = "europepmc" if blocks else None
    pdf_only = False
    if not blocks:
        u = route_unpaywall(rec, log)
        if isinstance(u, dict):
            pdf_only = True
        elif u:
            blocks, route = u, "unpaywall"
    if not blocks and not pdf_only:
        u = route_doi(rec, log)
        if isinstance(u, dict):
            pdf_only = True
        elif u:
            blocks, route = u, "doi_direct"
    status = "full_text" if blocks else ("pdf_only" if pdf_only else "unavailable")
    return {"pmid": rec["pmid"], "doi": rec.get("doi", ""), "status": status, "route": route,
            "routes_tried": [x["route"] for x in log], "log": log, "blocks": blocks or []}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True, help="report JSON (no text, just per-paper route status)")
    ap.add_argument("--cache", default="out/fulltext")
    ap.add_argument("--max", type=int, default=13)
    a = ap.parse_args()
    import extract
    d = common.load_json(a.inp)
    inc = extract.select_papers(d["records"], a.max)
    os.makedirs(a.cache, exist_ok=True)
    rep = []
    for r in inc:
        path = os.path.join(a.cache, f"{r['pmid']}.json")
        if os.path.exists(path):
            res = common.load_json(path)
        else:
            res = fetch_one(r)
            common.save_json(res, path)
        rep.append({k: res[k] for k in ("pmid", "doi", "status", "route", "routes_tried", "log")} | {"chars": body_chars(res["blocks"])})
        print(f"PMID {r['pmid']}: {res['status']} via {res['route']} ({body_chars(res['blocks'])} chars); tried {res['routes_tried']}")
    common.save_json({"hyp": d["hyp"], "papers": rep}, a.out)
    by = {}
    for x in rep:
        k = x["route"] if x["status"] == "full_text" else x["status"]
        by[k] = by.get(k, 0) + 1
    print("coverage:", by)


if __name__ == "__main__":
    main()
