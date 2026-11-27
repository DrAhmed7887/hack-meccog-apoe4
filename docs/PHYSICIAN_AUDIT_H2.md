# Physician A3 audit sheet for hypothesis H2 (v1 freeze)

**Audit Status: SIGNED & COMPLETE (100% physician `A3` audit across 11 `PubMed published` papers and 53 findings, 27 Nov 2026).** Every paper passed live PubMed/Europe PMC verification (`11/11`), `0` retractions (`doi-check --json`), `0` reviews (`pubTypeList` + `is_review_record`), single-block verbatim grounding (`50/50` full-text + `3/3` abstract), `--strict` official validation (`0` errors, `0` warnings), and `0` unresolved `[PHYSICIAN REVIEW REQUIRED]` markers.

## Completed review decisions (27 Nov 2026)

1. **Tier 2 model-system scope & caveats (`official/rules.html:469`):**
   - H2 mechanisms (ARF6/Rab11/NHE6 endosomal receptor recycling of ABCA1, ApoER2, LRP1, GluN2B/GluA1/2/3, LDLR) are established predominantly in primary rodent neurons/astrocytes, APOE-TR mice, knock-in brain slices, and cell lines (`11` Tier 2 papers ordered with anchor `31641056` first, each bearing explicit model caveats in `Experimental system`). `P9` (`39532095`) applies exogenous PUFA-CE ApoE directness clamping (`class >= 2`, `strength >= 3`).
2. **Contrary / null / conflicting evidence (`15 CONTRADICTING:` findings across 8 papers, Rule B1/C1):**
   - Preserved `35235798` (`P11`, `Abstract`-only, baseline ABCA1 particle lipidation largely unaffected by APOE isoform), `31641056` (`P1.F2`: total ABCA1 protein/mRNA unchanged), `39532095` (`P9`: BOTH `lipApoE3` and `lipApoE4` equally reduce surface LDLR vs `lipApoE2`, and equal LAMP1 colocalization), `30375977` (`P3`: Lrp1/Ldlr/IR/TfR unchanged by ApoE4, plus `P3` physiological ApoE3 mild impairment & unchanged I/O), `29946028` (`P2`: dextran endocytosis & cytoplasmic pH unchanged; NHE9 fails rescue), `34617884` (`P5`: ApoE3 also mildly reduces ApoER2 vs KO; NHE6 KO reduces ApoE3 Reelin-LTP), `20547867` (`P4`: PPF/basal I/O unchanged), and `39901180` (`P10`: caveolin-1 knockdown lowers ABCA1 efflux despite higher total ABCA1).
   - Explicitly retained the mechanistic divergence between astrocytes (`29946028`: **reduced** NHE6 and hyperacidified endosomes where NHE6 overexpression rescues LRP1) and neurons (`30375977`, `34617884`: NHE6 inhibition/KO restores ApoER2 recycling).
3. **Rule `C1` & `C3` exclusions:**
   - Excluded **`43026723`** (`ApoE4/4` skin fibroblasts/iNs) under Rule `C1` because its APOE4 line (`AG10788`) derives from an **87-year-old LOAD donor** rather than non-AD/non-aged control lines.
   - Excluded **`19326444`** (cholesterol efflux without receptor recycling/ARF6), **`39769453`** (9M/16-20M aging mice ACAT1/inflammation without receptor recycling), **`34068576`** (purely electrostatic computational modeling), **`40701521`** (AD CSF synthetic rHDL uptake in tumor lines), and duplicate preprint **`38798644`** (peer-reviewed `39901180` kept).
4. **Panel-level grounding & stat provenance (`50/50` full-text panels, `0` warnings):**
   - Visually inspected OA `PMC10894586` (`38217595`) Figure 4 (`Panel A` ApoER2 `47.02%`, `Panel B` LRP-1 `51.97%`, `N=3`) and Figure 10 (`Panel A` LRP-1) to assign exact subpanels `Fig 4A,B` and `Fig 10A`. Upgraded `31641056.F4` verbatim quote (`Fig 2A-D`).
   - Across `159` stat cells (`53` findings x 3), all `64` populated cells (`42` effect sizes [`9` numeric + `33` `qualitative`], `9` P values, `13` sample sizes) are 100% `printed_in_text` (`0` visual/estimated P values); `31/31` numeric fields across `17/17` findings verified verbatim in `data/H2/verify_sample.md`.

## Frozen H2 v1 paper pool (11 papers, 53 findings)

| Paper ID | Tier | PubMed ID | DOI | Source Type | OA Route | Findings (Contra) | Short Title |
|---|---|---|---|---|---|---|---|
| `P1` | `T2` | `31641056` | `10.1523/JNEUROSCI.1400-19.2019` | `PubMed published` | `unpaywall` | 5 (1 contra) | ApoE4 Alters ABCA1 Membrane Trafficking in Astrocytes (`start_pmid`) |
| `P2` | `T2` | `29946028` | `10.1073/pnas.1801612115` | `PubMed published` | `unpaywall` | 14 (3 contra) | Amyloid clearance defect in ApoE4 astrocytes reversed by NHE6 |
| `P3` | `T2` | `30375977` | `10.7554/eLife.40048` | `PubMed published` | `pmc_oa` | 9 (3 contra) | Reversal of ApoE4-induced recycling block as prevention approach |
| `P4` | `T2` | `20547867` | `10.1073/pnas.0914984107` | `PubMed published` | `unpaywall` | 7 (1 contra) | ApoE4 reduces glutamate receptor function by impairing recycling |
| `P5` | `T2` | `34617884` | `10.7554/eLife.72034` | `PubMed published` | `pmc_oa` | 6 (3 contra) | NHE6 depletion corrects ApoE4-mediated synaptic impairments |
| `P6` | `T2` | `23132858` | `10.1074/jbc.M112.420224` | `PubMed published` | `unpaywall` | 3 (0 contra) | Differential regulation of Aβ endocytic trafficking by ApoE isoforms |
| `P7` | `T2` | `31796678` | `10.3233/JAD-190914` | `PubMed published` | `unavailable` | 2 (0 contra) | Carnosic Acid Reverses ApoE4 Inhibition on Cell Surface ApoER2 |
| `P8` | `T2` | `38217595` | `10.3233/JAD-230514` | `PubMed published` | `pmc_oa` | 2 (0 contra) | Role of Impaired Receptor Trafficking in Mediating APOE4 Effects |
| `P9` | `T2` | `39532095` | `10.1016/j.cell.2024.10.027` | `PubMed published` | `pmc_oa` | 2 (2 contra) | Decreased lipidated ApoE-receptor interactions confer protection |
| `P10` | `T2` | `39901180` | `10.1186/s13024-025-00802-7` | `PubMed published` | `pmc_oa` | 2 (1 contra) | Cellular senescence via lysosomal ABCA1 trapping vs recycling |
| `P11` | `T2` | `35235798` | `10.1016/j.celrep.2022.110435` | `PubMed published` | `unavailable` | 1 (1 contra) | Isoform- and cell-state-specific lipidation of ApoE in astrocytes |
