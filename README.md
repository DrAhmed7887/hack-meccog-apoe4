# hack-meccog-apoe4

Pipeline for the MecCog Challenge pilot (APOE4 endosome hypotheses, Step 1: papers and findings). Private until the
method README is final. Python standard library only; `openpyxl` (in a git-ignored `.venv`) is needed only to run the
official validator.

Status (18 Nov 2026): skeleton plus dry run. Not submittable: extraction reads abstracts only, no full text yet.

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
| `extract.py` | Findings from abstracts via `rwth-ask`; every number kept only with a verbatim quote, else null |
| `to_template.py` | Writes the 19-column workbook (Submission and Method sheets) with zipfile and XML |
| `check_schema.py` | Own schema check, fallback to the official validator |
| `tests/` | Parsing tests on fixtures, no network: `make test` |

## Run

```
make test
make dry-run            # HYP=H5 by default; max 20 PubMed hits, 5 extractions, writes out/dry_run.xlsx and validates it
```

## Known gaps before a real submission

- Full text (PMC, Europe PMC, Unpaywall, publisher) is not fetched. Until it is, a number missing from an abstract is
  written as N/A with `full_text_unavailable`, which the rules allow only after those routes were tried.
- Data location is always "Abstract" at this stage; panel-level locations need full text.
- Directness class, strength and relevance are model proposals and need the physician check.
- The Method sheet in the dry run holds placeholders (team, leader, commit SHA).

## Method README (public, to be written for submission)

Six sections per `official/resources/method_README_template.md`: who did the work, model and version, how papers were
found, how full text was obtained, what a human checked (share of findings), anything else. To be written by Ahmed
from what actually happened; nothing is pre-filled.
