#!/usr/bin/env python3
"""Write the MecCog submission workbook (sheets Submission + Method, 19 official columns) with the standard
library only (zipfile + XML), so no spreadsheet package is needed to build it.
Usage: python3 to_template.py --in out/extracted.json --out out/dry_run.xlsx [--method method.json]

Provenance rule in this abstract-only stage: a number printed in the abstract is 'printed_in_text'; a number we
did not find is N/A with 'full_text_unavailable' (we did not try the full text). Such a file is a DRY RUN, not
submittable: the real pipeline must read full text first."""
import argparse
import os
import re
import zipfile
from xml.sax.saxutils import escape

import common

COLUMNS = ["Hypothesis", "DOI", "Paper/source type", "PubMed ID", "Paper/Finding ID", "Finding description",
           "Finding quote", "Finding summary", "Finding relevance", "Experimental system", "Data location",
           "Effect size", "Effect size provenance", "P value", "P value provenance", "Sample size",
           "Sample size provenance", "Directness class", "Directness strength"]
STRENGTH = {1: "very strong", 2: "strong", 3: "moderate", 4: "weak", 5: "very weak"}
METHOD_ROWS = ["Team", "Team leader", "Team leader email", "Method URL", "Commit SHA", "Who did the work", "Model and version"]
DRY_METHOD = {"Team": "dry-run (no team yet)", "Team leader": "dry run", "Team leader email": "dry-run@example.org",
              "Method URL": "https://github.com/DrAhmed7887/hack-meccog-apoe4", "Commit SHA": "GIT_HEAD",
              "Who did the work": "agent", "Model and version": "qwen3.8-27b (RWTHgpt KI:connect, via rwth-ask)"}


def col_letter(i):
    s = ""
    i += 1
    while i:
        i, r = divmod(i - 1, 26)
        s = chr(65 + r) + s
    return s


_BAD = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


def sheet_xml(rows):
    out = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
           '<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData>']
    for r, row in enumerate(rows, 1):
        out.append(f'<row r="{r}">')
        for c, v in enumerate(row):
            if v is None or v == "":
                continue
            t = escape(_BAD.sub("", str(v)))
            out.append(f'<c r="{col_letter(c)}{r}" t="inlineStr"><is><t xml:space="preserve">{t}</t></is></c>')
        out.append("</row>")
    out.append("</sheetData></worksheet>")
    return "".join(out)


def write_xlsx(path, sheets):
    """sheets: list of (name, rows). Minimal valid workbook, inline strings."""
    ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
          '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
          '<Default Extension="xml" ContentType="application/xml"/>'
          '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>'
          + "".join(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>'
                    for i in range(1, len(sheets) + 1)) + "</Types>")
    rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
            '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/></Relationships>')
    wb = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" '
          'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"><sheets>'
          + "".join(f'<sheet name="{escape(n)}" sheetId="{i}" r:id="rId{i}"/>' for i, (n, _) in enumerate(sheets, 1)) + "</sheets></workbook>")
    wrels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
             + "".join(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>'
                       for i in range(1, len(sheets) + 1)) + "</Relationships>")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", ct)
        z.writestr("_rels/.rels", rels)
        z.writestr("xl/workbook.xml", wb)
        z.writestr("xl/_rels/workbook.xml.rels", wrels)
        for i, (_, rows) in enumerate(sheets, 1):
            z.writestr(f"xl/worksheets/sheet{i}.xml", sheet_xml(rows))


def na(v):
    return v if v not in (None, "") else "N/A"


def build_rows(hyp_statement, papers):
    rows = [COLUMNS, [hyp_statement] + [None] * 18]
    n = 0
    for p in papers:
        if not p.get("findings"):
            continue
        n += 1
        rows.append([None, na(p.get("doi")), "PubMed published", p["pmid"], f"P{n}"] + [None] * 14)
        for j, f in enumerate(p["findings"], 1):
            desc = ("CONTRADICTING: " if f["direction"] == "contradicts" else "") + f["description"]
            row = [None, None, None, None, f"P{n}.F{j}", desc, na(f["quote"]), na(f["summary"]), f"{f['relevance']:g}",
                   na(f["experimental_system"]), "Abstract"]
            for kind in ("effect_size", "p_value", "sample_size"):
                v = f[kind]["value"]
                row += [v, "printed_in_text"] if v else ["N/A", "full_text_unavailable"]
            row.append(str(f["directness_class"] or 5))
            s = f["directness_strength"] or 5
            row.append(f"{s} {STRENGTH[s]}")
            rows.append(row)
    return rows


def git_head():
    """Commit SHA of this repo's HEAD (what the validator asks for), or N/A outside a git checkout."""
    import subprocess
    try:
        r = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, timeout=10,
                           cwd=os.path.dirname(os.path.abspath(__file__)))
        return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else "N/A"
    except Exception:
        return "N/A"


def build_method(method):
    m = dict(method)
    if m.get("Commit SHA") == "GIT_HEAD":
        m["Commit SHA"] = git_head()
    return [[k, m.get(k, "")] for k in METHOD_ROWS]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--method", help="JSON with the 7 Method-sheet fields; default is dry-run placeholders")
    a = ap.parse_args()
    d = common.load_json(a.inp)
    stmt = common.load_json("hypotheses.json")[d["hyp"]]["statement"]
    method = common.load_json(a.method) if a.method else DRY_METHOD
    os.makedirs(os.path.dirname(a.out) or ".", exist_ok=True)
    rows = build_rows(stmt, d["papers"])
    write_xlsx(a.out, [("Submission", rows), ("Method", build_method(method))])
    npap = sum(1 for r in rows[2:] if re.fullmatch(r"P\d+", r[4] or ""))
    nfin = sum(1 for r in rows[2:] if re.fullmatch(r"P\d+\.F\d+", r[4] or ""))
    print(f"wrote {a.out}: {npap} papers, {nfin} findings")


if __name__ == "__main__":
    main()
