#!/usr/bin/env python3
"""Write the MecCog submission workbook (sheets Submission + Method, 19 official columns) with the standard
library only (zipfile + XML), so no spreadsheet package is needed to build it.
Usage: python3 to_template.py --in out/extracted.json --out out/dry_run.xlsx [--method method.json]

Provenance: a number quoted verbatim from the source is 'printed_in_text'. A number missing from a finding read
from FULL TEXT is N/A with 'not_found_in_source' (Data location = the section or table name). A finding read from
the abstract only (full text unavailable after every route in fulltext.py) is N/A with 'full_text_unavailable'
and location 'Abstract'. A figure-only value would need visual_only/estimated_from_figure: not done yet."""
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
REVIEW_MARKER = "[PHYSICIAN REVIEW REQUIRED]"
METHOD_ROWS = ["Team", "Team leader", "Team leader email", "Method URL", "Commit SHA", "Who did the work", "Model and version"]
DRY_METHOD = {"Team": "Khepri", "Team leader": "dry run", "Team leader email": "dry-run@example.org",
              "Method URL": "https://github.com/DrAhmed7887/hack-meccog-apoe4", "Commit SHA": "GIT_HEAD",
              "Who did the work": "both", "Model and version": "qwen3.8-27b (RWTHgpt KI:connect, via rwth-ask)"}


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


ALLOWED_VALUE_PROVENANCE = {"printed_in_text", "estimated_from_figure", "visual_only", "supplement_only"}


def na(v):
    return v if v not in (None, "") else "N/A"


def stat_cells(kind, blk, ft):
    """Return [value, provenance] for one statistic cell pair, enforcing Rule C3 provenance guards."""
    blk = blk if isinstance(blk, dict) else {}
    raw_v = blk.get("value")
    prov = blk.get("provenance")
    if raw_v in (None, "") or str(raw_v).strip().upper() == "N/A":
        if prov == "estimated_from_figure":
            raise ValueError(f"{kind}: provenance 'estimated_from_figure' cannot accompany N/A")
        return ["N/A", "not_found_in_source" if ft else "full_text_unavailable"]
    vs = str(raw_v).strip()
    prov = prov or "printed_in_text"
    if prov not in ALLOWED_VALUE_PROVENANCE:
        raise ValueError(f"{kind}: invalid provenance {prov!r} for non-empty value {vs!r}")
    if kind == "p_value" and (prov == "estimated_from_figure" or vs.startswith("~")):
        raise ValueError(f"p_value cannot use '~' or 'estimated_from_figure' (got {vs!r}, {prov!r})")
    if prov == "estimated_from_figure":
        if not vs.startswith("~"):
            raise ValueError(f"{kind} with provenance 'estimated_from_figure' must start with '~' (got {vs!r})")
        if vs.lstrip("~").strip().lower() == "qualitative":
            raise ValueError(f"{kind} with provenance 'estimated_from_figure' cannot be qualitative")
    elif vs.startswith("~"):
        raise ValueError(f"{kind} starting with '~' must use provenance 'estimated_from_figure' (got {prov!r})")
    return [vs, prov]


def inconsistent_directness_pair(f):
    """Catch scale pair errors at export too, including older extracted JSON files."""
    directness_class = f.get("directness_class")
    directness_strength = f.get("directness_strength")
    return ((directness_class == 1 and directness_strength in (4, 5)) or
            (directness_class == 4 and directness_strength in (1, 2)))


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
            if f.get("physician_review") or inconsistent_directness_pair(f):
                desc = f"{REVIEW_MARKER} {desc}"
            ft = f.get("source") == "full_text"
            row = [None, None, None, None, f"P{n}.F{j}", desc, na(f["quote"]), na(f["summary"]), f"{f['relevance']:g}",
                   na(f["experimental_system"]), f.get("location") or "Abstract"]
            for kind in ("effect_size", "p_value", "sample_size"):
                row += stat_cells(kind, f.get(kind), ft)
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
