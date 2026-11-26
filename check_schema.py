#!/usr/bin/env python3
"""Own schema check (fallback when openpyxl / the official validator is unavailable): reads the xlsx with the
standard library and checks headers, IDs and enumerations. NOT a substitute for the official validator."""
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

from to_template import COLUMNS

NS = {"m": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
PROV = {"printed_in_text", "visual_only", "estimated_from_figure", "supplement_only", "not_found_in_source",
        "full_text_unavailable", "ambiguous_panel"}
PROV_ABSENT = {"not_found_in_source", "full_text_unavailable", "ambiguous_panel"}
MAX_PAPERS = 50
EST = r"~?\s*"
RE_STAT_SHAPES = {
    11: (re.compile(EST + r"(?:\d+(?:\.\d+)?%|\d+(?:\.\d+)?x|[a-zA-Z]+\s*=\s*-?\d+(?:\.\d+)?)$", re.I),
         re.compile(r"qualitative$", re.I)),
    13: (re.compile(r"(?:[<>]=?\s*)?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?$"), None),
    15: (re.compile(EST + r"\d+(?:\s*-\s*\d+)?$"), None),
}


def read_rows(path):
    with zipfile.ZipFile(path) as z:
        shared = []
        if "xl/sharedStrings.xml" in z.namelist():
            shared = ["".join(si.itertext()) for si in ET.fromstring(z.read("xl/sharedStrings.xml")).findall("m:si", NS)]
        names = [s.get("name") for s in ET.fromstring(z.read("xl/workbook.xml")).findall("m:sheets/m:sheet", NS)]
        sheets = {}
        for i, n in enumerate(names, 1):
            rows = []
            for row in ET.fromstring(z.read(f"xl/worksheets/sheet{i}.xml")).findall(".//m:row", NS):
                cells = {}
                for c in row.findall("m:c", NS):
                    col = re.match(r"[A-Z]+", c.get("r")).group(0)
                    idx = sum((ord(ch) - 64) * 26 ** k for k, ch in enumerate(reversed(col))) - 1
                    t = c.get("t")
                    if t == "inlineStr":
                        ise = c.find("m:is", NS)
                        v = "".join(ise.itertext()) if ise is not None else None
                    else:
                        ve = c.find("m:v", NS)
                        v = None if ve is None else (shared[int(ve.text)] if t == "s" else ve.text)
                    cells[idx] = v
                rows.append([cells.get(k) for k in range(max(cells) + 1)] if cells else [])
            sheets[n] = rows
    return sheets


def check(path):
    errs = []
    sh = read_rows(path)
    rows = sh.get("Submission", [])
    if "Method" not in sh:
        errs.append("no Method sheet")
    if not rows or rows[0][:19] != COLUMNS:
        errs.append("header row differs from the official 19 columns")
    if len(rows) < 2 or not (rows[1] + [None])[0]:
        errs.append("row 2 (hypothesis) empty")
    pn, fn = 0, 0
    for r, row in enumerate(rows[2:], 3):
        row = row + [None] * (19 - len(row))
        i = row[4] or ""
        if re.fullmatch(r"P\d+", i):
            pn += 1
            fn = 0
            if i != f"P{pn}":
                errs.append(f"row {r}: {i} out of sequence")
            if row[2] != "PubMed published" or not (row[3] or "").isdigit():
                errs.append(f"row {r}: source type or PMID bad")
        elif re.fullmatch(r"P\d+\.F\d+", i):
            fn += 1
            if i != f"P{pn}.F{fn}":
                errs.append(f"row {r}: {i} out of sequence")
            if any(row[k] in (None, "") for k in range(5, 19)):
                errs.append(f"row {r}: empty cell (use N/A)")
            for vcol, pcol, label in ((11, 12, "Effect size"), (13, 14, "P value"), (15, 16, "Sample size")):
                val = str(row[vcol] or "").strip()
                prov = str(row[pcol] or "").strip()
                if prov not in PROV:
                    errs.append(f"row {r}: bad provenance {row[pcol]!r}")
                    continue
                is_na = val.upper() == "N/A"
                if prov in PROV_ABSENT and not is_na:
                    errs.append(f"row {r}: {label} is {val!r} with absent provenance {prov!r}")
                elif prov not in PROV_ABSENT and is_na:
                    errs.append(f"row {r}: {label} is N/A with value provenance {prov!r}")
                if vcol == 13 and (prov == "estimated_from_figure" or val.startswith("~")):
                    errs.append(f"row {r}: P value cannot use ~ or estimated_from_figure")
                elif prov == "estimated_from_figure" and not val.startswith("~"):
                    errs.append(f"row {r}: {label} provenance 'estimated_from_figure' requires leading ~ (got {val!r})")
                elif val.startswith("~") and prov != "estimated_from_figure":
                    errs.append(f"row {r}: {label} {val!r} starts with ~ without estimated_from_figure provenance")
                if not is_na:
                    pat_num, pat_qual = RE_STAT_SHAPES[vcol]
                    if not (pat_num.match(val) or (pat_qual and pat_qual.match(val))):
                        errs.append(f"row {r}: {label} {val!r} has invalid shape")
            if row[17] not in {"1", "2", "3", "4", "5"}:
                errs.append(f"row {r}: bad directness class")
        else:
            errs.append(f"row {r}: bad ID {i!r}")
    if pn == 0:
        errs.append("no papers")
    elif pn > MAX_PAPERS:
        errs.append(f"{pn} papers exceeds {MAX_PAPERS}-paper cap")
    return errs


if __name__ == "__main__":
    e = check(sys.argv[1])
    print("schema check:", "OK" if not e else "\n  ".join(["FAILED"] + e))
    sys.exit(1 if e else 0)
