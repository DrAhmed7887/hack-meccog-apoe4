# SPEC.md: MecCog APOE4 pilot (Step 1)

Status: **FROZEN H5 v3 & H2 v1 (`27 Nov 2026`)** — Flagship `H5 v3` (`19` primary records, `67` findings, `14` contradicting) and Secondary `H2 v1` (`11` primary records, `53` findings, `15` contradicting) both audited (`docs/PHYSICIAN_AUDIT_H5.md`, `docs/PHYSICIAN_AUDIT_H2.md`), hashed in `data/FREEZE.json` (17 files), and `--strict` validated (`0` errors, `0` warnings).

## Buyer line
The MecCog group (organizers of the MecCog Challenge, a Hugging Face Space) need, for each APOE4 hypothesis, a curated list of verified papers and their primary experimental findings, each traceable to a panel/block location and stat provenance in the paper (`official/README.md`, `official/rules.html`).

## Judge line
Quote, `official/rules.html:429`: "Accuracy and relevance over volume. A shorter submission containing only relevant material will score better than one padded with general Alzheimer's literature. Do not exclude findings that provide evidence against the hypothesis." Full rubric: `JUDGES.md`.

## Dates (Valencia time)
- Opens: 00:00 UTC 17 Nov 2026 (`official/rules.html:999`).
- Official deadline: `end of January 15th, 2027, anywhere on Earth` (`official/rules.html:1001`) = Sat 16 Jan 2027 13:00 Valencia.
- **Submit-by target: Wed 13 Jan 2027 13:00 Valencia** (48 h early).

## Checklist
- [x] HF account & Team `Khepri` registered (`DrZayed` leader)
- [x] Public repo with GitHub CI (`ci/test-verify-validate`), branch protection on `main`, and two-channel 6-gate PR review (`scripts/pr_review_bundle.py`)
- [x] Phase 2 pipeline upgrades merged (`PAPER_CHARS=None`, `<app-group>`/`<supplementary-material>` + table splitting, `list_and=True` panel grounding, `N-fold -> Nx`, tiered `C1`, review purge, `collab` Method guards)
- [x] Flagship `H5 v3` & Secondary `H2 v1` extraction, OA figure checks, 100% physician `A3` audits, `FREEZE.md`, `make test && make verify && make validate --strict` PASS
- [x] AI-use disclosure in `README.md` (`Who did the work: collab`)
- [x] Release `.xlsx` workbooks (`H5 v3` & `H2 v1`) built with `--release` and submitted live on `meccog-meccogchallenge.hf.space` as `DrZayed` (Team `Khepri`); post-close organizer survey due after `15 Jan 2027 AoE`

## Signed scope & decisions
- **Step 1 only (`Rule C5`):** `.xlsx` workbooks contain strictly primary papers, verbatim quotes, locations, stat provenance, and directness.
- **Tiered `C1` + `Strict C3` (`official/rules.html:469` & `submission_example.xlsx`):** Tier 1 human non-AD/non-aged cells ordered before Tier 2 models with `Experimental system` caveats (`<= 50` papers). Reviews, retractions, non-readout candidates, and LOAD donor lines (`43026723`) excluded.
- **Rule `C3` stats policy:** All populated stats (`62` H5, `64` H2) are 100% `printed_in_text`, `0` estimated P values, and Turnstile gates (`37777962`) never bypassed.
