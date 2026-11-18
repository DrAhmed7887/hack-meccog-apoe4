# Hypothesis ranking (MecCog APOE4 pilot, Step 1)

Prepared 2026-11-18. Statements are quoted exactly from the official page (official/hypotheses.html, parsed into hypotheses.json). Criteria: closeness to clinical medicine, size of the literature, measurable effect sizes, feasibility in ~20 h.
PubMed hits come from my draft queries in queries.json (`python3 search.py --hyp Hn --count-only`, 18 Nov 2026): they size the candidate pool, they are not counts of relevant papers. Citations are Europe PMC `citedByCount` of the starting reference (18 Nov 2026). The ranking is my judgement; the clinical call is Ahmed's.

| Rank | H | Title | Draft-query PubMed hits | Starting-ref citations |
|---|---|---|---|---|
| 1 | H5 | Lipid metabolism and late endosome function | 71 | 84 |
| 2 | H1 | Lower endosome pH | 47 | 163 |
| 3 | H2 | Impaired receptor recycling | 33 | 140 |
| 4 | H3 | APOE4 aggregation in the endo-lysosome | 227 | 82 |
| 5 | H4 | APOE4 adhesion to recycling receptors | 108 | 107 |

## Top pick: H5 (his click to confirm)

Runner-up H1. The Makefile defaults to `HYP=H5`; change with `make dry-run HYP=H1`.

## Data decision, 18 Nov (report run 19 Nov 00:37; `python3 datadecision.py report --hyp H1 --hyp H5`, `out/dd/report.json`)

Rule set 18 Nov: the hypothesis with more full-text papers passing every check goes first; within 5 of each other → H5.
Checks: C1 human cell model (AD brain + mouse only = fail), C2 APOE4 vs APOE3 compared, C3 the hypothesis readout actually measured,
C4 free full text (PMC, Europe PMC, Unpaywall, DOI), C5 the text reports a finding that argues against the hypothesis. Each verdict needs a verbatim quote; "unclear" counts as fail.

| | H1 (endosome pH) | H5 (lipid / late endosome) |
|---|---|---|
| Screened | 37 | 40 |
| Pass C1-C3 | 0 | 6 |
| Pass C1-C4 (free full text) | 0 | 5 |
| Pass C1-C5 (every check) | 0 | 1 |
| Papers with a numeric effect (C1-C4) | 0 | 1 |

**Result: H5 goes first** (1 vs 0 on every check; also within 5, so H5 either way). The Makefile default stays `HYP=H5`.
The H5 pool is thin: only 5 papers pass C1-C4. Hand-check of those 5 against the C3 definition (orchestrator, 19 Nov, from the quotes in report.json):
- 34919811 (cholesterol in lysosomes elevated), 35750033 (lysosomal cholesterol sequestration), 40457456 (lysosomal membrane permeabilization stronger in APOE4/4; also C5: autophagic flux blocked in both genotypes), 42636814 (impaired degradation of α-synuclein; 2.25-fold effect quote): C3 holds.
- 39532095: borderline. C3 rests on "lipofuscinosis" and C1 adds exogenous ApoE to human neurons rather than APOE-genotyped cells. Physician review.
No P value or effect size was estimated; only quoted numbers are kept.

### 1. H5: Lipid metabolism and late endosome function

> In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.

Starting reference: Starting reference. Lee H, Cho S, Kim MJ, et al. ApoE4-dependent lysosomal cholesterol accumulation impairs mitochondrial homeostasis and oxidative phosphorylation in human astrocytes. Cell Rep. 2023;42(10):113183. PMID 37777962.

- For: Closest to clinical medicine: cholesterol and lipid handling, lysosomal storage-like phenotype, in human iPSC astrocytes/microglia. Results are printed as percentages, fold changes and P values, so the effect-size columns fill well.
- Against: Largest focused body of work after H3 without H3's noise; scope is wider than H1, so cap at 50 papers and watch the hypothesis boundary (lipid vs lysosome function).

### 2. H1: Lower endosome pH

> In some types of non-Alzheimer's, non-aged human brain cells, for example astrocytes, APOE4 causes reduced endosome pH compared with APOE3.

Starting reference: Starting reference. Prasad H, Rao R. Amyloid clearance defect in ApoE4 astrocytes is reversed by epigenetic correction of endosomal pH. Proc Natl Acad Sci U S A. 2018;115(28):E6640-E6649. PMID 29946028.

- For: Narrowest and cleanest scope, best-cited anchor paper (163 citations), clear human-cell readout (endosomal pH, NHE6).
- Against: pH is reported in pH units, which the effect-size format (%, x, d=, qualitative) fits poorly, so many rows become qualitative or N/A; smallest literature (47 hits).

### 3. H2: Impaired receptor recycling

> In some types of non-Alzheimer's, non-aged human brain cells, for example astrocytes, APOE4 causes impaired ARF6-related recycling of receptors between the cell surface and the endosome, compared with APOE3.

Starting reference: Starting reference. Rawat V, Wang S, Sima J, et al. ApoE4 Alters ABCA1 Membrane Trafficking in Astrocytes. J Neurosci. 2019;39(48):9611-9622. PMID 31641056.

- For: Receptor recycling (ARF6, Rab11, ABCA1, LRP1) links to cholesterol efflux, so it has some clinical meaning; colocalisation percentages are common.
- Against: Cell-biology heavy (trafficking assays, microscopy), small literature (33 hits), the ARF6 wording is specific.

### 4. H3: APOE4 aggregation in the endo-lysosome

> In some types of non-Alzheimer's, non-aged human brain cells, APOE4 undergoes increased aggregation in the endo-lysosome compared with APOE3.

Starting reference: Starting reference. Kaji S, Berghoff SA, Spieth L, et al. Apolipoprotein E aggregation in microglia initiates Alzheimer's disease pathology by seeding beta-amyloidosis. Immunity. 2024;57(11):2651-2668.e12. PMID 39419029.

- For: APOE aggregation sits close to amyloid pathology that a physician knows; a recent anchor paper (Kaji 2024).
- Against: Few papers test aggregation inside the endo-lysosome; my draft query returns 227 hits (not inspected, likely broad), so screening cost may be high.

### 5. H4: APOE4 adhesion to recycling receptors

> In some types of non-Alzheimer's, non-aged human brain cells, APOE4 adheres more tightly to some recycling receptors than APOE3, impeding recycling.

Starting reference: Starting reference. Xian X, Pohlkamp T, Durakoglugil MS, et al. Reversal of ApoE4-induced recycling block as a novel prevention approach for Alzheimer's disease. Elife. 2018;7:e40048. PMID 30375977.

- For: Direct receptor binding (ApoER2, LRP1, SORLA) is a clean molecular question.
- Against: Biochemistry (binding affinity, recycling block) furthest from bedside medicine; likely few human-cell experiments (not checked); 108 draft-query hits; binding data may not fit the allowed effect-size shapes.
