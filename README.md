# hack-meccog-apoe4

**Status (27 Nov 2026, H5 v3 frozen):** Hypothesis `H5` submission built and verified (**19 papers [10 Tier 1 + 9 Tier 2], 68 findings [54 supporting, 14 `CONTRADICTING:`]** in `data/dry_run.xlsx`), **19/19** PMIDs/DOIs verified live (`data/id_verification.json`, 0 retractions, 0 reviews), **15/15** sampled numeric findings (**22/22** fields) verified verbatim (`data/verify_sample.md`), **68** unit tests passing (`make test`), `make verify` (**0 FAIL, 0 WARN**), and **`SUBMISSION VALID — no problems found.`** (`data/validator_output.txt`).

- **Team:** `Khepri` (leader `DrZayed` / Dr Ahmed Zayed on `meccog-meccogchallenge.hf.space`)
- **Hypothesis:** `H5` — *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Freeze date:** 2026-11-27

---

## 1. Who did the work

**Collaborative human-AI workflow** (`Who did the work: collab` in the workbook `Method` sheet) — physician-engineer **Dr Ahmed Zayed** worked alongside specialized AI agents, backed by deterministic Python quote, panel-location, stat-provenance, identifier, and schema guards:
- **Human (`Dr Ahmed Zayed`):** Signed `H5` hypothesis selection, tiered `C1` policy (`official/rules.html:469`), `Strict C3` scope, exogenous-ApoE & Tier 2 caveats, visual star inspections of OA figures (`PMC8758949`, `PMC13260029`, `PMC12041514`), and 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`).
- **AI agents & scripts:** `qwen3.8-27b` (`rwth-ask`) initial pipeline + Antigravity `/swarm` extraction/audit agents (`gemini-4-hydrogen-high`, `gemini-3.8-flash-high`, `gemini-4-neon-high`) + Opus adversarial review (`claude -p --model opus`).

## 2. Model and version

`qwen3.8-27b, gemini-4-hydrogen-high, gemini-3.8-flash-high, gemini-4-neon-high` (automated extraction paired with deterministic Python verification in `extract.py`, `datadecision.py`, `verify_ids.py`, `scripts/verify.py`, `scripts/pr_review_bundle.py`, and `to_template.py`).

## 3. How papers were found

PubMed queries (`queries.json`, `search.py`) plus Europe PMC reference/citation snowballing (`snowball.py`, `pool_H5.json`) screened primary papers against `C1` (Tier 1 human non-AD/non-aged cells ordered first; Tier 2 `APOE-TR`/rescue/exogenous models second with system caveats), `C2` (APOE4 vs APOE3 or rescue comparator), `C3` (measured endolysosomal/lysosomal/autophagic dysfunction readout), `C4` (free full text), and `C5` (contrary/null findings preserved). Reviews (`is_review_record` + Europe PMC `pubTypeList`) and retractions (`doi-check`) were purged (`0` reviews, `0` retractions), and non-endolysosomal near misses (`33658354`, `39995873`, `41808104`, `33406436`, `41409143`) were excluded. The frozen pool retains **19 clean primary papers** (`10` Tier 1 + `9` Tier 2, well within the 50-paper cap).

## 4. How full text was obtained

`fulltext.py` fetches free open-access text in strict order: (1) PMC OA JATS XML (`efetch`), (2) Europe PMC OA XML, (3) Unpaywall OA HTML/PDF (`pdftotext`), and (4) direct DOI HTML. Across the 19 `H5` papers (`data/fulltext_report.json`), **17/19 (89.5%)** resolved to full text (`15` `pmc_oa`, `1` `unpaywall` [`41338186`], `1` `doi_direct` [`40571761`]), while **2/19** remained abstract-only (`full_text_unavailable`, `unavailable` in automated fetch: `37777962` Gold OA CC BY at *Cell Reports* without a PMCID and behind Elsevier Cloudflare Turnstile; `41785939` paywalled). `fulltext.py` parses `<app-group>`, `<supplementary-material>`, and oversized tables without truncation (`PAPER_CHARS=None`, `CHUNK_CHARS=6000`).

## 5. What a human checked

**100% of papers (19/19) and findings (68/68)** were audited by Dr Ahmed Zayed (`docs/PHYSICIAN_AUDIT_H5.md`, `0` unresolved `[PHYSICIAN REVIEW REQUIRED]` markers):
- Audited every directness `class`/`strength` assignment, Tier 2 caveat (`39532095` exogenous ApoE clamped `class >= 2`, `strength >= 3`), AD-brain boundary exclusion (`38480892` scoped strictly to human iPSC microglia), and all **14 `CONTRADICTING:`** findings across both tiers.
- Visually downloaded and inspected OA figure files for visual star checks (`PMC8758949` Fig 4E LAMP2 `**p<0.01`, `PMC13260029` Fig 4D `*p<0.05`, `PMC12041514` Fig 3/Table 1 `****p<0.001`), while stopping immediately at ScienceDirect Cloudflare Turnstile on `37777962` (`Abstract` only).
- Upgraded `Data location` to panel-level IDs across `63/68` findings (incl. `40675218` `Fig 2G-H`/`Fig 4J-K`/`Fig 5M`/`Fig 6J`/`Fig 6M`, `41867897` `Fig 2A-C`/`Fig 4B`, `35750033` `Fig 6H`).

## 6. Anything else

- **Provenance discipline:** `62` stats `printed_in_text`, `2` visually verified `visual_only`, missing values marked `not_found_in_source` or `full_text_unavailable`; zero estimated P values.
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
