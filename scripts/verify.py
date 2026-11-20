#!/usr/bin/env python3
"""Offline verification of the committed (frozen) data. Standard library only. No network, no keys, no rwth-ask.

Checks:
  1. data/FREEZE.json exists and every listed file matches its sha256 (skipped with --data out).
  2. data/dd/report.json: per-hypothesis counts agree with the rows (C1-C4 passes).
  3. data/extracted.json: every paper has a PMID, every finding has the required fields,
     directness class 1-5, and every kept number carries a verbatim quote.
  4. data/*.xlsx (if present): own schema check (check_schema.py) and paper/finding counts equal extracted.json.
  5. CLAIMS.md: every backticked file path in the table resolves (out/ paths map to the data dir).

Usage: python3 scripts/verify.py [--data data] [--claims CLAIMS.md]
Exit code 0 only if there are no FAIL lines. This script does not run the pipeline.
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

FAILS = []
WARNS = []


def fail(msg: str) -> None:
    FAILS.append(msg)
    print("FAIL:", msg)


def warn(msg: str) -> None:
    WARNS.append(msg)
    print("WARN:", msg)


def ok(msg: str) -> None:
    print("ok:  ", msg)


def load(path: Path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, ValueError) as e:
        fail(f"cannot read {path.relative_to(ROOT) if path.is_relative_to(ROOT) else path}: {e}")
        return None


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def check_freeze(data: Path, strict: bool) -> None:
    fz = data / "FREEZE.json"
    if not fz.exists():
        (fail if strict else warn)(f"{fz.name} missing: data not frozen yet (see FREEZE.md)")
        return
    man = load(fz)
    if man is None:
        return
    if not isinstance(man, dict) or not isinstance(man.get("files"), dict) or not man["files"]:
        fail(f"{fz.name} is empty or has no non-empty 'files' map: nothing is hashed")
        return
    for rel, want in man.get("files", {}).items():
        p = data / rel
        if not p.exists():
            fail(f"frozen file missing: {rel}")
        elif sha256(p) != want:
            fail(f"hash mismatch: {rel}")
    ok(f"FREEZE.json: {len(man.get('files', {}))} files hashed")


def check_report(data: Path) -> None:
    rep = load(data / "dd" / "report.json")
    if rep is None:
        return
    if not isinstance(rep, dict) or not rep:
        fail("dd/report.json is empty: no per-hypothesis counts to check")
        return
    for hyp, blk in rep.items():
        rows = blk.get("rows", [])
        if blk.get("screened") != len(rows):
            fail(f"report {hyp}: screened={blk.get('screened')} but {len(rows)} rows")
        passes = [r for r in rows
                  if all(isinstance(r.get(k), dict) and r[k].get("v") == "yes" for k in ("C1", "C2", "C3"))
                  and r.get("C4") == "yes"]
        if blk.get("pass_C1_C4") != len(passes):
            fail(f"report {hyp}: pass_C1_C4={blk.get('pass_C1_C4')} but rows give {len(passes)}")
        if blk.get("n_pass_C1_C4_cap50") != min(len(passes), 50):
            fail(f"report {hyp}: cap50 count disagrees with rows")
        ok(f"report {hyp}: screened {len(rows)}, pass C1-C4 {len(passes)}")


def check_extracted(data: Path):
    ext = load(data / "extracted.json")
    if ext is None:
        return None
    if not isinstance(ext, dict):
        fail("extracted.json is not a JSON object")
        return None
    papers = ext.get("papers", [])
    if not papers:
        fail("extracted.json has no papers")
    if len(papers) > 50:
        fail(f"{len(papers)} papers exceeds the 50-paper cap")
    nf = 0
    with_findings = 0  # to_template.build_rows skips papers without findings
    for p in papers:
        if p.get("findings"):
            with_findings += 1
        if not str(p.get("pmid", "")).isdigit():
            fail(f"paper without numeric PMID: {p.get('title', '?')[:40]}")
        for f in p.get("findings", []):
            nf += 1
            tag = f"{p.get('pmid')}"
            if f.get("directness_class") not in (1, 2, 3, 4, 5):
                fail(f"{tag}: bad directness_class")
            for need in ("description", "quote", "direction"):
                if not f.get(need):
                    fail(f"{tag}: finding missing {need}")
            for key in ("effect_size", "p_value", "sample_size"):
                blk = f.get(key) or {}
                if blk.get("value") not in (None, "") and not blk.get("quote"):
                    fail(f"{tag}: {key} value kept without a verbatim quote")
    ok(f"extracted.json: {len(papers)} papers ({with_findings} with findings), {nf} findings")
    return with_findings, nf


def check_workbook(data: Path, counts, strict: bool = True) -> None:
    gate = fail if strict else warn
    books = sorted(data.glob("*.xlsx"))
    if not books:
        gate("no .xlsx in data dir (final workbook not frozen yet)")
        return
    import check_schema
    for b in books:
        errs = check_schema.check(str(b))
        if errs:
            fail(f"{b.name} schema: " + "; ".join(errs[:5]))
            continue
        rows = check_schema.read_rows(str(b)).get("Submission", [])[2:]
        ids = [(r + [None] * 5)[4] or "" for r in rows]
        pn = sum(1 for i in ids if re.fullmatch(r"P\d+", i))
        fn = sum(1 for i in ids if re.fullmatch(r"P\d+\.F\d+", i))
        ok(f"{b.name}: schema ok, {pn} papers, {fn} findings")
        if counts and (pn, fn) != counts:
            gate(f"{b.name} counts {(pn, fn)} differ from extracted.json (papers with findings, findings) {counts}")


def check_claims(data: Path, claims: Path) -> None:
    if not claims.exists():
        fail(f"{claims.name} missing")
        return
    n = 0
    for line in claims.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        for path in re.findall(r"`([^`\s]+\.[A-Za-z0-9]+)(?::\d+(?:-\d+)?)?`", line):
            if path.startswith("--") or "*" in path or path.startswith("http"):
                continue
            # out/ is git-ignored scratch: map it to the data dir only, never to the local out/
            cand = [data / path[4:]] if path.startswith("out/") else [ROOT / path]
            n += 1
            if not any(c.exists() for c in cand):
                fail(f"CLAIMS.md references missing file: {path}")
    ok(f"CLAIMS.md: {n} file references checked")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data", help="frozen data dir (use 'out' for a pre-freeze local check)")
    ap.add_argument("--claims", default="CLAIMS.md")
    a = ap.parse_args()
    data = (ROOT / a.data).resolve()
    if not data.is_dir():
        fail(f"data dir {a.data}/ not found: freeze not done (see FREEZE.md)")
    else:
        strict = data != (ROOT / "out").resolve()
        check_freeze(data, strict=strict)
        check_report(data)
        counts = check_extracted(data)
        check_workbook(data, counts, strict=strict)
    check_claims(data, ROOT / a.claims)
    print(f"\nverify: {len(FAILS)} FAIL, {len(WARNS)} WARN")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
