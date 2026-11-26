# SPEC.md: MecCog APOE4 pilot (Step 1)

Status: **FROZEN H5 v3 (`27 Nov 2026`)** on `H5`, tiered `C1` + `Strict C3`, 19-paper pool (`10` Tier 1 + `9` Tier 2; `68` findings, `14` contradicting), 100% physician `A3` audit, `data/FREEZE.json` SHA-256 manifest, public repo, team `Khepri` (`DrZayed`), and `--strict` validation PASS; ready for H2 workbook & final release staging.

## Buyer line
The MecCog group (organizers of the MecCog Challenge, a Hugging Face Space) need, for each APOE4 endosome hypothesis, a curated list of verified papers and their primary experimental findings, each traceable to a panel/block location and stat provenance in the paper, so groups can cross-evaluate and check specifics (`official/README.md`, `official/rules.html`). No commercial buyer or sponsor product applies.

## Judge line
Quote, `official/rules.html:429`: "Accuracy and relevance over volume. A shorter submission containing only relevant material will score better than one padded with general Alzheimer's literature. Do not exclude findings that provide evidence against the hypothesis."
Full rubric mapping: `JUDGES.md`.

## Dates (Valencia time)
- Opens: 00:00 UTC 17 Nov 2026 (`official/rules.html:999`).
- Official deadline: "the end of January 15th, 2027, anywhere on Earth" (`official/rules.html:1001`) = Sat 16 Jan 2027 13:00 Valencia.
- **Submit-by target: Wed 13 Jan 2027 13:00 Valencia** (48 h early).
- One live submission per hypothesis, replaceable until the deadline; the team leader submits (`official/rules.html:988-990`).

## Checklist
- [x] HF account & Team `Khepri` registered (`DrZayed` leader)
- [x] Method repo public with GitHub CI (`ci/test-verify-validate`), branch protection on `main`, and two-channel 6-gate PR review (`scripts/pr_review_bundle.py`)
- [x] Pipeline Phase 2 upgrades merged (uncapped `PAPER_CHARS=None`, `<app-group>`/`<supplementary-material>` + table row-chunking, panel-level `Data location` grounding, `N-fold -> Nx`, tiered `C1`, review purge, `collab` Method guards)
- [x] Flagship `H5 v3` extraction, OA visual figure inspections, 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`), `FREEZE.md` (`data/`), `make test && make verify && make validate` PASS (`68/68` unit tests, `19/19` live IDs, `0` retractions)
- [x] AI-use disclosure documented in `README.md` (`Who did the work: collab`)
- [ ] Rules diff vs live HF Space & final release `.xlsx` upload (`~5-10 min HITL`) before `Wed 13 Jan 2027 13:00 Valencia`

## Signed scope & decisions
- **Step 1 only:** `.xlsx` workbooks stop strictly at primary papers, verbatim quotes, locations, stat provenance, and directness (`Rule C5`).
- **Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Tiered `C1` + `Strict C3` (`official/rules.html:469` & `submission_example.xlsx`):** Tier 1 human non-AD/non-aged cells ordered before Tier 2 `APOE-TR`/rescue/exogenous models with `Experimental system` caveats (`<= 50` papers). Non-endolysosomal lipid-droplet/raft-only candidates (`33658354`, `39995873`, `41808104`, `33406436`, `41409143`) and all 5 review articles (`REV=True`) excluded; AD-brain-only excluded (`38480892` scoped strictly to human iMGs).
- **Rule `C3` stat & figure policy:** `62` `printed_in_text`, `2` visually verified `visual_only` (`PMC8758949` Fig 4E, `PMC13260029` Fig 4D), zero estimated P values, and Turnstile gates (`37777962`) never bypassed (`Abstract` only).
