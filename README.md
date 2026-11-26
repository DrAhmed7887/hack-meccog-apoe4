# hack-meccog-apoe4

**Status (26 Nov 2026, frozen):** Hypothesis `H5` submission built and verified offline (**6 papers, 21 findings** including **1 `CONTRADICTING:`** row in `data/dry_run.xlsx`), **6/6** PMIDs/DOIs verified (`data/id_verification.json`), **6/6** numeric findings verified verbatim (`data/verify_sample.md`), **57** unit tests passing (`make test`), `make verify` (**0 FAIL, 0 WARN**), and **`SUBMISSION VALID — no problems found.`** (`data/validator_output.txt`).

- **Team:** Pending Hugging Face Space team registration (lead: Dr Ahmed Zayed)
- **Hypothesis:** `H5` — *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Freeze date:** 2026-11-26

---

## 1. Who did the work

**Both** (`Who did the work: both` in the workbook `Method` sheet) — a physician-engineer (**Dr Ahmed Zayed**) and AI agents worked together, with deterministic Python scripts enforcing verbatim-quote, provenance, identifier, and schema guards:
- **Human (`Dr Ahmed Zayed`):** Signed hypothesis selection (`H5`), `Strict C3` scope, borderline-paper constraints (`39532095`), and completed a **100% physician `A3` audit** across all 6 papers and extracted findings (`docs/PHYSICIAN_AUDIT_H5.md`).
- **AI agents (`qwen3.8-27b` via `rwth-ask`; coding/audit orchestration):** Ran batch abstract screening, full-text checklist evaluation (`C1`–`C5`), and per-finding extraction (`extract.py`), plus pipeline tests, verification scripts, and freeze packaging.

## 2. Model and version

- **Automated screening & finding extraction (`screen.py`, `datadecision.py`, `extract.py`):** `qwen3.8-27b` (RWTHgpt KI:connect, via `rwth-ask` CLI, single-request sequential execution).
- **Pipeline engineering, tests & audit tooling:** Built with Claude (`claude-sonnet-4-6`, `claude-opus-4-6`) and Antigravity (`gemini-3.8-flash`) agents; all numeric/quote checks and workbook generation run deterministically in standard-library Python.

## 3. How papers were found

Draft PubMed queries (`queries.json`, `search.py`) sized all 5 hypotheses (`H5`: 71 hits; `H1`: 47; `H2`: 33; `H3`: 227; `H4`: 108 on 18 Nov 2026). For `H1` vs `H5` (`datadecision.py`), an initial pool of 40 papers per hypothesis (PubMed hits + Europe PMC reference/citation snowballing from anchor PMIDs) was screened against `C1` (non-AD, non-aged human brain cells), `C2` (APOE4 vs APOE3), `C3` (measured late-endosome/lysosome function), `C4` (free full text), and `C5` (contrary evidence). `H1` passed `0`; `H5` passed `5` (`C1`–`C4`). Widening `H5` via Europe PMC snowballing (`pool_H5.json`: 40 -> 120 papers, 80 new APOE-matching candidates) yielded 0 additional `C1`–`C4` passes (`n_pass_C1_C4_cap50 = 5`, plus 4 non-lysosomal near misses). The signed `H5` pool keeps those 5 free-full-text passes (`42636814`, `34919811`, `35750033`, `39532095`, `40457456`) plus anchor paper `37777962`.

## 4. How full text was obtained

`fulltext.py` tries free open-access routes strictly in order: (1) PMC OA JATS XML (`efetch`), (2) Europe PMC OA XML, (3) Unpaywall OA HTML/PDF, and (4) direct DOI HTML. Across the 6 signed `H5` papers (`data/fulltext_report.json`), **5/6 (83%)** were obtained as full text via `pmc_oa`, and **1/6 (17%, anchor `37777962`)** remained abstract-only (`full_text_unavailable`, `C4: no`) after exhausting all free routes. Extraction (`extract.py`) scores Results, tables, and figure-legend blocks and reads up to `9,000` characters per paper (`6,000`-char chunks).

## 5. What a human checked

**100% of papers (6/6) and findings (21/21)** were audited by Dr Ahmed Zayed (`A3` physician audit, `docs/PHYSICIAN_AUDIT_H5.md`, signed 26 Nov 2026):
- Fixed `P5.F4` (`39532095`) experimental system from `H4 cells (human iPSC-derived neurons)` to `H4 human neuroblastoma cells`, confirmed exogenous-ApoE lower directness clamping (`class >= 2`, `strength >= 3`), and cleared `[PHYSICIAN REVIEW REQUIRED]` markers.
- Added `P6.F5` (`40457456`) `CONTRADICTING:` autophagic-flux finding verbatim from Results (`Fig. 1C-E`) per Rule B1/C1.
- Replaced 3 lipid-only rows (`P3.F2`–`P3.F4`, `34919811`) with the verbatim lysosomal LAMP2 / lysosomal-activity finding (`Figures 4D-F`) to preserve `Strict C3`.

## 6. Anything else

- **Strict `C3` & contrary evidence:** Non-lysosomal lipidomics/GSEA rows were excluded (`34919811`) and null autophagic-flux evidence was explicitly retained (`40457456` `P6.F5`).
- **Provenance & figure estimates:** `0` `estimated_from_figure` values appear in this text-only extraction pass (all numbers are `printed_in_text`, verified verbatim in `data/verify_sample.md`; missing values carry `not_found_in_source` or `full_text_unavailable`).
- **Licence-safe public freeze:** Cached raw full-text XML/JSON (`out/fulltext/`) is excluded from `data/` to respect per-article publisher licences (`FREEZE.md`); `data/FREEZE.json` SHA-256-pins all frozen artifacts.

---

## Code and prompts

| File | Job |
|---|---|
| `official/` | Organizer template, validator, example, hypotheses, rules (`SOURCES.md` SHA-256) |
| `hypotheses.json`, `parse_hypotheses.py`, `HYPOTHESES.md` | Exact hypothesis statements and signed `H5` ranking |
| `queries.json`, `search.py`, `snowball.py` | PubMed search and Europe PMC citation snowball |
| `screen.py`, `datadecision.py`, `fulltext.py` | Screening, strict `C1`–`C4` selection, and free full-text fetcher |
| `extract.py` | Quote-guarded extraction (`PAPER_CHARS=9000`) and `apply_h5_physician_audit` post-rules |
| `verify_ids.py`, `verify_sample.py`, `scripts/verify.py` | Rule C4 ID check, verbatim number audit, and offline `data/` verifier |
| `to_template.py`, `check_schema.py` | Standard-library 19-column `.xlsx` builder (`Submission` + `Method`) and schema checker |
| `docs/PHYSICIAN_AUDIT_H5.md`, `CLAIMS.md`, `JUDGES.md`, `FREEZE.md`, `SPEC.md` | Audit record, claim-source map, judge rubric, freeze manifest, and spec |

## Run & Verify (offline)

```sh
make test      # 57 offline unit tests (standard library only)
make verify    # offline SHA-256, schema, report, ID, and CLAIMS.md check on data/ (0 FAIL, 0 WARN)
make validate  # official organizer validator in isolated /private/tmp (requires .venv openpyxl)
```
