# Physician A3 audit sheet for hypothesis H5 (v3 freeze)

**Audit Status: SIGNED & COMPLETE (100% physician `A3` audit across 19 primary research records [18 peer-reviewed + 1 `PubMed preprint`] and 67 findings, 27 Nov 2026).** Every record was verified live for PubMed/Europe PMC IDs (`19/19`), zero retractions (`doi-check`), zero reviews (`pubTypeList` + `is_review_record`), verbatim single-block grounding against cached `out/fulltext/` or `Abstract`, and zero unresolved `[PHYSICIAN REVIEW REQUIRED]` markers.

## Completed review decisions (27 Nov 2026)

1. **Tiered `C1` ordering & model-system caveats (`official/rules.html:469` & `submission_example.xlsx`):**
   - **10 Tier 1 papers (`P1`–`P10`):** Human iPSC-derived non-AD/non-aged brain cells (astrocytes, microglia, neuron-astrocyte cocultures, miBrains) ordered first (`P5` `38480892` scoped strictly to human iPSC microglia, excluding post-mortem AD brain and J20 mouse findings).
   - **9 Tier 2 papers (`P11`–`P19`):** APOE-TR mice, knock-in primary cultures, non-AD human fibroblasts under NPC1/stress challenge, and exogenous ApoE systems ordered after Tier 1 with explicit caveats in `Experimental system` (`P12` `39532095` clamped to `class >= 2`, `strength >= 3`).
2. **Contrary / null evidence (`14 CONTRADICTING:` findings across 11 papers, Rule B1/C1):**
   - Preserved explicit `contradicts` findings across both Tier 1 (`34919811` `Fig 4C` LAMP2 IF & `Fig 4F` `E3 = E4` lysosomal activity, `40457456` `Fig 1C` autophagic flux, `35750033` `Fig 7J` cytokine response, `38480892` autophagic flux) and Tier 2 (`40675218` 18 DIV DQ-BSA & post-cholesterol DQ-BSA, `39532095` total LAMP1 area, `32517777` female Ca2+ null, `39901180` total brain cholesterol unchanged, `40571761` young brain CE reduction, `41338186` lysosomal exocytosis, `40301465` ApoE abundance/transport, `42274838` chloroquine null in E4).
3. **`Strict C3` scope justification & exclusions:**
   - Kept `P5` (`38480892`, iMG subset only) because GNE-317 directly reverses **lysosomal accumulation** (`Fig 7E,F`) and alters **autophagy/LC3B** (`Fig 7D,K-N`), and kept `P10` (`42749735`) because it directly measures **selective autophagy (lipophagy) via SQSTM1/p62** and **LipiDye-M autophagosome-like structures** (`Fig 5I`).
   - Excluded 5 review papers (`42927732`, `42415114`, `41688855`, `42505400`, `41224653`) and 5 candidates lacking APOE4-vs-APOE3 endolysosomal/autophagic readouts or non-tauopathy scope (`33658354`, `39995873`, `41808104`, `33406436`, `41409143`).
4. **Rule `C3` stats discipline & OA visual verification:**
   - Visually inspected OA figures (`PMC8758949` Fig 4E, `PMC13260029` Fig 4D, `PMC12041514` Fig 3/Table 1) to confirm comparisons, and dropped redundant/star-only `visual_only` P-value entries (`34919811` Fig 4E duplicate row removed cleanly alongside `P1.F2`; `42274838` Fig 4D P-value set to `not_found_in_source`), ensuring **62/62** populated stat cells (`46` effect sizes, `12` P values, `4` sample sizes out of `201` total stat cells) are 100% `printed_in_text` with zero estimated P values.
   - `P8` (`37777962`, Gold OA CC BY *Cell Reports*) presented Cloudflare Turnstile on Elsevier ScienceDirect; closed immediately without bypassing (`Abstract` only, `full_text_unavailable`). `P19` (`41785939`, paywalled) similarly kept `Abstract` only, with non-AD fibroblast arm isolated (`sAD` excluded).
5. **Panel-level location & sample verification:** **58/63** full-text findings (**58/67** overall; `5` prose-only full-text + `4` `Abstract`) carry panel/table-level `Data location` (comma/range normalized without unverified middle-panel expansion); `14/14` sampled numeric findings (**20/20** fields) verified verbatim in `data/verify_sample.md`.

## Frozen H5 v3 paper pool (19 papers, 67 findings)

