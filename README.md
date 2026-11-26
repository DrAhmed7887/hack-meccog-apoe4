# hack-meccog-apoe4

**Status (27 Nov 2026, H5 v3 frozen):** Hypothesis `H5` submission built and verified (**19 primary research records [18 peer-reviewed + 1 `PubMed preprint`, 10 Tier 1 + 9 Tier 2], 67 findings [53 supporting, 14 `CONTRADICTING:`]** in `data/dry_run.xlsx`), **19/19** PMIDs/DOIs verified live (`data/id_verification.json`, 0 retractions, 0 reviews), **14/14** numeric findings (**20/20** number fields) verified verbatim (`data/verify_sample.md`), **68** unit tests passing (`make test`), `make verify` (**0 FAIL, 0 WARN**), and **`SUBMISSION VALID — no problems found.`** (`data/validator_output.txt`).

- **Team:** `Khepri` (leader `DrZayed` / Dr Ahmed Zayed on `meccog-meccogchallenge.hf.space`)
- **Hypothesis:** `H5` — *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Freeze date:** 2026-11-27

---

## 1. Who did the work

**Collaborative human-AI workflow** (`Who did the work: collab` in the workbook `Method` sheet) — physician-engineer **Dr Ahmed Zayed** worked with multi-agent AI extraction and review pipelines, backed by deterministic Python quote, panel-location, stat-provenance, identifier, and schema guards:
- **Human (`Dr Ahmed Zayed`):** Signed `H5` hypothesis selection, tiered `C1` policy (`official/rules.html:469`), `Strict C3` scope, exogenous-ApoE & Tier 2 caveats, visual verification of OA figures (`PMC8758949`, `PMC13260029`, `PMC12041514`), and 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`).
- **AI agents & scripts:** Multi-agent extraction and independent adversarial verification (`qwen3.8-27b`, `gemini-4-hydrogen-high`, `gemini-3.8-flash-high`, `gemini-4-neon-high`, plus adversarial review using `claude-opus-4-6`).

## 2. Model and version

`qwen3.8-27b, gemini-4-hydrogen-high, gemini-3.8-flash-high, gemini-4-neon-high` (automated extraction paired with deterministic Python verification in `extract.py`, `datadecision.py`, `verify_ids.py`, `scripts/verify.py`, `scripts/pr_review_bundle.py`, and `to_template.py`).

## 3. How papers were found

PubMed queries (`queries.json`, `search.py`) plus Europe PMC reference/citation snowballing (`snowball.py`, `pool_H5.json`) screened primary research records against `C1` (Tier 1 human non-AD/non-aged cells ordered first; Tier 2 `APOE-TR`/rescue/exogenous models second with system caveats), `C2` (APOE4 vs APOE3 or rescue comparator), `C3` (measured endolysosomal, lysosomal, or selective autophagic dysfunction readout), `C4` (open-access full text where un-gated; 2 paywalled/Turnstile-gated papers retained strictly as honest `Abstract`-only `full_text_unavailable`), and `C5` (contrary/null findings preserved). Reviews (`is_review_record` + Europe PMC `pubTypeList`) and retractions (`doi-check`) were purged (`0` reviews, `0` retractions), and non-endolysosomal candidates (`33658354`, `39995873`, `41808104`, `33406436`, `41409143`) were excluded. The frozen pool retains **19 primary records** (`18` peer-reviewed + `1` BioRxiv/PubMed preprint `42182449`; `10` Tier 1 + `9` Tier 2, well within the 50-paper cap).

## 4. How full text was obtained

`fulltext.py` fetches free open-access text in strict order: (1) PMC OA JATS XML (`efetch`), (2) Europe PMC OA XML, (3) Unpaywall OA HTML/PDF (`pdftotext`), and (4) direct DOI HTML. Across the 19 `H5` records (`data/fulltext_report.json`), **17/19 (89.5%)** resolved to full text (`15` `pmc_oa`, `1` `unpaywall` [`41338186`], `1` `doi_direct` [`40571761`]), while **2/19** remained abstract-only (`full_text_unavailable`: `37777962` Gold OA CC BY at *Cell Reports* without a PMCID and behind Elsevier Cloudflare Turnstile; `41785939` paywalled). `fulltext.py` parses `<app-group>`, `<supplementary-material>`, and oversized tables without truncation (`PAPER_CHARS=None`, `CHUNK_CHARS=6000`).

## 5. What a human checked

**100% of papers (19/19) and findings (67/67)** were audited by Dr Ahmed Zayed (`docs/PHYSICIAN_AUDIT_H5.md`, `0` unresolved `[PHYSICIAN REVIEW REQUIRED]` markers):
- Audited every directness `class`/`strength` assignment, Tier 2 caveat (`39532095` exogenous ApoE clamped `class >= 2`, `strength >= 3`), AD-brain boundary exclusion (`38480892` scoped strictly to human iPSC microglia), `Strict C3` selective-autophagy/lysosomal boundaries (`42749735` lipophagy/p62, `38480892` lysosomal accumulation & LC3B), and all **14 `CONTRADICTING:`** findings.
- Stopped immediately at ScienceDirect Cloudflare Turnstile on `37777962` (`Abstract` only), cross-checked OA figure images (`PMC8758949`, `PMC13260029`, `PMC12041514`), and removed redundant `visual_only` P values so 100% of populated stats are strictly printed text/table values (`40301465` Table 1 `****p < 0.001`).
- Upgraded `Data location` to panel/table-level IDs across **58/63** full-text findings (`5` prose-only + `4` `Abstract`; `58/67` overall).

## 6. Anything else

- **Provenance discipline:** Across `201` stat cells (`67` findings x 3 fields), `62` non-empty stats (`46` effect sizes, `12` P values, `4` sample sizes) are 100% `printed_in_text`, `0` estimated P values, and `139` missing cells are `not_found_in_source` or `full_text_unavailable`.
- **Step 1 boundary (Rule C5) & licence safety:** Workbooks contain strictly Step 1 papers, quotes, locations, stats, and directness; cached raw full texts (`out/fulltext/`) stay gitignored (`data/FREEZE.json` SHA-256-pins frozen artifacts).

---

## Code & Verification

| File | Job |
|---|---|
| `official/` | Organizer template, `--strict` validator, example, hypotheses, rules (`SOURCES.md`) |
| `search.py`, `snowball.py`, `datadecision.py` | PubMed search, EPMC snowball, tiered `C1–C5` screening & review purge |
| `fulltext.py`, `extract.py` | Uncapped JATS/supp/table OA parser (`PAPER_CHARS=None`) & quote/panel/stat guards |
| `verify_ids.py`, `verify_sample.py`, `scripts/verify.py`, `scripts/pr_review_bundle.py` | Rule C4 ID check, verbatim sample audit, offline `data/` check & PR gate |
| `to_template.py`, `check_schema.py` | 19-column `.xlsx` builder (`Submission` + `Method`) & schema checker |
| `docs/PHYSICIAN_AUDIT_H5.md`, `CLAIMS.md`, `JUDGES.md`, `FREEZE.md`, `SPEC.md` | Physician audit record, claim map, rubric, freeze manifest & spec |

```sh
make test      # 68 offline unit tests
make verify    # offline SHA-256, schema, report, ID, and CLAIMS.md check on data/ (0 FAIL, 0 WARN)
make validate  # official organizer validator in isolated /private/tmp (--strict)
```
