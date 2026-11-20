# CLAIMS.md: every number in the README and method docs, mapped to its source

Written 21 Nov 2026 by reading files only. Nothing was run in this pass. "Not run" = no fresh measurement; the figure is carried from an earlier recorded output. The one exception is row 21: `make test` was run on 21 Nov (47 passed). No claim here says the pipeline passes.

| Claim | Where stated | Source file / script | Status |
|---|---|---|---|
| 5 hypotheses, quoted exactly | README layout table | `hypotheses.json` from `parse_hypotheses.py` over `official/hypotheses.html` | Not re-run |
| H5 ranked first; PubMed hits 71 (H5), 47 (H1), 33 (H2), 227 (H3), 108 (H4); citations 84, 163, 140, 82, 107 | `HYPOTHESES.md` ranking table | `search.py --count-only` with `queries.json`; Europe PMC `citedByCount` (18 Nov 2026) | Not run (no saved output checked in this pass) |
| Screened 37 (H1), 40 (H5) | `HYPOTHESES.md` data decision | `datadecision.py report`, `out/dd/report.json` | Not run |
| Pass C1-C3: 0 (H1), 6 (H5); pass C1-C4: 0 (H1), 5 (H5) | `HYPOTHESES.md` | `out/dd/report.json` | Not run |
| Pass C1-C5: 0 / 1; numeric-effect papers 0 / 1 | `HYPOTHESES.md` (pre-correction table) | `out/dd/report.json` | Not run. C5 was later redefined as a submission-level count, so the C1-C5 row is superseded. |
| Widened pool 120 (80 new); still 5 pass C1-C4 (`n_pass_C1_C4_cap50` = 5); free full text 9 to 19; contrary findings 1 among passes, 2 in all; of 80 new, 52 fail C1, 15 pass it, none passes C2 + C3 | `HYPOTHESES.md` widening result | `out/dd/widen_run.log`, `out/dd/report.json`, `out/dd/pool_H5.json` | Not run |
| 4 near misses (41673700, 41102453, 40958776, 39056789) judged C3 "no" | `HYPOTHESES.md` | `out/dd/report.json` | Not run |
| Hand-check of the 5 passes against C3 (4 hold, 39532095 borderline) | `HYPOTHESES.md` | Orchestrator review of quotes in `out/dd/report.json`, 19 Nov. Not a physician check. | Not run; not clinically verified |
| 2.25-fold effect quote (PMID 42636814) | `HYPOTHESES.md` | `out/dd/report.json` | Not run |
| "10/10 findings, 11/11 number fields found verbatim" (seed 7, 10 of 13 findings with a number) | `out/verify_sample.md` line 17 (not in README text) | `verify_sample.py` | Existing output, not re-run. Checks the extractor against its own cached source text, not against a human expert. |
| Extraction reads about 9,000 characters per paper | README "Known gaps" | `extract.py` | Not run; value not re-read from code in this pass |
| "Free full-text fetch (PMC, Europe PMC, Unpaywall, DOI)" | README status | `fulltext.py`; route log `out/fulltext_report.json` | Not run |
| Dry run: 20 PubMed hits, 13 extractions | README Run section, Makefile (`fulltext.py --max 13`, `extract.py --max 13`) | `make dry-run` | Not run. README said 5; corrected to 13 to match the Makefile (the code is the source of truth). |
| Official validator: "SUBMISSION VALID (with suggestions), 0 to fix, 1 suggestion" | `out/validator_output.txt` (not in README) | `official/resources/validate_submission.py` on `out/dry_run.xlsx` | Existing output from an earlier dry run; not re-run. Not a real submission. |
| 39 test functions in `tests/` (3 + 6 + 27 + 3 by file) | counted by grep this pass | `tests/test_c1_rule.py`, `tests/test_extraction_guards.py`, `tests/test_pipeline.py`, `tests/test_widen.py` | Count above is from the 21 Nov grep (39 functions). **Tests now run: 47 passed, 0 failed on 2026-11-21 via `make test`** (39 existing + 8 new in `tests/test_verify.py`; source: `~/.hermes/cache/scratch/2026-11-21_shell-rerun.md`). An earlier audit note said 14. |
| 19-column workbook | README layout table | `to_template.py`, `official/resources/submission_template.xlsx` | Not run |
| Deadline end of 15 Jan 2027 AoE = Sat 16 Jan 13:00 Valencia | `SPEC.md` | `official/rules.html:1001`, page JS in `official/rules.html` | Verified in snapshot; live page not re-checked |
| 50-paper cap | `JUDGES.md`, `HYPOTHESES.md` | `official/rules.html:534` | Verified in snapshot |

## Not claimed
- `make test` passed locally on 2026-11-21 (47 passed). No claim that `make dry-run` or any CI run passes.
- No claim of accuracy against a human gold set. None exists.
- No physician check has been done; class, strength and relevance are model proposals.
- Figure-only values are not captured.
