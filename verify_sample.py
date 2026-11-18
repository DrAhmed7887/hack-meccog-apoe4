#!/usr/bin/env python3
"""Verification sample: pick findings that carry a number (seeded), and for each number field locate its quoted
string in the CACHED SOURCE TEXT (out/fulltext/<pmid>.json, or the abstract for abstract-only papers) by program,
then show the surrounding sentence.
Usage: python3 verify_sample.py --in out/extracted.json --out out/verify_sample.md [--n 10] [--seed 7]
A 'found' means: the quote is a verbatim substring of the source (after whitespace/dash normalisation) AND the
value's digits appear inside that quote. Nothing here calls a model."""
import argparse
import os
import random
import re

import common
import extract

FIELDS = ("effect_size", "p_value", "sample_size")


def source_blocks(paper, cache):
    p = os.path.join(cache, f"{paper['pmid']}.json")
    if paper.get("fulltext", {}).get("status") == "full_text" and os.path.exists(p):
        return common.load_json(p)["blocks"]
    return [{"loc": "Abstract", "kind": "text", "text": paper.get("abstract", "")}]


def sentence_around(text, quote):
    """The sentence(s) of `text` that contain `quote` (whitespace-normalised)."""
    t, q = extract.norm_text(text), extract.norm_text(quote)
    i = t.find(q)
    if i < 0:
        return ""
    a = max(t.rfind(". ", 0, i) + 2, 0) if t.rfind(". ", 0, i) >= 0 else 0
    j = t.find(". ", i + len(q))
    b = j + 1 if j >= 0 else len(t)
    return t[a:b].strip()


def check_field(kind, field, blocks):
    """-> (found: bool, sentence: str, location: str)."""
    v, q = field["value"], field["quote"]
    for b in blocks:
        if extract.quote_in_text(q, b["text"]):
            digits_ok = extract.verify_stat(kind, v, q, b["text"]) is not None
            return digits_ok, sentence_around(b["text"], q), b["loc"]
    return False, "", ""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cache", default="out/fulltext")
    ap.add_argument("--n", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    a = ap.parse_args()
    d = common.load_json(a.inp)
    pool = []
    for p in d["papers"]:
        for j, f in enumerate(p["findings"], 1):
            if any(f[k]["value"] and f[k]["value"] != "qualitative" for k in FIELDS):
                pool.append((p, j, f))
    random.Random(a.seed).shuffle(pool)
    pick = pool[:a.n]
    lines = [f"# Verification sample (seed {a.seed}, {len(pick)} of {len(pool)} findings with a number)", "",
             "| finding | field | quoted value | found in source? | location | sentence |", "|---|---|---|---|---|---|"]
    tot = ok = 0
    for p, j, f in pick:
        blocks = source_blocks(p, a.cache)
        for k in FIELDS:
            if not f[k]["value"] or f[k]["value"] == "qualitative":
                continue
            found, sent, loc = check_field(k, f[k], blocks)
            tot += 1
            ok += found
            sent = sent.replace("|", "\\|")
            lines.append(f"| PMID {p['pmid']} F{j} | {k} | {f[k]['value']} | {'yes' if found else 'NO'} | {loc} | {sent} |")
    ok_f = 0
    for p, j, f in pick:
        blocks = source_blocks(p, a.cache)
        ok_f += all(check_field(k, f[k], blocks)[0] for k in FIELDS if f[k]["value"] and f[k]["value"] != "qualitative")
    lines += ["", f"Findings with every number found verbatim: {ok_f}/{len(pick)}. Number fields found verbatim: {ok}/{tot}."]
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    with open(a.out, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")
    print(f"findings {ok_f}/{len(pick)} fully verbatim; number fields {ok}/{tot}; pool {len(pool)} -> {a.out}")


if __name__ == "__main__":
    main()
