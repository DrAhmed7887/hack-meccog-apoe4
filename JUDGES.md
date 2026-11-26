# JUDGES.md: assessment criteria and status (27 Nov 2026)

Criteria summarize `official/rules.html` and `official/official-rules.html` (snapshot 2026-11-18). No explicit ranking formula exists (`official/rules.html:960-962`); organizer decisions are final (`official/official-rules.html:314-322`).

## Frozen H5 v3 status (27 Nov 2026)
- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Tiered Pool (19 primary records, cap 50):** 18 peer-reviewed + 1 `PubMed preprint` (`42182449`), ordered as 10 Tier 1 human non-AD cells + 9 Tier 2 APOE-TR/rescue/exogenous models with explicit caveats (`17/19` OA full text [`15 pmc_oa`, `1 unpaywall`, `1 doi_direct`], `2/19` honest `Abstract`-only `unavailable`); `0` reviews, `0` retractions.
- **100% Physician `A3` Audit (`docs/PHYSICIAN_AUDIT_H5.md`):** 67 findings (`53 supports`, `14 CONTRADICTING:`), 0 unresolved `[PHYSICIAN REVIEW REQUIRED]` flags, `Method` sheet uses `Who did the work: collab`.

## Assessment criteria (`official/rules.html:963-981,429,527-548`)

| ID | Criterion | Our evidence / status |
|---|---|---|
| A1 | Cross-evaluation by participants | Public repo + six-section `README.md` (`collab` model versions documented). |
| A2 | Cross-group paper & experiment comparison | Frozen 19-paper `H5` workbook (`67` findings in `data/dry_run.xlsx`); `--strict` validator PASS (`0` errors, `0` warnings). |
| A3 | Finding relevance via directness criteria | 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`); exogenous ApoE clamped (`class >= 2`, `strength >= 3`). |
| A4 | Specifics vs source paper | `verify_sample.py`: `14/14` sampled numeric findings (`20/20` fields) verbatim (`data/verify_sample.md`). |
| A5 | Manual inspection where necessary | Verified OA figures (`PMC8758949`, `PMC13260029`, `PMC12041514`); stopped on Turnstile (`37777962`). |
| B1 / C1 | Relevance over volume; cap 50; contrary | `19` papers (`<= 50`); **14 `CONTRADICTING:`** findings preserved; non-endolysosomal candidates excluded. |
| C2 | No fabrication; panel-level location | Single-block verbatim quote guard (`67/67`); `58/63` full-text (`58/67` overall) panel/table IDs (`extract.py`). |
| C3 | Provenance & no estimated P values | `62` populated cells (`46` effect, `12` P, `4` sample) are 100% `printed_in_text`; `0` estimated P values. |
| C4 | Real DOIs and PubMed IDs | `19/19` verified live against PubMed, Europe PMC `core`, and `doi-check --json` (`data/id_verification.json`). |
| C5 | Step 1 only | `.xlsx` and `extracted.json` contain strictly Step 1 papers & findings (`RULE_C5_LEAK = 0`). |

## Remaining human items before upload
- Final release workbook generation (`Team`, real email, final `origin/main` `Commit SHA` in local gitignored `out/release_method.json`) and HF Space upload by `Wed 13 Jan 2027 13:00 Valencia` (`Sat 16 Jan 2027` deadline).
