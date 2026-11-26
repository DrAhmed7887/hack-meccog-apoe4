# CLAIMS.md: every number in the README and method docs, mapped to its source

Updated 27 Nov 2026 from frozen H5 v3 outputs in `data/` after 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`) and `FREEZE.md` execution.

| Claim | Where stated | Source file / script | Status |
|---|---|---|---|
| 5 hypotheses, quoted exactly | `README.md`, `HYPOTHESES.md` | `hypotheses.json` from `parse_hypotheses.py` over `official/hypotheses.html` | Verified in repo |
| Benchmark widening counts (screened 37 H1 / 120 H5, pass 0 H1 / 6 H5) | `HYPOTHESES.md`, `README.md` | `datadecision.py`, `data/dd/report.json`, `data/dd/pool_H5.json`, `data/dd/widen_run.log` | Verified by `scripts/verify.py` (`make verify`) |
| Frozen H5 v3 submission: 19 primary records (18 peer-reviewed + 1 `PubMed preprint`; 10 Tier 1 + 9 Tier 2), 67 findings (53 supporting, 14 `CONTRADICTING:`) | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `data/extracted.json`, `data/dry_run.xlsx`, `extract.py`, `to_template.py` | Verified 27 Nov 2026 (`make verify`) |
| `Method` sheet uses `Who did the work: collab` and comma-separated model list | `README.md`, `JUDGES.md` | `to_template.py` (`DRY_METHOD`), `data/dry_run.xlsx` | Verified by `check_schema.py` & `scripts/pr_review_bundle.py` |
| 100% physician `A3` audit across 19 papers and 67 findings (0 unresolved `[PHYSICIAN REVIEW REQUIRED]` flags) | `README.md`, `JUDGES.md`, `SPEC.md` | `docs/PHYSICIAN_AUDIT_H5.md`, `data/extracted.json`, `data/dry_run.xlsx` | Signed 27 Nov 2026 |
| Rule C4 live ID check: 19/19 PMIDs/DOIs verified; 0 retractions; 0 reviews | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `verify_ids.py`, `data/id_verification.json`, `scripts/pr_review_bundle.py` | Verified 27 Nov 2026 live (`--online`) |
| Verbatim stat check: 14/14 sampled numeric findings (20/20 fields) verified verbatim | `README.md`, `JUDGES.md`, `FREEZE.md` | `verify_sample.py`, `data/verify_sample.md` | Verified 27 Nov 2026 |
| Stats provenance: 62 populated cells out of 201 (`46` effect sizes, `12` P values, `4` sample sizes) are 100% `printed_in_text`; 0 estimated/visual P values; `58/63` full-text (`58/67` overall) panel/table locations | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `data/extracted.json`, `extract.py`, `docs/PHYSICIAN_AUDIT_H5.md` | Verified 27 Nov 2026 |
| Uncapped full-text extraction (`PAPER_CHARS=None`, `CHUNK_CHARS=6000`) & 17/19 OA full text (`15 pmc_oa`, `1 unpaywall`, `1 doi_direct`, `2 unavailable`) | `README.md`, `FREEZE.md` | `fulltext.py`, `extract.py`, `data/fulltext_report.json` | Verified 27 Nov 2026 |
| Official validator: `SUBMISSION VALID — no problems found.` on `data/dry_run.xlsx` (`--strict`) | `README.md`, `JUDGES.md`, `FREEZE.md` | `data/validator_output.txt` via `official/resources/validate_submission.py` | Verified 27 Nov 2026 |
| 68 unit tests passing (`make test`) & 11-file SHA-256 freeze (`data/FREEZE.json`, `make verify` 0 FAIL / 0 WARN) | `README.md`, `FREEZE.md` | `tests/test_c1_rule.py`, `tests/test_extraction_guards.py`, `tests/test_pipeline.py`, `tests/test_verify.py`, `tests/test_widen.py`, `tests/test_upgrades.py`, `tests/test_pr_review_bundle.py`, `tests/test_phase2_upgrades.py`, `data/FREEZE.json`, `scripts/verify.py` | Verified 27 Nov 2026 |
| 50-paper cap & deadline (`end of 15 Jan 2027 AoE` = Sat 16 Jan 2027 13:00 Valencia) | `JUDGES.md`, `SPEC.md` | `official/rules.html`, `extract.py`, `check_schema.py` | Verified in snapshot & code |

## Not claimed
- Zero `estimated_from_figure` or `visual_only` values remain in the frozen H5 v3 workbook: every populated statistic is `printed_in_text`, while missing stats carry `not_found_in_source` or `full_text_unavailable`.
- Elsevier ScienceDirect (`37777962`) presented Cloudflare Turnstile in browser check and was immediately closed without bypassing (`Abstract` only).
- Final release workbook upload on HF Space (`Team`, real email, final `Commit SHA`) awaits team leader verification before `Wed 13 Jan 2027 13:00 Valencia`.