| Paper ID | Tier | PubMed ID | DOI | Source Type | OA Route | Findings (Contra) | Short Title |
|---|---|---|---|---|---|---|---|
| `P1` | `T1` | `34919811` | `10.1016/j.stemcr.2021.11.007` | `PubMed published` | `pmc_oa` | 4 (2 contra) | APOE2, E3, and E4 differentially modulate cellular homeostasis |
| `P2` | `T1` | `40457456` | `10.1186/s12974-025-03470-y` | `PubMed published` | `pmc_oa` | 5 (1 contra) | Inflammation-induced lysosomal dysfunction in human iPSC-derived microglia |
| `P3` | `T1` | `42636814` | `10.1016/j.stem.2026.08.001` | `PubMed published` | `pmc_oa` | 5 (0 contra) | Cholesterol dysregulation in APOE4 astrocytes promotes α-synuclein |
| `P4` | `T1` | `35750033` | `10.1016/j.cell.2022.05.017` | `PubMed published` | `pmc_oa` | 4 (1 contra) | Cholesterol and matrisome pathways dysregulated in astrocytes/microglia |
| `P5` | `T1` | `38480892` | `10.1038/s41586-024-07185-7` | `PubMed published` | `pmc_oa` | 3 (1 contra) | APOE4/4 is linked to damaging lipid droplets in AD microglia (iMG subset) |
| `P6` | `T1` | `42182449` | `10.64898/2026.05.12.724612` | `PubMed preprint` | `pmc_oa` | 3 (0 contra) | Impaired lipoprotein secretion by APOE4 leads to lysosomal/mito defects |
| `P7` | `T1` | `29861287` | `10.1016/j.neuron.2018.05.008` | `PubMed published` | `pmc_oa` | 2 (0 contra) | APOE4 Causes Widespread Molecular and Cellular Alterations (`#AG09173`) |
| `P8` | `T1` | `37777962` | `10.1016/j.celrep.2023.113183` | `PubMed published` | `unavailable` | 2 (0 contra) | ApoE4-dependent lysosomal cholesterol accumulation impairs mitophagy |
| `P9` | `T1` | `41867897` | `10.1093/pnasnexus/pgag053` | `PubMed published` | `pmc_oa` | 2 (0 contra) | APOE3 astrocytes rescue lipid abnormalities and dystrophic neurites |
| `P10` | `T1` | `42749735` | `10.1038/s41467-026-76565-6` | `PubMed published` | `pmc_oa` | 2 (0 contra) | APOE genotypes differentially remodel astrocytic LD proteome & lipophagy |
| `P11` | `T2` | `40675218` | `10.1016/j.jbc.2025.110479` | `PubMed published` | `pmc_oa` | 6 (2 contra) | Neuronal endolysosomal alterations induced by ApoE4 emerge with age |
| `P12` | `T2` | `39532095` | `10.1016/j.cell.2024.10.027` | `PubMed published` | `pmc_oa` | 5 (1 contra) | Decreased lipidated ApoE-receptor interactions confer protection |
| `P13` | `T2` | `32517777` | `10.1186/s13024-020-00382-8` | `PubMed published` | `pmc_oa` | 4 (1 contra) | Sex-dependent calcium hyperactivity due to lysosomal-related dysfunction |
| `P14` | `T2` | `39901180` | `10.1186/s13024-025-00802-7` | `PubMed published` | `pmc_oa` | 4 (1 contra) | Cellular senescence induced by cholesterol accumulation via lysosomal ABCA1/mTORC1 |
| `P15` | `T2` | `40571761` | `10.1007/s11064-025-04463-2` | `PubMed published` | `doi_direct` | 4 (1 contra) | APOE Genotype Impacts Polyunsaturated Neutral Lipid Storage |
| `P16` | `T2` | `41338186` | `10.1016/j.neuron.2025.10.040` | `PubMed published` | `unpaywall` | 4 (1 contra) | Protective ApoE variants support neuronal function by effluxing lipids |
| `P17` | `T2` | `40301465` | `10.1038/s41598-025-96531-4` | `PubMed published` | `pmc_oa` | 3 (1 contra) | ApoE4 requires lipidation enhancement to resolve lipid/protein phenotypes |
| `P18` | `T2` | `42274838` | `10.1007/s12035-026-05996-5` | `PubMed published` | `pmc_oa` | 3 (1 contra) | APOE4-Expressing Astrocytes Exhibit PD-Related Pathology |
| `P19` | `T2` | `41785939` | `10.1016/j.bbadis.2026.168211` | `PubMed published` | `unavailable` | 2 (0 contra) | Mitochondrial complex-derived ROS induces lysosomal dysfunction |
