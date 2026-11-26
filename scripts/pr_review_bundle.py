#!/usr/bin/env python3
"""Deterministic PR pre-review verification bundle for hack-meccog-apoe4.

Audits every extracted JSON and workbook under a target data directory:
  (a) Verbatim finding & stat quotes against a single block in out/fulltext/ or abstract
      (requires --require-fulltext-cache locally; CI offline mode marks missing gitignored caches as WARN)
  (b) Panel-level Data location precision & Rule C3 stat provenance against check_schema.PROV
  (c) Identifier validity (PMID/DOI), plus live (--online) Europe PMC core pubType
      review/meta-analysis purge, title match, and doi-check retraction status
  (d1) Rule B1/C1 (contrary findings, <= 50 papers)
  (d2) Rule C5 Step 1 boundary across extracted JSON and workbook Submission cells
  (e) Repo hygiene & secret scan (no PDFs, .env, out/fulltext/, method.json, .licenses/, keys, or >2 MB structures)
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import check_schema
import extract
import verify_ids

RE_WHOLE_FIG = re.compile(r"^(?:supplementary\s+)?fig(?:ure)?\.?\s*s?\d+$", re.I)
RE_PANEL_LOC = re.compile(
    r"(?:supplementary\s+)?(?:fig(?:ure)?\.?\s*s?\d+[a-z0-9]*(?:\s*[-–,&]+\s*[a-z0-9]+)*|table\s*s?\d+)",
    re.I,
)
RULE_C5_LEAK = re.compile(
    r"\b(?:plddt|pae|predicted aligned error|alphafold|experiment proposal|mechanism confidence score)\b",
    re.I,
)
SECRET_RE = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH |PGP )?PRIVATE KEY-----|"
    r"\bghp_[A-Za-z0-9]{20,}\b|\bsk-[A-Za-z0-9]{20,}\b|\bAIza[0-9A-Za-z\-_]{30,}\b"
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
        elif rel == "method.json" or rel == ".env" or rel.startswith(".env.") or rel.startswith(".licenses/"):
            bad.append(f"forbidden tracked file: {rel}")
        elif rel.startswith("docs/structures/") and p.exists() and p.stat().st_size > 2 * 1024 * 1024:
            bad.append(f"oversized structure (>2MB): {rel}")
        elif p.exists() and p.is_file() and p.suffix.lower() not in (".xlsx", ".docx", ".png", ".jpg", ".cif", ".gz", ".mp4"):
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if SECRET_RE.search(txt):
                    bad.append(f"potential secret pattern in tracked file: {rel}")
            except OSError:
                pass
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


def audit_extracted_file(ext_path: Path, fulltext_dir: Path, require_fulltext_cache: bool = False) -> dict:
    """Audit one extracted JSON against single-block quotes, panel locations, stats, and Rule C5."""
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
            fid = f"{pmid or p.get('doi') or 'paper'}.F{idx}"
            if f.get("direction") == "contradicts":
                n_contrary += 1

            is_ft = f.get("source") == "full_text"
            matched_block = None
            cache_missing = is_ft and ft_blocks is None
            if cache_missing:
                msg = f"{fid}: fulltext cache missing ({ft_path.name})"
                if require_fulltext_cache:
                    issues.append(msg)
                else:
                    warnings.append(msg + " (CI offline mode)")
            else:
                blocks = ft_blocks if is_ft else abs_block
                quote = f.get("quote") or ""
                matched_block = extract.find_block(quote, blocks)
                if not matched_block:
                    issues.append(f"{fid}: quote not verbatim in a single source block")

            loc = str(f.get("location") or "").strip()
            if is_ft:
                if RE_WHOLE_FIG.match(loc):
                    warnings.append(f"{fid}: whole-figure location without panel letter ({loc!r})")
                elif not RE_PANEL_LOC.search(loc):
                    warnings.append(f"{fid}: prose-only Data location ({loc!r})")

            text_blob = " ".join(str(f.get(k) or "") for k in ("description", "summary", "experimental_system", "location"))
            if RULE_C5_LEAK.search(text_blob):
                issues.append(f"{fid}: Rule C5 Step 1 boundary leak detected in finding text")

            for kind in ("effect_size", "p_value", "sample_size"):
                blk = f.get(kind) or {}
                val = blk.get("value")
                raw_prov = blk.get("provenance")
                if raw_prov is not None and raw_prov not in check_schema.PROV:
                    issues.append(f"{fid}.{kind}: invalid provenance code {raw_prov!r}")
                    continue
                prov = raw_prov or "printed_in_text"
                vs = str(val or "").strip()
                if kind == "p_value" and (prov == "estimated_from_figure" or vs.startswith("~")):
                    issues.append(f"{fid}.p_value: P value cannot use '~' or 'estimated_from_figure'")
                    continue
                if val in (None, "", "N/A"):
                    continue
                n_stats += 1
                if vs.lower() == "qualitative":
                    if prov == "estimated_from_figure":
                        issues.append(f"{fid}.{kind}: qualitative cannot use 'estimated_from_figure'")
                    continue
                if matched_block is None:
                    continue
                squote = blk.get("quote") or ""
                if not extract.quote_in_text(squote, matched_block["text"]):
                    issues.append(f"{fid}.{kind}: stat quote not in same block as finding quote")
                elif extract.verify_stat(kind, val, squote, matched_block["text"], provenance=prov) is None:
                    issues.append(f"{fid}.{kind}: stat {val!r} ({prov}) failed verify_stat")

    if n_findings > 0 and n_contrary == 0:
        warnings.append(f"{ext_path.name}: 0 contradicting findings recorded (verify Rule B1 search)")

    return {
        "file": str(ext_path),
        "n_papers": len(papers),
        "n_findings": n_findings,
        "n_contrary": n_contrary,
        "n_stats": n_stats,
        "issues": issues,
        "warnings": warnings,
    }


def _extract_epmc_pub_types(hit: dict) -> list[str]:
    """Extract normalized publication types from Europe PMC core or lite result."""
    types = []
    ptl = (hit.get("pubTypeList") or {}).get("pubType") or []
    if isinstance(ptl, str):
        ptl = [ptl]
    types.extend(str(t).strip().lower() for t in ptl if t)
    raw_pt = hit.get("pubType") or ""
    if raw_pt:
        types.extend(part.strip().lower() for part in str(raw_pt).split(";") if part.strip())
    return types


def check_live_ids(papers: list[dict]) -> list[str]:
    """Run live Europe PMC core pubType/title check and doi-check retraction guard."""
    import common
    issues = []
    dois = []
    for p in papers:
        pmid = str(p.get("pmid") or "").strip()
        doi = str(p.get("doi") or "").strip()
        st = str(p.get("source_type") or "PubMed published").lower()
        if doi and doi.lower() != "n/a":
            dois.append(doi)
        if not pmid or pmid.upper() == "N/A":
            if st.startswith("pubmed"):
                issues.append(f"DOI {doi or '?'}: PubMed source missing numeric PMID")
            continue
        if not pmid.isdigit():
            issues.append(f"invalid non-numeric PMID {pmid!r}")
            continue
        try:
            raw = common.http_get(
                EPMC_SEARCH,
                {"query": f"EXT_ID:{pmid} AND SRC:MED", "format": "json", "resultType": "core"},
                min_interval=0.15,
            )
            hits = json.loads(raw).get("resultList", {}).get("result", [])
        except Exception as e:
            issues.append(f"PMID {pmid}: Europe PMC lookup failed ({type(e).__name__}: {e})")
            continue
        if not hits:
            issues.append(f"PMID {pmid}: not found in Europe PMC")
            continue
        hit = hits[0]
        pub_types = _extract_epmc_pub_types(hit)
        if any(("review" in t or "meta-analysis" in t) for t in pub_types):
            issues.append(f"PMID {pmid}: flagged as review/meta-analysis ({pub_types})")
        if not verify_ids._title_match(p.get("title", ""), hit.get("title", "")):
            issues.append(f"PMID {pmid}: title mismatch vs Europe PMC ({hit.get('title', '')[:60]})")

    doi_check_bin = shutil.which("doi-check") or os.path.expanduser("~/.local/bin/doi-check")
    if dois:
        if not os.path.exists(doi_check_bin):
            issues.append("doi-check binary missing: cannot verify retraction status")
        else:
            try:
                res = subprocess.run([doi_check_bin, "--json", *dois], capture_output=True, text=True, timeout=60)
                if res.returncode != 0:
                    issues.append(f"doi-check exited with code {res.returncode}: {res.stderr.strip()[:120]}")
                else:
                    rows = json.loads(res.stdout)
                    for row in rows:
                        if row.get("retracted"):
                            issues.append(f"RETRACTED DOI detected: {row.get('doi')}")
            except Exception as e:
                issues.append(f"doi-check execution failed ({type(e).__name__}: {e})")
    return issues


def check_workbooks(data_dir: Path) -> list[str]:
    """Check every .xlsx under data_dir with check_schema, Rule C5 scan, and Method/README consistency."""
    issues = []
    readme = (ROOT / "README.md").read_text(encoding="utf-8") if (ROOT / "README.md").exists() else ""
    books = sorted(list(data_dir.glob("*.xlsx")) + list(data_dir.glob("*/*.xlsx")))
    for b in books:
        errs = check_schema.check(str(b))
        if errs:
            issues.extend(f"{b.name}: {e}" for e in errs)
            continue
        sheets = check_schema.read_rows(str(b))
        for r_idx, row in enumerate(sheets.get("Submission", [])[2:], 3):
            for col_idx in (5, 7, 9, 10):
                val = row[col_idx] if col_idx < len(row) else None
                if val and RULE_C5_LEAK.search(str(val)):
                    issues.append(f"{b.name} row {r_idx}: Rule C5 Step 1 boundary leak in Submission cell")
        method_rows = sheets.get("Method", [])
        m = {r[0]: r[1] for r in method_rows if len(r) >= 2}
        if m.get("Who did the work") == "collab":
            models = m.get("Model and version") or ""
            if not any(sep in models for sep in (",", ";", "/", "\n")):
                issues.append(f"{b.name}: collab Method row missing multi-agent separator in Model and version")
        who = m.get("Who did the work") or ""
        if readme and who and not re.search(rf"\b{re.escape(who)}\b", readme, re.I):
            issues.append(f"{b.name}: README.md does not mention Who did the work={who!r}")
    return issues


def _paper_dedup_key(paper: dict) -> tuple[str, str]:
    pmid = str(paper.get("pmid") or "").strip()
    doi = str(paper.get("doi") or "").strip().lower()
    if pmid or doi:
        return (pmid, doi)
    return ("", f"obj:{id(paper)}")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--data", default="data", help="Data directory to audit")
    ap.add_argument("--fulltext", default="out/fulltext", help="Cached fulltext directory")
    ap.add_argument("--require-fulltext-cache", action="store_true",
                    help="Fail if a full_text paper is missing out/fulltext/<pmid>.json")
    ap.add_argument("--online", action="store_true", help="Also verify live Europe PMC pubType + doi-check")
    ap.add_argument("--pr", help="Optional PR number for display")
    ap.add_argument("--out", help="Optional JSON summary output path")
    a = ap.parse_args()

    data_dir = (ROOT / a.data).resolve()
    ft_dir = (ROOT / a.fulltext).resolve()
    hygiene = check_hygiene(ROOT)
    wb_issues = check_workbooks(data_dir)
    ext_reports = [
        audit_extracted_file(p, ft_dir, require_fulltext_cache=a.require_fulltext_cache)
        for p in find_extracted_files(data_dir)
    ]

    live_issues = []
    if a.online:
        dedup = {}
        for p in find_extracted_files(data_dir):
            for rec in json.loads(p.read_text(encoding="utf-8")).get("papers", []):
                dedup[_paper_dedup_key(rec)] = rec
        live_issues = check_live_ids(list(dedup.values()))

    total_issues = list(hygiene) + list(wb_issues) + list(live_issues)
    for rep in ext_reports:
        total_issues.extend(rep["issues"])

    summary = {
        "pr": a.pr,
        "mode": "full_premerge" if (a.require_fulltext_cache and a.online) else "ci_offline",
        "hygiene_issues": hygiene,
        "workbook_issues": wb_issues,
        "live_id_issues": live_issues,
        "extracted": ext_reports,
        "pass": not total_issues,
    }
    if a.out:
        Path(a.out).write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"=== PR Review Bundle ({'PR #' + a.pr if a.pr else 'local'}, mode={summary['mode']}) ===")
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
