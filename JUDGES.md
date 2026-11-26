# JUDGES.md: assessment criteria and status (26 Nov 2026)

Criteria summarize `official/rules.html` and `official/official-rules.html` (snapshot 2026-11-18). No explicit ranking formula exists (`official/rules.html:960-962`); organizer decisions are final (`official/official-rules.html:314-322`).

## Signed & frozen decisions (26 Nov 2026)
- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Strict `C3` & pool (cap 50):** Measured late-endosome/lysosome readout only; 5 free-full-text `C1–C4` passes (`42636814`, `34919811`, `35750033`, borderline `39532095` with exogenous-ApoE clamping, `40457456`) + anchor `37777962` (`C4: no`, abstract-only).
- **100% `A3` audit & freeze:** Signed `docs/PHYSICIAN_AUDIT_H5.md`; `data/` frozen with SHA-256 manifest (`data/FREEZE.json`); `make verify` passes **0 FAIL, 0 WARN**.

## Assessment criteria (`official/rules.html:963-981,429,527-548`)

| ID | Criterion | Our evidence / status |
|---|---|---|
| A1 | Cross-evaluation by participants | Post-submission; public repo + six-section `README.md` live. |
| A2 | Cross-group paper & experiment comparison | Frozen 6-paper `H5` workbook (`21` findings in `data/dry_run.xlsx`); `make validate` valid (0 errors, 0 warnings). |
| A3 | Finding relevance via directness criteria | 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`): `P5.F4` fixed, `P3` strict-C3 LAMP2 replaced, review flags cleared. |
| A4 | Specifics vs source paper | `verify_sample.py`: `6/6` numeric findings & `6/6` number fields verbatim (`data/verify_sample.md`). |
| A5 | Manual inspection where necessary | Post-submission (`n/a` before upload). |
| B1 / C1 | Relevance over volume; cap 50; contrary evidence | `6` papers (`<= 50`); `P6.F5` (`40457456`) `CONTRADICTING:` autophagic-flux row explicitly included. |
| C2 | No fabrication; panel-level location | Verbatim quote guard per block (`data/extracted.json`); `1` non-verbatim finding rejected. |
| C3 | Estimates `~` + `estimated_from_figure`; never P values | Guards tested (`tests/test_upgrades.py`); `0` visual estimates in text-only pass (`printed_in_text` only). |
| C4 | Real DOIs and PubMed IDs | `verify_ids.py`: `6/6` PMIDs/DOIs verified live against PubMed + Europe PMC (`data/id_verification.json`). |
| C5 | Step 1 only | Pipeline stops at papers and findings by design. |

## Remaining human items before upload
- **HF Space registration & Method team cells:** Team `Khepri` created on `meccog-meccogchallenge.hf.space` (leader `DrZayed`); verify live Space rules and upload workbook before `Wed 13 Jan 2027 13:00 Valencia` (`Sat 16 Jan 2027 13:00 Valencia` official deadline).
