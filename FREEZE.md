# FREEZE.md: what is committed, and what is optional to regenerate

Status: **FROZEN (26 Nov 2026).** Ahmed signed `H5`, `Strict C3`, the 5-paper `C1–C4` pool (+ anchor `37777962`), and the 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`). Frozen outputs live in `data/` with SHA-256 verification in `data/FREEZE.json`, and `make verify` passes **0 FAIL, 0 WARN** offline.

## Verify path (needs nothing but Python 3 and this repo)

```
make test      # 57 unit tests on fixtures, offline
make verify    # SHA-256, schema, report, ID, and CLAIMS.md checks on committed data/ dir
```

`make verify` never calls PubMed, Europe PMC, Unpaywall, `rwth-ask` or the Keychain, and requires no `out/` directory.

## Regenerate steps (optional, not needed for verify)

These re-run the pipeline. A reader without them can still verify the frozen data.

| Step | Needs | Script |
|---|---|---|
| PubMed search | NCBI API key in the macOS Keychain, service name `NCBI_API_KEY` (optional: works without a key at a lower rate limit). The key is never printed or stored in this repo. | `search.py` |
| Citation snowball | Network (Europe PMC, no key) | `snowball.py` |
| Screening and extraction | `rwth-ask` (free RWTHgpt CLI, available to the author only). Output is model-dependent, so a re-run will not reproduce the frozen findings verbatim without `apply_h5_physician_audit` post-rules. | `screen.py`, `extract.py` |
| Full-text fetch | Network (PMC, Europe PMC, Unpaywall, DOI) | `fulltext.py` |

## Frozen manifest (`data/FREEZE.json`)

Target dir `data/`, with `data/FREEZE.json` = `{"files": {"<path relative to data/>": "<sha256>"}}`.

| Committed in `data/` | From | Why | Status |
|---|---|---|---|
| `data/dd/report.json` | `out/dd/report.json` | C1-C4 verdicts with quotes; `verify.py` recomputes counts | Frozen |
| `data/dd/pool_H5.json` | `out/dd/pool_H5.json` | 120-paper candidate pool behind H5 counts | Frozen |
| `data/dd/screen_H5.json`, `data/dd/ft_H5.json` | `out/dd/` | Screening and full-text route log for the H5 pool | Frozen |
| `data/dd/widen_run.log` | `out/dd/widen_run.log` | Widening run log (cited by `CLAIMS.md`) | Frozen |
| `data/extracted.json` | `out/extracted.json` | Audited 6-paper, 21-finding extraction (`H5`) | Frozen |
| `data/id_verification.json` | `out/id_verification.json` | Live PubMed + Europe PMC Rule C4 verification (`6/6`) | Frozen |
| `data/fulltext_report.json` | `out/fulltext_report.json` | Free full-text route log per PMID | Frozen |
| `data/verify_sample.md` | `out/verify_sample.md` | `6/6` verbatim numeric field verification output | Frozen |
| `data/dry_run.xlsx` | `out/dry_run.xlsx` | Validated 19-column submission workbook (`Method` pinned to commit SHA) | Frozen |
| `data/validator_output.txt` | `out/validator_output.txt` | Official validator result (`SUBMISSION VALID — no problems found.`) | Frozen |
| **not committed** | `out/fulltext/` (33 files, ~4.9 MB) | Cached raw full-text blocks; omitted for publisher licence compliance | Licence-excluded |
| **not committed** | `out/search.json`, `snowball.json`, `screened*.json`, `extract_cache/`, `extract_log*.txt` | Scratch intermediates | Ignored in `out/` |

### Signed paper pool & extraction policy (25–26 Nov 2026)

- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Strict `C3`:** Measured late-endosome/lysosome readout only (do NOT widen to general lipid handling or pad per `official/rules.html:429,529-534`).
- **Signed pool:** Focused strict `C1–C4` pool of 5 free-full-text papers (`34919811`, `35750033`, `40457456` [preserving contrary `C5=yes` finding], `42636814`, plus borderline `39532095` kept with its exact exogenous-ApoE human-neuron experimental system and lower directness class per `official/rules.html:469`) + anchor paper `37777962` (abstract-only; note `C4: no`).
- **Rule `C3` figure-estimate policy (`official/rules.html:537-542`):** Pipeline guards for `~` + `estimated_from_figure` are active and tested; `0` visual figure estimates were added in this text-only extraction pass.
- **Full-text licence compliance:** Cached raw full text (`out/fulltext/`) is never committed to the public repository; readers can re-fetch open-access text via `fulltext.py` using `data/fulltext_report.json`.
