# CLAIMS.md: every number in the README and method docs, mapped to its source

Updated 27 Nov 2026 from frozen H5 v3 outputs in `data/` after 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`) and `FREEZE.md` execution.

| Claim | Where stated | Source file / script | Status |
|---|---|---|---|
| 5 hypotheses, quoted exactly | `README.md`, `HYPOTHESES.md` | `hypotheses.json` from `parse_hypotheses.py` over `official/hypotheses.html` | Verified in repo |
| Benchmark widening counts (screened 37 H1 / 120 H5, pass 0 H1 / 6 H5) | `HYPOTHESES.md`, `README.md` | `datadecision.py`, `data/dd/report.json`, `data/dd/pool_H5.json`, `data/dd/widen_run.log` | Verified by `scripts/verify.py` (`make verify`) |
| Frozen H5 v3 submission: 19 papers (10 Tier 1 + 9 Tier 2), 68 findings (54 supporting, 14 `CONTRADICTING:`) | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `data/extracted.json`, `data/dry_run.xlsx`, `extract.py`, `to_template.py` | Verified 27 Nov 2026 (`make verify`) |
| `Method` sheet uses `Who did the work: collab` and comma-separated model list | `README.md`, `JUDGES.md` | `to_template.py` (`DRY_METHOD`), `data/dry_run.xlsx` | Verified by `check_schema.py` & `scripts/pr_review_bundle.py` |
| 100% physician `A3` audit across 19 papers and 68 findings (0 unresolved `[PHYSICIAN REVIEW REQUIRED]` flags) | `README.md`, `JUDGES.md`, `SPEC.md` | `docs/PHYSICIAN_AUDIT_H5.md`, `data/extracted.json`, `data/dry_run.xlsx` | Signed 27 Nov 2026 |
| Rule C4 live ID check: 19/19 PMIDs/DOIs verified; 0 retractions; 0 reviews | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `verify_ids.py`, `data/id_verification.json`, `scripts/pr_review_bundle.py` | Verified 27 Nov 2026 live (`--online`) |
| Verbatim stat check: 15/15 sampled numeric findings (22/22 fields) verified verbatim | `README.md`, `JUDGES.md`, `FREEZE.md` | `verify_sample.py`, `data/verify_sample.md` | Verified 27 Nov 2026 |
| Stats provenance: 62 `printed_in_text`, 2 visually verified `visual_only` (`34919811` Fig 4E, `42274838` Fig 4D); 0 estimated P values | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `data/extracted.json`, `extract.py`, `docs/PHYSICIAN_AUDIT_H5.md` | Verified 27 Nov 2026 |
| Uncapped full-text extraction (`PAPER_CHARS=None`, `CHUNK_CHARS=6000`) & 17/19 OA full text (`15 pmc_oa`, `1 unpaywall`, `1 doi_direct`, `2 unavailable`) | `README.md`, `FREEZE.md` | `fulltext.py`, `extract.py`, `data/fulltext_report.json` | Verified 27 Nov 2026 |
| Official validator: `SUBMISSION VALID — no problems found.` on `data/dry_run.xlsx` (`--strict`) | `README.md`, `JUDGES.md`, `FREEZE.md` | `data/validator_output.txt` via `official/resources/validate_submission.py` | Verified 27 Nov 2026 |
| 68 unit tests passing (`make test`) & 11-file SHA-256 freeze (`data/FREEZE.json`, `make verify` 0 FAIL / 0 WARN) | `README.md`, `FREEZE.md` | `tests/test_c1_rule.py`, `tests/test_extraction_guards.py`, `tests/test_pipeline.py`, `tests/test_verify.py`, `tests/test_widen.py`, `tests/test_upgrades.py`, `tests/test_pr_review_bundle.py`, `tests/test_phase2_upgrades.py`, `data/FREEZE.json`, `scripts/verify.py` | Verified 27 Nov 2026 |
| 50-paper cap & deadline (`end of 15 Jan 2027 AoE` = Sat 16 Jan 2027 13:00 Valencia) | `JUDGES.md`, `SPEC.md` | `official/rules.html`, `extract.py`, `check_schema.py` | Verified in snapshot & code |

## Not claimed
- Zero `~` + `estimated_from_figure` bar estimates were added beyond OA text/table values and the two visually verified `visual_only` star P values (`PMC8758949` Fig 4E, `PMC13260029` Fig 4D); missing stats carry `not_found_in_source` or `full_text_unavailable`.
- Elsevier ScienceDirect (`37777962`) presented Cloudflare Turnstile in browser check and was immediately closed without bypassing (`Abstract` only).
- Final release workbook upload on HF Space (`Team`, real email, final `Commit SHA`) awaits Ahmed's HITL review before `Wed 13 Jan 2027 13:00 Valencia`.
