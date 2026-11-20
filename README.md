# hack-meccog-apoe4

> **DRAFT headline (placeholder, no result yet):** [HEADLINE RESULT TO BE WRITTEN AFTER THE SIGNED RUN: papers kept, findings extracted, share checked by a physician]. Nothing in this repo has been validated for submission. See `CLAIMS.md`.

Pipeline for the MecCog Challenge pilot (APOE4 endosome hypotheses, Step 1: papers and findings). Private until the
method README is final. Python standard library only; `openpyxl` (in a git-ignored `.venv`) is needed only to run the
official validator.

Status (18 Nov 2026): pipeline with free full-text fetch (PMC, Europe PMC, Unpaywall, DOI) and full-text extraction. The dry run is still not submittable: Method sheet is placeholders, classes and strengths are model proposals, figure-only values are not captured.

## Layout

| File | Job |
|---|---|
| `official/` | Organizer files (template, validator, example, hypotheses, rules) with `SOURCES.md` (URL, date, SHA-256) |
| `hypotheses.json`, `parse_hypotheses.py` | The 5 statements, quoted exactly from `official/hypotheses.html` |
| `HYPOTHESES.md` | Ranking for a physician and the top pick |
| `queries.json` | One draft PubMed query per hypothesis |
| `search.py` | PubMed esearch and efetch (key from Keychain `NCBI_API_KEY`, never printed) |
| `snowball.py` | Europe PMC references and citations of seed papers |
| `screen.py` | Title and abstract screening, `rwth-ask` (free Qwen), one call per batch of 10, strict JSON |
| `fulltext.py` | Free full text per PMID: PMC OA (efetch) -> Europe PMC -> Unpaywall (OA only) -> DOI link; HTML/XML, PDF only via `pdftotext`; cache `out/fulltext/`; per-paper route log |
| `extract.py` | Findings from full text (Results, tables, legends; chunked, one `rwth-ask` request at a time) or abstract; every number kept only as a verbatim quote from one source block, else null; Data location = that block's section/table |
| `verify_sample.py` | Seeded sample of findings with numbers: re-locates each quote in the cached source text, writes `out/verify_sample.md` |
| `to_template.py` | Writes the 19-column workbook (Submission and Method sheets) with zipfile and XML |
| `check_schema.py` | Own schema check, fallback to the official validator |
| `tests/` | Parsing tests on fixtures, no network: `make test` |

## Run

```
make test
make dry-run            # HYP=H5 by default; max 20 PubMed hits, 13 extractions (Makefile `--max 13`), writes out/dry_run.xlsx and validates it
```

## Verify (offline, for a stranger)

```
make test
make verify             # checks the committed data/ dir; needs no key, no network, no rwth-ask
```

Re-running the pipeline is optional: the NCBI key (macOS Keychain, service `NCBI_API_KEY`, never stored in files) and
`rwth-ask` are only needed to regenerate. What is frozen and why: `FREEZE.md`. Status: `data/` is not committed yet, so
`make verify` fails until the freeze is done.

## Known gaps before a real submission

- Full text is fetched only by free routes (no proxy, no Sci-Hub, no login). A paper is `full_text_unavailable` only if the
  route log in `out/fulltext_report.json` shows every route tried. Closed papers stay abstract-only.
- Figure-only values are not captured: a number not quoted in the text/table is N/A `not_found_in_source` (it may sit in a
  figure: `visual_only` / `estimated_from_figure` is not implemented). P values are never estimated or computed.
- Extraction reads about 9,000 characters of the most relevant Results/table/legend blocks per paper (keyword-ranked): slow
  free model, so coverage of each paper is partial.
- Directness class, strength and relevance are model proposals and need the physician check.
- The Method sheet in the dry run holds placeholders (team, leader, commit SHA).

## Method README (public, to be written for submission)

Six sections per `official/resources/method_README_template.md`: who did the work, model and version, how papers were
found, how full text was obtained, what a human checked (share of findings), anything else. To be written by Ahmed
from what actually happened; nothing is pre-filled.
