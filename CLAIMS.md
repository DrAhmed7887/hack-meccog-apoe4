# CLAIMS.md: every number in the README and method docs, mapped to its source

Updated 26 Nov 2026 from verified outputs of the signed `H5` pre-freeze run (nothing in `data/` frozen yet; `A3` physician audit pending in `docs/PHYSICIAN_AUDIT_H5.md`).

| Claim | Where stated | Source file / script | Status |
|---|---|---|---|
| 5 hypotheses, quoted exactly | README layout table | `hypotheses.json` from `parse_hypotheses.py` over `official/hypotheses.html` | Verified in repo |
| H5 ranked first; PubMed hits 71 (H5), 47 (H1), 33 (H2), 227 (H3), 108 (H4); citations 84, 163, 140, 82, 107 | `HYPOTHESES.md` ranking table | `search.py --count-only` with `queries.json`; Europe PMC `citedByCount` (18 Nov 2026) | Carried from 18 Nov run |
| Screened 37 (H1), 40 (H5); widened H5 pool 120 (80 new); pass C1-C3: 0 (H1), 6 (H5); pass C1-C4: 0 (H1), 5 (H5); contrary 1 among passes, 2 in all | `HYPOTHESES.md` data decision | `datadecision.py report`, `out/dd/report.json`, `out/dd/pool_H5.json`, `out/dd/widen_run.log` | Verified by `scripts/verify.py` (`make verify DATA=out`) |
| 4 near misses (41673700, 41102453, 40958776, 39056789) judged C3 "no" | `HYPOTHESES.md` | `out/dd/report.json` | Carried from 19 Nov `out/dd/report.json` |
| Hand-check of the 5 passes against C3 (4 hold, 39532095 borderline) | `HYPOTHESES.md` | Orchestrator review of quotes in `out/dd/report.json` (19 Nov); `39532095` constrained in `datadecision.py` | Carried; `A3` physician audit pending |
| Signed H5 pool: 6 papers (5 `C1-C4` full-text + anchor `37777962`), 22 findings extracted | `README.md`, `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `out/extracted.json`, `out/dry_run.xlsx`, `datadecision.py` | Verified 26 Nov 2026 (`make verify DATA=out`) |
| Rule C4 identifier check: 6/6 PMIDs and DOIs verified live against PubMed and Europe PMC | `JUDGES.md`, `docs/PHYSICIAN_AUDIT_H5.md` | `verify_ids.py`, `out/id_verification.json` | Verified 26 Nov 2026 |
| Verbatim stat check: 7/7 findings with numbers, 7/7 number fields found verbatim | `README.md`, `JUDGES.md` | `verify_sample.py`, `out/verify_sample.md` | Verified 26 Nov 2026 |
| Extraction reads about 9,000 characters per paper | `README.md`, `extract.py` | `extract.py` (`PAPER_CHARS = 9000`, `CHUNK_CHARS = 6000`) | Verified in code |
| Free full-text fetch (PMC, Europe PMC, Unpaywall, DOI) | `README.md` | `fulltext.py`, `out/fulltext_report.json` | Verified in code and route log |
| Official validator: `SUBMISSION VALID — no problems found.` on `out/dry_run.xlsx` | `README.md`, `JUDGES.md` | `out/validator_output.txt` via `make validate` | Verified 26 Nov 2026 (`make validate`) |
| 56 unit test functions passing (`make test`: 47 existing + 9 new in `tests/test_upgrades.py`) | `README.md` | `tests/test_c1_rule.py`, `tests/test_extraction_guards.py`, `tests/test_pipeline.py`, `tests/test_verify.py`, `tests/test_widen.py`, `tests/test_upgrades.py` | Verified 26 Nov 2026 (`make test`) |
| 19-column workbook | `README.md` | `to_template.py`, `official/resources/submission_template.xlsx` | Verified by `check_schema.py` and `make validate` |
| Deadline end of 15 Jan 2027 AoE = Sat 16 Jan 13:00 Valencia | `SPEC.md` | `official/rules.html:1001` | Verified in snapshot |
| 50-paper cap | `JUDGES.md`, `HYPOTHESES.md` | `official/rules.html:534`, `extract.py`, `check_schema.py` | Verified in snapshot and code |

## Not claimed
- No `A3` physician sign-off has been completed yet; `docs/PHYSICIAN_AUDIT_H5.md` lists the 22 findings and flagged decisions for Ahmed's review.
- Zero visual `~` + `estimated_from_figure` values were read from figure images in this text-only pass (`printed_in_text`, `not_found_in_source`, or `full_text_unavailable` only), although pipeline support and guards are implemented and tested.
- `data/` is not frozen yet; `FREEZE.json` waits for Ahmed's `A3` audit.
