#!/usr/bin/env python3
"""Parse official/hypotheses.html into hypotheses.json (exact statements, starting reference PMID)."""
import html
import json
import re
import sys


def parse_hypotheses(page):
    out = {}
    for m in re.finditer(r'<article class="hyp" id="(h\d)">(.*?)</article>', page, flags=re.S):
        hid = m.group(1).upper()
        body = m.group(2)
        title = re.search(r"<h2>(?:<span class=\"sr\">[^<]*</span>)?(.*?)</h2>", body, re.S).group(1)
        stmt = re.search(r'<p class="statement">(.*?)</p>', body, re.S).group(1)
        ref = re.search(r'<p class="ref">(.*?)</p>', body, re.S).group(1)
        pmid = re.search(r"PMID\s*(\d+)", ref).group(1)
        clean = lambda s: html.unescape(re.sub(r"<[^>]+>", "", s)).strip()
        out[hid] = {"title": clean(title), "statement": clean(stmt),
                    "start_ref": clean(ref), "start_pmid": pmid}
    return out


if __name__ == "__main__":
    page = open(sys.argv[1] if len(sys.argv) > 1 else "official/hypotheses.html", encoding="utf-8").read()
    h = parse_hypotheses(page)
    json.dump(h, open("hypotheses.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(len(h), "hypotheses written")
