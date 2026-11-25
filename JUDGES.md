# JUDGES.md: assessment criteria and signed status (25 Nov 2026)

Criteria below summarize `official/rules.html` and `official/official-rules.html` (snapshot 2026-11-18; live page not re-checked). No explicit ranking formula exists (`official/rules.html:960-962`); organizer decisions are final (`official/official-rules.html:314-322`).

## Signed decisions (25 Nov 2026)
- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Strict `C3`:** Measured late-endosome/lysosome readout only; do not widen to general lipid handling or pad (`official/rules.html:429,529-534`).
- **Signed pool (cap 50):** 5 free-full-text `C1–C4` passes (`34919811`, `35750033`, `40457456` [preserving contrary `C5=yes`], `42636814`, plus borderline `39532095` kept with its exogenous-ApoE human-neuron system and lower directness class per `official/rules.html:469`) + anchor `37777962` (if abstract-only/non-OA permitted; `C4: no`).
- **Figure-estimate policy (`official/rules.html:537-542`):** Approved enabling `~` + `estimated_from_figure` for bar-chart effect sizes and plotted-point sample sizes (never P values) in January extraction.

## Assessment criteria (`official/rules.html:963-981,429,527-548`)

| ID | Criterion | Our evidence / status |
|---|---|---|
| A1 | Cross-evaluation by participants (10 peer reviews if many entries) | Post-submission; depends on public repo and Method README. |
| A2 | Cross-group paper and experiment comparison | Signed `H5` pool above (from 120-paper `pool_H5.json`); January run pending. |
| A3 | Finding relevance via evidence directness criteria | Model proposals only; physician `A3` audit scheduled for January. |
| A4 | Specifics vs source paper (effect size, P value, system) | Dry-run `verify_sample.py` (seed 7): 10/10 findings, 11/11 numbers verbatim; re-run in January. |
| A5 | Manual inspection where necessary | Post-submission (`n/a` before upload). |
| B1 / C1 | Accuracy/relevance over volume; cap 50; keep contrary findings | Strict `C3`; `40457456` (`C5=yes`) preserved; order by relevance in January. |
| C2 | No fabrication; location at panel level | Verbatim quote guard per block; full run + `A3` audit in January. |
| C3 | Estimates marked `~` + `estimated_from_figure`; never P values | Currently unimplemented (`not_found_in_source`); approved for January pass. |
| C4 | Real DOIs and PubMed IDs | PMIDs from `search.py` (PubMed); identifier audit in January. |
| C5 | Step 1 only (no confidence scores, experiment design, schemas) | Pipeline stops at papers and findings by design. |

## Products, unknowns, and remaining January items
- **Challenge products (`official/rules.html:427`):** Open-source pipeline, scientific paper, and co-authorship; verify live HF Space rules for any prize terms (and results-release timeline).
- **Human / HF setup:** Register institutional HF account (`ahmed.zayed@rwth-aachen.de`), create team + set Ahmed as leader, check live rules on HF Space.
- **January build & submit (`Wed 13 Jan 2027 13:00 Valencia`, 48 h before `Sat 16 Jan 2027 13:00 Valencia`):** Run extraction (`~` + `estimated_from_figure`), physician `A3` audit, `FREEZE.md`, `make validate`, Method README + secrets scan.
