# CLAIMS.md: every number in the README and method docs, mapped to its source

Updated 26 Nov 2026 from frozen outputs in `data/` after 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`) and `FREEZE.md` execution.

| Claim | Where stated | Source file / script | Status |
|---|---|---|---|
| 5 hypotheses, quoted exactly | `README.md` | `hypotheses.json` from `parse_hypotheses.py` over `official/hypotheses.html` | Verified in repo |
| H5 ranked first; PubMed hits 71 (H5), 47 (H1), 33 (H2), 227 (H3), 108 (H4); citations 84, 163, 140, 82, 107 | `HYPOTHESES.md`, `README.md` | `search.py` with `queries.json`; Europe PMC `citedByCount` (18 Nov 2026) | Verified from 18 Nov run |
| Screened 37 (H1), 40 (H5); widened H5 pool 120 (80 new); pass C1-C3: 0 (H1), 7 (H5); pass C1-C4: 0 (H1), 6 (H5); contrary 1 among passes, 2 in all | `HYPOTHESES.md`, `README.md` | `datadecision.py`, `data/dd/report.json`, `data/dd/pool_H5.json`, `data/dd/widen_run.log` | Verified by `scripts/verify.py` (`make verify`) |
| 4 near misses (41673700, 41102453, 40958776, 39056789) judged C3 "no" | `HYPOTHESES.md`, `README.md` | `data/dd/report.json` | Verified in frozen report |
| Hand-check of the 6 C1-C4 passes against C3 (5 hold incl. `29861287`, `39532095` borderline exogenous-ApoE) | `HYPOTHESES.md`, `README.md` | `data/dd/report.json`, `datadecision.py` | Verified + updated 26 Nov 2026 |
| Frozen H5 submission: 7 papers (6 `C1-C4` full-text `pmc_oa` + anchor `37777962`), 23 findings (incl. 1 `CONTRADICTING:` in `40457456`) | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `data/extracted.json`, `data/dry_run.xlsx`, `extract.py` | Verified 26 Nov 2026 (`make verify`) |
| 100% physician `A3` audit across 7 papers and 23 findings (P5.F4 H4 fix, P3.F2 LAMP2/lysosomal-activity replacement, P6.F5 contrary row, P7.F1-P7.F2 `29861287`) | `README.md`, `JUDGES.md` | `docs/PHYSICIAN_AUDIT_H5.md`, `extract.py`, `data/extracted.json` | Signed 26 Nov 2026 |
| Rule C4 identifier check: 7/7 PMIDs and DOIs verified live against PubMed and Europe PMC | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `verify_ids.py`, `data/id_verification.json` | Verified 26 Nov 2026 (`make verify`) |
| Verbatim stat check: 6/6 findings with numbers, 6/6 number fields found verbatim | `README.md`, `JUDGES.md` | `verify_sample.py`, `data/verify_sample.md` | Verified 26 Nov 2026 |
| Extraction reads up to 9,000 characters per paper (6,000-char chunks) | `README.md`, `extract.py` | `extract.py` (`PAPER_CHARS = 9000`, `CHUNK_CHARS = 6000`) | Verified in code |
| Free full-text fetch (PMC OA, Europe PMC, Unpaywall, DOI): 6/7 signed pool full text (`pmc_oa`), 1/7 (`37777962`) `unavailable` (Gold OA CC BY at Cell Reports, no PMCID, HTTP 403 automated) | `README.md` | `fulltext.py`, `data/fulltext_report.json` | Verified in code and route log |
| Official validator: `SUBMISSION VALID — no problems found.` on `data/dry_run.xlsx` | `README.md`, `JUDGES.md` | `data/validator_output.txt` via `make validate` | Verified 26 Nov 2026 |
| 57 unit test functions passing (`make test`) | `README.md` | `tests/test_c1_rule.py`, `tests/test_extraction_guards.py`, `tests/test_pipeline.py`, `tests/test_verify.py`, `tests/test_widen.py`, `tests/test_upgrades.py` | Verified 26 Nov 2026 (`make test`) |
| 19-column workbook (`Submission` + `Method` sheets) | `README.md` | `to_template.py`, `official/resources/submission_template.xlsx` | Verified by `check_schema.py` and `make validate` |
| SHA-256 freeze manifest (`data/FREEZE.json`), `make verify` passes 0 FAIL, 0 WARN | `README.md`, `FREEZE.md` | `data/FREEZE.json`, `scripts/verify.py` | Verified 26 Nov 2026 (`make verify`) |
| Deadline end of 15 Jan 2027 AoE = Sat 16 Jan 13:00 Valencia | `SPEC.md`, `JUDGES.md` | `official/rules.html:1001` | Verified in snapshot |
| 50-paper cap | `JUDGES.md`, `HYPOTHESES.md` | `official/rules.html:534`, `extract.py`, `check_schema.py` | Verified in snapshot and code |

## Not claimed
- Zero visual `~` + `estimated_from_figure` values were read from figure images in this text-only pass (`printed_in_text`, `not_found_in_source`, or `full_text_unavailable` only), although pipeline support and guards are implemented and tested.
- Hugging Face Space team registration and final upload (`Team`, `Team leader`, `Team leader email` on `Method` sheet) remain pending Ahmed's HF Space click before `Wed 13 Jan 2027 13:00 Valencia`.
