# FREEZE.md: what is committed, and what is optional to regenerate

Status: **FROZEN H5 v3 (27 Nov 2026).** 19 clean non-review, non-retracted primary papers (**10 Tier 1** human non-AD/non-aged cells + **9 Tier 2** model systems with caveats), **68 findings** (**54 supporting, 14 contradicting**), **19/19** live PubMed/Europe PMC/DOI verifications (`0` retractions), and 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`). Frozen outputs live in `data/` with SHA-256 verification in `data/FREEZE.json`, and `make verify` passes **0 FAIL, 0 WARN** offline.

## Verify path (needs nothing but Python 3 and this repo)

```sh
make test      # 68 offline unit tests (standard library only)
make verify    # SHA-256, schema, report, ID, and CLAIMS.md checks on committed data/ dir
make validate  # official organizer validator --strict on data/dry_run.xlsx
```

## Regenerate steps (optional, not needed for verify)

| Step | Needs | Script |
|---|---|---|
| PubMed search & snowball | Optional NCBI API key in Keychain; Europe PMC REST | `search.py`, `snowball.py` |
| Screening & checklist | `rwth-ask` / agent pipeline; tiered `C1–C5` | `screen.py`, `datadecision.py` |
| OA full-text fetch | Network (PMC, Europe PMC, Unpaywall, DOI) | `fulltext.py` |
| Extraction & workbook build | Cached `out/fulltext/` + audit sign-off + schema/ID guards | `extract.py`, `verify_ids.py`, `to_template.py` |

## Frozen manifest (`data/FREEZE.json`)

Target dir `data/`, with `data/FREEZE.json` = `{"files": {"<path relative to data/>": "<sha256>"}}`.

| Committed in `data/` | From | Why | Status |
|---|---|---|---|
| `data/dd/report.json` | `out/dd/report.json` | Early Qwen widening benchmark counts (`screened 120`, `H1 0`, `H5 6`) | Frozen |
| `data/dd/pool_H5.json`, `screen_H5.json`, `ft_H5.json`, `widen_run.log` | `out/dd/` | Reproducible widening pool & screening logs | Frozen |
| `data/extracted.json` | H5 v3 merge | Audited **19-paper, 68-finding** extraction (`H5`; `14` contradicting) | Frozen (v3) |
| `data/id_verification.json` | `verify_ids.py` | Live PubMed + Europe PMC Rule C4 verification (`19/19`) | Frozen (v3) |
| `data/fulltext_report.json` | `fulltext.py` | Free OA route log (`15 pmc_oa`, `1 unpaywall`, `1 doi_direct`, `2 unavailable`) | Frozen (v3) |
| `data/verify_sample.md` | `verify_sample.py` | `15/15` sampled numeric findings (`22/22` fields) verbatim | Frozen (v3) |
| `data/dry_run.xlsx` | `to_template.py` | Validated 19-column workbook (`Who did the work: collab`) | Frozen (v3) |
| `data/validator_output.txt` | `validate_submission.py --strict` | `SUBMISSION VALID — no problems found.` (`RC=0`) | Frozen (v3) |
| **not committed** | `out/fulltext/` (gitignored) | Cached raw OA XML/HTML/JSON blocks excluded per publisher licences | Licence-excluded |
| **not committed** | `out/search.json`, `screened*.json`, `release_method.json` | Scratch & local release identity intermediates | Ignored in `out/` |
