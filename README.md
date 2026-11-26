# hack-meccog-apoe4

> **Pre-freeze status (26 Nov 2026):** Signed `H5` pool run produced **6 papers, 22 findings** (`out/dry_run.xlsx`), **6/6** PMIDs/DOIs verified (`out/id_verification.json`), **7/7** number fields verified verbatim (`out/verify_sample.md`), and **`SUBMISSION VALID — no problems found.`** (`make validate`). **Awaiting Ahmed's 5-minute `A3` physician audit (`docs/PHYSICIAN_AUDIT_H5.md`) before freezing `data/`.** See `CLAIMS.md`.

Pipeline for the MecCog Challenge pilot (APOE4 endosome hypotheses, Step 1: papers and findings). Private until the method README is final. Python standard library only; `openpyxl` (in a git-ignored `.venv`) is needed only to run the official validator.

## Layout

| File | Job |
|---|---|
| `official/` | Organizer files (template, validator, example, hypotheses, rules) with `SOURCES.md` (URL, date, SHA-256) |
| `hypotheses.json`, `parse_hypotheses.py` | The 5 statements, quoted exactly from `official/hypotheses.html` |
| `HYPOTHESES.md` | Ranking for a physician and the signed `H5` decision |
| `queries.json`, `search.py`, `snowball.py` | PubMed search (`NCBI_API_KEY` from Keychain) and Europe PMC citation snowball |
| `screen.py`, `datadecision.py` | Batch abstract screening and strict `C1`–`C4` pool selection (`select` stage, `<= 50` cap, contrary findings preserved) |
| `fulltext.py` | Free full text per PMID: PMC OA -> Europe PMC -> Unpaywall (OA) -> DOI; caches `out/fulltext/`; route log `out/fulltext_report.json` |
| `extract.py` | Findings from full text (`PAPER_CHARS=9000`) or abstract; Rule C1 selection (`<= 50`), verbatim quote guard, Rule C3 `~` + `estimated_from_figure` support (rejected on P values) |
| `verify_ids.py`, `verify_sample.py` | Rule C4 deterministic PMID/DOI existence check (`out/id_verification.json`) and verbatim number audit (`out/verify_sample.md`) |
| `to_template.py`, `check_schema.py` | Writes and schema-checks the 19-column workbook (`Submission` and `Method` sheets), enforcing Rule C3 provenance guards |
| `docs/PHYSICIAN_AUDIT_H5.md` | 5-minute physician `A3` audit sheet for all 22 extracted `H5` findings |
| `tests/` | Offline unit tests (56 tests passing): `make test` |

## Run & Verify

```
make test               # 56 offline unit tests
make verify DATA=out    # pre-freeze check on out/ (schema, counts, id_verification, CLAIMS.md)
make validate           # isolated official validator (/private/tmp) on out/dry_run.xlsx
make verify             # offline check of committed data/ (after FREEZE.md is executed)
```

## Known gaps before submission

- Physician `A3` audit pending (`docs/PHYSICIAN_AUDIT_H5.md`): confirm `class`/`strength`/`relevance`, fix `39532095` `P5.F4` H4-cell-line label, and decide on adding `40457456`'s `C5=yes` contrary finding row and any visual `~` + `estimated_from_figure` bar/dot measurements.
- Full text uses free OA routes only (`37777962` stays abstract-only with `full_text_unavailable`); extraction reads up to 9,000 chars of top-ranked Results/table/legend blocks per paper.
- `Method` sheet holds dry-run placeholders until team registration, public repo release, and `FREEZE.md` execution.
- Public Method README (`official/resources/method_README_template.md`, six sections including AI-use disclosure) to be finalized by Ahmed at freeze time.
