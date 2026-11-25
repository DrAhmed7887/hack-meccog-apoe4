# FREEZE.md: what is committed, and what is optional to regenerate

Status: SIGNED DIRECTION (25 Nov 2026); `data/` not frozen yet. Ahmed signed `H5`, `Strict C3`, the 5-paper `C1–C4` pool (+ anchor `37777962` if abstract-only/non-OA permitted), and enabling `~` + `estimated_from_figure` in January extraction. Copying into `data/` and freezing wait for the January extraction pass, physician `A3` audit, and `make validate`.

## Verify path (needs nothing but Python 3 and this repo)

```
make test      # unit tests on fixtures, offline
make verify    # schema, counts and CLAIMS.md file references on the committed data/ dir
```

`make verify` never calls PubMed, Europe PMC, Unpaywall, `rwth-ask` or the Keychain.

## Regenerate steps (optional, not needed for verify)

These re-run the pipeline. A reader without them can still verify the frozen data.

| Step | Needs | Script |
|---|---|---|
| PubMed search | NCBI API key in the macOS Keychain, service name `NCBI_API_KEY` (optional: works without a key at a lower rate limit). The key is never printed or stored in this repo. | `search.py` |
| Citation snowball | Network (Europe PMC, no key) | `snowball.py` |
| Screening and extraction | `rwth-ask` (free RWTHgpt CLI, available to the author only). Output is model-dependent, so a re-run will not reproduce the frozen findings exactly. | `screen.py`, `extract.py` |
| Full-text fetch | Network (PMC, Europe PMC, Unpaywall, DOI) | `fulltext.py` |

## Freeze manifest (execute in January after re-extraction and `A3` audit)

Target dir `data/`, with `data/FREEZE.json` = `{"files": {"<path relative to data/>": "<sha256>"}}`.

| Commit as | From | Size | Why | Decision |
|---|---|---|---|---|
| `data/dd/report.json` | `out/dd/report.json` | 166 KB | C1-C4 verdicts with quotes; `verify.py` recomputes the counts | Needed |
| `data/dd/pool_H5.json` | `out/dd/pool_H5.json` | 242 KB | the 120-paper candidate pool behind the counts | Needed for H5 |
| `data/dd/screen_H5.json`, `ft_H5.json` | `out/dd/` | 64 KB, 13 KB | screening and route log for the pool | Needed for H5 |
| `data/dd/*_H1.*`, `pool_H1.json` | `out/dd/` | ~94 KB | H1 comparison (H1 passes 0) | Option: commit only if H1 stays in the method story |
| `data/dd/widen_run.log`, `screen.log`, `ft.log` | `out/dd/` | ~9 KB | run logs | `widen_run.log` Needed (cited by CLAIMS.md row 12, checked by `verify.py`); `screen.log`, `ft.log` Option |
| `data/extracted.json` | `out/extracted.json` | 79 KB | extracted findings. **This file is a 13-paper dry run from 18 Nov (seed 7), not the final list.** | Re-extract on the signed pool, then freeze that |
| `data/extract_cache/` | `out/extract_cache/` | 64 KB | per-paper model replies (9 files) | Option: lets a reader see raw extraction |
| `data/fulltext_report.json` | `out/fulltext_report.json` | 6 KB | route log: which free route supplied each paper | Needed |
| `data/fulltext/` | `out/fulltext/` | 2.4 MB, 33 files | cached free full text so `verify_sample.py` can re-find quotes offline | **Licence check first** (see below) |
| `data/verify_sample.md` | `out/verify_sample.md` | 4 KB | the 10/10 verbatim check output | Needed |
| `data/dry_run.xlsx` | `out/dry_run.xlsx` | 13 KB | the workbook that `verify.py` schema-checks | Freeze the final workbook, not the dry run. If it is renamed (e.g. `submission.xlsx`), update the `out/dry_run.xlsx` references in `CLAIMS.md` in the same commit or `verify.py` fails |
| `data/validator_output.txt` | `out/validator_output.txt` | 0.5 KB | official validator result | Needed, but rerun on the final workbook |
| not committed | `out/search.json`, `snowball.json`, `screened.json`, `extracted_abstract_only.json`, `extract_log*.txt` | ~190 KB | superseded dry-run intermediates | Leave ignored |

### Signed paper pool & extraction policy (25 Nov 2026)

- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Strict `C3`:** Measured late-endosome/lysosome readout only (do NOT widen to general lipid handling or pad per `official/rules.html:429,529-534`).
- **Signed pool:** Focused strict `C1–C4` pool of 5 free-full-text papers (`34919811`, `35750033`, `40457456` [preserving contrary `C5=yes` finding], `42636814`, plus borderline `39532095` kept with its exact exogenous-ApoE human-neuron experimental system and lower directness class per `official/rules.html:469`) + anchor paper `37777962` (if abstract-only/non-OA permitted; note `C4: no`). In `out/dd/report.json`, `pass_C1_C4 = 5` corresponds to those exact five `C4=yes` PMIDs while `37777962` has `C4: no`.
- **Rule `C3` figure-estimate policy (`official/rules.html:537-542`):** Approved enabling `~` prefix + `estimated_from_figure` provenance for bar-chart effect sizes and plotted-point sample sizes (never P values) in the January extraction pass.
- **Remaining human/January items:** Institutional HF account (`ahmed.zayed@rwth-aachen.de`), team name + Ahmed as leader, live rules check on HF Space, January extraction + physician `A3` audit + `FREEZE.md` + `make validate` (submit-by `Wed 13 Jan 2027 13:00 Valencia`).

### Full-text licence caveat

The 33 files in `out/fulltext/` include text fetched from PMC OA, Europe PMC and Unpaywall. Committing them to a public repo may breach per-article licences (not all PMC articles are CC-BY). Safer route: commit only the route log (`fulltext_report.json`) plus, for each quote, the quote and its location, and let `fulltext.py` re-fetch. That makes quote re-verification need the network, so `verify.py` currently checks quote presence only structurally. Ahmed or a licence check decides.

## Proposed `.gitignore` diff (not applied)

```diff
 .venv/
-out/
+out/*
+!out/.gitkeep
 __pycache__/
 *.pyc
 .DS_Store
 method.json
+.tmp/
+.pytest_cache/
```

`out/` stays ignored as scratch; the frozen copies live in the tracked `data/`. `.tmp/` holds `xcrun_db` (a local file, mode 600, not inspected): keep it out of git.

## Before going public

Run a history and secrets scan first (`git log -p` for key-like strings). `common.py` reads the NCBI key from the Keychain only, so no key is expected in files, but this has not been checked.
