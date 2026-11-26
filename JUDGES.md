# JUDGES.md: assessment criteria and status (26 Nov 2026)

Criteria summarize `official/rules.html` and `official/official-rules.html` (snapshot 2026-11-18). No explicit ranking formula exists (`official/rules.html:960-962`); organizer decisions are final (`official/official-rules.html:314-322`).

## Signed decisions (25 Nov 2026)
- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Strict `C3` & signed pool (cap 50):** Measured late-endosome/lysosome readout only; 5 free-full-text `C1–C4` passes (`34919811`, `35750033`, `40457456`, `42636814`, borderline `39532095` with exogenous-ApoE system & lower directness) + anchor `37777962` (`C4: no`, abstract-only).
- **Figure-estimate policy (`official/rules.html:537-542`):** `~` + `estimated_from_figure` enabled for effect/sample sizes (never P values).

## Assessment criteria (`official/rules.html:963-981,429,527-548`)

| ID | Criterion | Our evidence / status |
|---|---|---|
| A1 | Cross-evaluation by participants | Post-submission; depends on public repo and Method README. |
| A2 | Cross-group paper and experiment comparison | Signed 6-paper `H5` pool extracted (`22` findings in `out/dry_run.xlsx`); `make validate` valid (0 errors, 0 warnings). |
| A3 | Finding relevance via evidence directness criteria | `docs/PHYSICIAN_AUDIT_H5.md` generated for Ahmed's 5-min audit; `39532095` exogenous-ApoE flags active. |
| A4 | Specifics vs source paper (effect size, P value, system) | `verify_sample.py`: `7/7` findings & `7/7` number fields verbatim (`out/verify_sample.md`). |
| A5 | Manual inspection where necessary | Post-submission (`n/a` before upload). |
| B1 / C1 | Accuracy/relevance over volume; cap 50; keep contrary findings | `extract.select_papers` + `datadecision.py select` order by relevance, cap `<= 50`, preserve `40457456`; audit `C5=yes` row in `A3`. |
| C2 | No fabrication; location at panel level | Verbatim quote guard per block (`out/extracted.json`); `1` non-verbatim finding rejected. |
| C3 | Estimates marked `~` + `estimated_from_figure`; never P values | Implemented & guarded in `extract.py`, `to_template.py`, `check_schema.py`, `scripts/verify.py`; `0` visual estimates in text pass. |
| C4 | Real DOIs and PubMed IDs | `verify_ids.py`: `6/6` PMIDs/DOIs verified live against PubMed + Europe PMC (`out/id_verification.json`). |
| C5 | Step 1 only (no confidence scores, experiment design, schemas) | Pipeline stops at papers and findings by design. |

## Remaining human / freeze items
- **HF & Method setup:** Institutional HF account (`ahmed.zayed@rwth-aachen.de`), team/leader setup, check live HF Space rules, Method README + secrets scan.
- **Freeze & submit (`Wed 13 Jan 2027 13:00 Valencia`, 48 h before `Sat 16 Jan 2027 13:00 Valencia`):** Complete `docs/PHYSICIAN_AUDIT_H5.md`, execute `FREEZE.md`, run `make test && make verify && make validate`.
