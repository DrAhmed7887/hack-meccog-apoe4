# hack-meccog-apoe4

**Status (27 Nov 2026, H5 v3 & H2 v1 frozen + Companion 3D Workbench & Film):** Flagship **`H5` (`data/dry_run.xlsx`):** **19 primary records (`18` peer-reviewed + `1` `PubMed preprint`, 10 Tier 1 + 9 Tier 2), 67 findings (53 supporting, 14 `CONTRADICTING:`)**. Secondary **`H2` (`data/H2/dry_run_H2.xlsx`):** **11 primary records (Tier 2 model systems with caveats), 53 findings (38 supporting, 15 `CONTRADICTING:`)**. Interactive companion visualizer: [Live 3D Mol* Evidence Workbench & Film](https://drahmed7887.github.io/hack-meccog-apoe4/) (`docs/index.html`). Both workbooks pass live ID checks (`19/19` H5, `11/11` H2; `0` retractions, `0` reviews), verbatim numeric audits (`14/14` H5, `17/17` H2), `74` unit tests (`make test`), `make verify` (**0 FAIL, 0 WARN**), and **`SUBMISSION VALID — no problems found.`** (`--strict`).

- **Team:** `Khepri` (leader `DrZayed` / Dr Ahmed Zayed on `meccog-meccogchallenge.hf.space`)
- **Flagship `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Secondary `H2`:** *In some types of non-Alzheimer's, non-aged human brain cells, for example astrocytes, APOE4 causes impaired ARF6-related recycling of receptors between the cell surface and the endosome, compared with APOE3.*

---

## 1. Who did the work

**Collaborative human-AI workflow** (`Who did the work: collab` in workbook `Method` sheets) — physician-engineer **Dr Ahmed Zayed** worked with multi-agent AI extraction and review pipelines, backed by deterministic Python quote, panel-location, stat-provenance, identifier, and schema guards:
- **Human (`Dr Ahmed Zayed`):** Signed `H5`/`H2` selections, tiered `C1` policy (`official/rules.html:469`), `Strict C3` rules, AD/aged exclusions (`43026723` LOAD donor), OA figure visual checks (`PMC8758949`, `PMC13260029`, `PMC12041514`, `PMC10894586`), and 100% physician `A3` audits (`docs/PHYSICIAN_AUDIT_H5.md`, `docs/PHYSICIAN_AUDIT_H2.md`).
- **AI agents & scripts:** Multi-agent extraction and independent adversarial verification (`qwen3.8-27b`, `gemini-4-hydrogen-high`, `gemini-3.8-flash-high`, `gemini-4-neon-high`, plus adversarial review using `claude-opus-5-5`).

## 2. Model and version

`qwen3.8-27b, gemini-4-hydrogen-high, gemini-3.8-flash-high, gemini-4-neon-high` (automated extraction paired with deterministic Python verification in `extract.py`, `datadecision.py`, `verify_ids.py`, `scripts/verify.py`, `scripts/pr_review_bundle.py`, and `to_template.py`).

## 3. How papers were found

PubMed queries (`queries.json`, `search.py`) plus Europe PMC citation/reference snowballing (`snowball.py`, `pool_H5.json`, `31641056`/`19326444` H2 snowballing) screened records against `C1` (Tier 1 human non-AD/non-aged cells first; Tier 2 animal/rescue/exogenous models second with system caveats), `C2` (APOE4 vs APOE3 or rescue), `C3` (measured endolysosomal/autophagic function for H5; receptor recycling/surface trafficking for H2), `C4` (open-access full text where un-gated; paywalled/Turnstile-gated papers retained strictly as honest `Abstract`-only `full_text_unavailable`), and `C5` (contrary/null findings preserved). Reviews (`pubTypeList`) and retractions (`doi-check`) were purged (`0` reviews, `0` retractions).

## 4. How full text was obtained

`fulltext.py` tries free OA routes in strict order: (1) PMC OA JATS XML, (2) Europe PMC OA XML, (3) Unpaywall OA HTML/PDF (`pdftotext`), and (4) direct DOI HTML, parsing `<app-group>`, `<supplementary-material>`, and split tables without truncation (`PAPER_CHARS=None`). **H5 (`data/fulltext_report.json`):** `17/19` full text (`15` `pmc_oa`, `1` `unpaywall`, `1` `doi_direct`), `2/19` honest `unavailable` (`37777962` Turnstile-gated, `41785939` paywalled). **H2 (`data/H2/fulltext_report.json`):** `9/11` full text (`5` `pmc_oa`, `4` `unpaywall`), `2/11` honest `unavailable` (`31796678`, `35235798`).

## 5. What a human checked

**100% of papers and findings (19 papers / 67 findings in `H5`; 11 papers / 53 findings in `H2`)** were physician-audited (`0` unresolved `[PHYSICIAN REVIEW REQUIRED]` markers):
- Enforced `Strict C3`, Tier 2 caveats (`39532095` clamped), non-AD/non-aged `C1` rules (`38480892` iMG-only; excluded `43026723` 87yo LOAD), and preserved all contrary evidence (**14** H5 across 12 papers; **15** H2 across 8 papers, plus NHE6 astrocyte-vs-neuron directionality).
- Visually verified `PMC10894586` (`38217595`) Fig 4 (`Panel A,B`) and Fig 10 (`Panel A`) directly on OA graphics (`58/63` H5 full-text and `50/50` H2 full-text findings carry panel/table `Data location`).

## 6. Anything else

- **Provenance & Rule C5 boundary:** Populated stats (`62/201` H5 cells; `64/159` H2 cells) are **100% `printed_in_text`** with `0` estimated P values. Step 1 workbooks contain strictly primary literature findings (`Rule C5`); companion 3D PDB / AlphaFold DB v6 models (`docs/structures/`, compiled via `scripts/stage_structures.py` & `scripts/build_explorer_data.py`) and documentary film (*"The APOE4 Endosome Bottleneck"*, `video/`) provide structural context only. Raw full texts (`out/fulltext/`) stay gitignored (`data/FREEZE.json` pins 17 frozen files).

```sh
make test                                  # 74 offline unit tests
make verify                                # offline SHA-256, schema, report, ID, and CLAIMS.md check on data/ and data/H2/ (0 FAIL, 0 WARN)
make validate                              # official organizer validator --strict
python3 scripts/build_explorer_data.py     # recompile docs/data/explorer_data.json from frozen Step 1 outputs
```
