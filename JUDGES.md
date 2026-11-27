# JUDGES.md: assessment criteria and status (27 Nov 2026)

Criteria summarize `official/rules.html` and `official/official-rules.html` (snapshot 2026-11-18). No explicit ranking formula exists (`official/rules.html:960-962`); organizer decisions are final (`official/official-rules.html:314-322`).

## Frozen submissions (`H5 v3` + `H2 v1`, 27 Nov 2026)
- **Flagship `H5 v3` (`data/dry_run.xlsx`):** 19 primary records (`18` peer-reviewed + `1` `PubMed preprint` [`42182449`]; `10` Tier 1 + `9` Tier 2), 67 findings (`53 supports`, `14 CONTRADICTING:`), `17/19` OA full text, `58/63` panel/table full-text locations, `62/201` `printed_in_text` stats (`0` visual/estimated P values).
- **Secondary `H2 v1` (`data/H2/dry_run_H2.xlsx`):** 11 primary `PubMed published` Tier 2 records with explicit caveats, 53 findings (`38 supports`, `15 CONTRADICTING:` across 8 papers), `9/11` OA full text, `50/50` panel/table full-text locations, `64/159` `printed_in_text` stats (`0` visual/estimated P values). Both `Method` sheets use `Who did the work: collab`.

## Assessment criteria (`official/rules.html:963-981,429,527-548`)

| ID | Criterion | Our evidence / status |
|---|---|---|
| A1 | Cross-evaluation by participants | Public repo + six-section `README.md` (`collab` model versions & methods documented). |
| A2 | Cross-group paper & experiment comparison | Two `--strict` valid workbooks (`H5` `19/67`; `H2` `11/53`), `0` errors, `0` warnings. |
| A3 | Finding relevance via directness criteria | 100% physician `A3` audits (`docs/PHYSICIAN_AUDIT_H5.md`, `docs/PHYSICIAN_AUDIT_H2.md`); `0` review flags. |
| A4 | Specifics vs source paper | `verify_sample.py`: `14/14` (`20/20` fields) H5 & `17/17` (`31/31` fields) H2 verbatim (`verify_sample.md`). |
| A5 | Manual inspection where necessary | Verified OA figures (`PMC8758949`, `PMC13260029`, `PMC12041514`, `PMC10894586` Fig 4/10); Turnstile never bypassed. |
| B1 / C1 | Relevance over volume; cap 50; contrary | `19 <= 50` (H5), `11 <= 50` (H2); `14` (H5) & `15` (H2) `CONTRADICTING:` rows preserved. |
| C2 | No fabrication; panel-level location | Single-block verbatim quote guards; `58/63` (H5) & `50/50` (H2) panel/table IDs (`extract.py`). |
| C3 | Provenance & no estimated P values | `62` (H5) & `64` (H2) populated stats are 100% `printed_in_text`; `0` estimated P values. |
| C4 | Real DOIs and PubMed IDs | `19/19` (H5) & `11/11` (H2) verified live against PubMed, EPMC `core`, & `doi-check --json` (`0` retractions). |
| C5 | Step 1 only | `.xlsx` and `extracted.json` contain strictly Step 1 papers & findings (`RULE_C5_LEAK = 0`). |

## Remaining human items before upload
- Generate release `.xlsx` files with real team-leader email + final `Commit SHA` in local gitignored `out/release_method.json` and upload on HF Space by `Wed 13 Jan 2027 13:00 Valencia` (`Sat 16 Jan 2027` deadline).
