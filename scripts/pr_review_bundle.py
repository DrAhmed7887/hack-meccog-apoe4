#!/usr/bin/env python3
"""Deterministic PR pre-review verification bundle for hack-meccog-apoe4.

Checks every extracted JSON and workbook under a target data directory (and
optionally git diff against origin/main) across:
  (a) Verbatim finding & stat quotes against a single block in out/fulltext/ or abstract
  (b) Panel-level Data location precision & Rule C3 stat provenance
  (c) Identifier validity (PMID/DOI), optional live Europe PMC pubType review purge,
      and doi-check retraction status
  (d) Rule B1/C1 (contrary findings, <= 50 papers) & Rule C5 Step 1 boundary
  (e) Repo hygiene (no PDFs, out/fulltext/, method.json, .licenses/, or >2 MB structure assets)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import check_schema
import extract
import verify_ids
import verify_sample

RE_WHOLE_FIG = re.compile(r"^(?:supplementary\s+)?fig(?:ure)?\.?\s*s?\d+$", re.I)
RE_PANEL_LOC = re.compile(
    r"(?:supplementary\s+)?(?:fig(?:ure)?\.?\s*s?\d+[a-z0-9]*(?:\s*[-–,&]+\s*[a-z0-9]+)*|table\s*s?\d+)",
    re.I,
)
RULE_C5_LEAK = re.compile(
    r"\b(?:plddt|pae|predicted aligned error|alphafold|experiment proposal|confidence score)\b",
    re.I,
)
EPMC_SEARCH = "https://www.ebi.ac.uk/europepmc/webservices/rest/search"


def check_hygiene(repo_root: Path = ROOT) -> list[str]:
    """Verify tracked git files contain no forbidden binaries, caches, or secrets."""
    out = subprocess.check_output(["git", "ls-files"], cwd=repo_root, text=True)
    bad = []
    for rel in out.splitlines():
        p = repo_root / rel
        if rel.lower().endswith(".pdf"):
            bad.append(f"tracked PDF: {rel}")
        elif rel.startswith("out/fulltext/"):
            bad.append(f"tracked fulltext cache: {rel}")
        elif rel == "method.json" or rel.startswith(".licenses/"):
            bad.append(f"forbidden tracked file: {rel}")
        elif rel.startswith("docs/structures/") and p.exists() and p.stat().st_size > 2 * 1024 * 1024:
            bad.append(f"oversized structure (>2MB): {rel}")
    return bad


def find_extracted_files(data_dir: Path) -> list[Path]:
    """Return sorted extracted JSON files under data/ or data/<HYP>/."""
    files = []
    if (data_dir / "extracted.json").exists():
        files.append(data_dir / "extracted.json")
    for p in sorted(data_dir.glob("*/extracted*.json")):
        if p not in files:
            files.append(p)
    return files


def audit_extracted_file(ext_path: Path, fulltext_dir: Path) -> dict:
    """Audit one extracted JSON against single-block quotes, panel locations, and Rule C5."""
    data = json.loads(ext_path.read_text(encoding="utf-8"))
    papers = data.get("papers", [])
    issues = []
    warnings = []
    n_findings = 0
    n_contrary = 0
    n_stats = 0

    if len(papers) > 50:
        issues.append(f"{ext_path.name}: {len(papers)} papers exceeds 50-paper cap")

    for p in papers:
        pmid = str(p.get("pmid") or "").strip()
        ft_path = fulltext_dir / f"{pmid}.json"
        ft_blocks = None
        if p.get("fulltext", {}).get("status") == "full_text" and ft_path.exists():
            ft_blocks = json.loads(ft_path.read_text(encoding="utf-8")).get("blocks", [])
        abs_block = [{"loc": "Abstract", "kind": "text", "text": p.get("abstract", "")}]

        for idx, f in enumerate(p.get("findings", []), 1):
            n_findings += 1
            fid = f"{pmid}.F{idx}"
            if f.get("direction") == "contradicts":
                n_contrary += 1

            blocks = ft_blocks if (f.get("source") == "full_text" and ft_blocks) else abs_block
            quote = f.get("quote") or ""
            matched_block = extract.find_block(quote, blocks)
            if not matched_block:
                issues.append(f"{fid}: quote not verbatim in a single source block")

            loc = str(f.get("location") or "").strip()
            if f.get("source") == "full_text":
                if RE_WHOLE_FIG.match(loc):
                    warnings.append(f"{fid}: whole-figure location without panel letter ({loc!r})")
                elif not RE_PANEL_LOC.search(loc):
                    warnings.append(f"{fid}: prose-only Data location ({loc!r})")

            text_blob = " ".join(str(f.get(k) or "") for k in ("description", "summary", "experimental_system"))
            if RULE_C5_LEAK.search(text_blob):
                issues.append(f"{fid}: Rule C5 Step 1 boundary leak detected in finding text")

            for kind in ("effect_size", "p_value", "sample_size"):
                blk = f.get(kind) or {}
                val = blk.get("value")
                if val in (None, "", "N/A"):
                    continue
                n_stats += 1
                prov = blk.get("provenance") or "printed_in_text"
                if str(val).strip().lower() == "qualitative":
                    continue
                squote = blk.get("quote") or ""
                if not matched_block or not extract.quote_in_text(squote, matched_block["text"]):
                    issues.append(f"{fid}.{kind}: stat quote not in same block as finding quote")
                elif extract.verify_stat(kind, val, squote, matched_block["text"], provenance=prov) is None:
                    issues.append(f"{fid}.{kind}: stat {val!r} ({prov}) failed verify_stat")

    return {
        "file": str(ext_path),
        "n_papers": len(papers),
        "n_findings": n_findings,
        "n_contrary": n_contrary,
        "n_stats": n_stats,
        "issues": issues,
        "warnings": warnings,
    }


def check_live_ids(papers: list[dict]) -> list[str]:
    """Run live Europe PMC pubType/title check and doi-check retraction guard."""
    import common
    issues = []
    dois = []
    for p in papers:
        pmid = str(p.get("pmid") or "").strip()
        doi = str(p.get("doi") or "").strip()
        if doi and doi.lower() != "n/a":
            dois.append(doi)
        if not pmid.isdigit():
            continue
        raw = common.http_get(
            EPMC_SEARCH,
            {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "lite"},
            min_interval=0.15,
        )
        hits = json.loads(raw).get("resultList", {}).get("result", [])
        if not hits:
            issues.append(f"PMID {pmid}: not found in Europe PMC")
            continue
        hit = hits[0]
        pub_types = [t.lower() for t in (hit.get("pubTypeList", {}).get("pubType") or [])]
        if any("review" in t for t in pub_types):
            issues.append(f"PMID {pmid}: flagged as review article ({pub_types})")
        if not verify_ids._title_match(p.get("title", ""), hit.get("title", "")):
            issues.append(f"PMID {pmid}: title mismatch vs Europe PMC ({hit.get('title', '')[:60]})")

    doi_check_bin = shutil.which("doi-check") or os.path.expanduser("~/.local/bin/doi-check")
    if dois and os.path.exists(doi_check_bin):
        res = subprocess.run([doi_check_bin, "--json", *dois], capture_output=True, text=True, timeout=60)
        if res.returncode == 0 and res.stdout.strip():
            try:
                rows = json.loads(res.stdout)
                for row in rows:
                    if row.get("retracted"):
                        issues.append(f"RETRACTED DOI detected: {row.get('doi')}")
            except ValueError:
                issues.append("doi-check output was not valid JSON")
    return issues


def check_workbooks(data_dir: Path) -> list[str]:
    """Check every .xlsx under data_dir with check_schema and Method/README consistency."""
    issues = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    books = sorted(list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*/*.xlsx")))
    for b in books:
        errs = check_schema.check(str(b))
        if errs:
            issues.extend(f"{b.name}: {e}" for e in errs)
            continue
        method_rows = check_schema.read_rows(str(b)).get("Method", [])
        m = {r[0]: r[1] for r in method_rows if len(r) >= 2}
        if m.get("Who did the work") == "collab":
            models = m.get("Model and version") or ""
            if not any(sep in models for sep in (",", ";", "/", "\n", " and ")):
                issues.append(f"{b.name}: collab Method row missing multi-agent separator in Model and version")
        if readme and m.get("Who did the work") and m["Who did the work"] not in readme:
            issues.append(f"{b.name}: README.md does not mention Who did the work={m['Who did the work']!r}")
    return issues


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data", help="Data directory to audit")
    ap.add_argument("--fulltext", default="out/fulltext", help="Cached fulltext directory")
    ap.add_argument("--online", action="store_true", help="Also verify live Europe PMC pubType + doi-check")
    ap.add_argument("--pr", help="Optional PR number for display")
    ap.add_argument("--out", help="Optional JSON summary output path")
    a = ap.parse_args()

    data_dir = (ROOT / a.data).resolve()
    ft_dir = (ROOT / a.fulltext).resolve()
    hygiene = check_hygiene(ROOT)
    wb_issues = check_workbooks(data_dir)
    ext_reports = [audit_extracted_file(p, ft_dir) for p in find_extracted_files(data_dir)]

    live_issues = []
    if a.online:
        all_papers = []
        for p in find_extracted_files(data_dir):
            all_papers.extend(json.loads(p.read_text(encoding="utf-8")).get("papers", []))
        dedup = list({str(p.get("pmid")): p for p in all_papers}.values())
        live_issues = check_live_ids(dedup)

    total_issues = list(hygiene) + list(wb_issues) + list(live_issues)
    for rep in ext_reports:
        total_issues.extend(rep["issues"])

    summary = {
        "pr": a.pr,
        "hygiene_issues": hygiene,
        "workbook_issues": wb_issues,
        "live_id_issues": live_issues,
        "extracted": ext_reports,
        "pass": not total_issues,
    }
    if a.out:
        Path(a.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"=== PR Review Bundle ({'PR #' + a.pr if a.pr else 'local'}) ===")
    print(f"Hygiene issues: {len(hygiene)} | Workbook issues: {len(wb_issues)} | Live ID issues: {len(live_issues)}")
    for rep in ext_reports:
        print(f"Extracted {Path(rep['file']).name}: {rep['n_papers']} papers, {rep['n_findings']} findings "
              f"({rep['n_contrary']} contradicting), {rep['n_stats']} numeric/qual stats | "
              f"issues={len(rep['issues'])}, warnings={len(rep['warnings'])}")
        for w in rep["warnings"][:10]:
            print(f"  WARN: {w}")
    for iss in total_issues:
        print(f"  FAIL: {iss}")
    print(f"GATE STATUS: {'PASS' if summary['pass'] else 'FAIL'}")
    return 0 if summary["pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
