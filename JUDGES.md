# JUDGES.md: how this entry is assessed, and what we have for each criterion

Every criterion below is copied word for word from the organizer snapshot in `official/` (downloaded 2026-11-18, see `official/SOURCES.md`). The live page was not re-checked for this file; the rules say they may change. Evidence status: "not run" means no fresh measurement exists in this pass.

The organizers state there is no ranking formula: "This challenge sets out a set of initial considerations (below), without an explicit ranking formula. These may be modified and added to once the results are analyzed." (`official/rules.html:960-962`)

## A. The five initial assessment steps (`official/rules.html:963-981`, "How You'll Be Evaluated")

| # | Criterion (verbatim) | Source | Our evidence | Status |
|---|---|---|---|---|
| A1 | "Cross-evaluation by participants to find the subset of strongest performing groups (each participant provides subjective scores for the methods and results submitted by ten other participants, with comments, generating ten assessments per group). Necessary only if there are a large number of submissions." | `official/rules.html:965-969` | None possible before submission. Method README and public repo are what other participants will read. | Not applicable to us before submission |
| A2 | "Comparison of results across groups: which papers were included, which experiments were extracted from those papers. This does not imply that findings reported by one or a few groups will be considered incorrect. Rather, it will help identify 'easy' results." | `official/rules.html:970-973` | Paper pool: `out/dd/pool_H5.json` (120 candidates). Final list not chosen: waiting on Ahmed's signed question. | Not run |
| A3 | "Evaluation of each finding's relevance using the evidence directness criteria." | `official/rules.html:974-975` | Class, strength and relevance are model proposals in `extract.py` output. Physician check not done (README "Known gaps"). | Not run |
| A4 | "Checking of each Finding's specifics (effect size, P value, experimental system) against the source paper. (Experience with the Hugging Face collab showed that providing these specifics is hard for current methods)" | `official/rules.html:976-979` | `verify_sample.py` writes `out/verify_sample.md`. The existing file (seed 7) says "Findings with every number found verbatim: 10/10. Number fields found verbatim: 11/11." This checks quotes against the cached source text, not against a human expert. `out/` is git-ignored. | Existing output only; not re-run in this pass |
| A5 | "Where necessary, manual inspection." | `official/rules.html:980` | Not applicable until a submission exists. | n/a |

## B. What matters most (`official/rules.html:429`, key-facts box)

| # | Criterion (verbatim) | Source | Our evidence | Status |
|---|---|---|---|---|
| B1 | "Accuracy and relevance over volume. A shorter submission containing only relevant material will score better than one padded with general Alzheimer's literature. Do not exclude findings that provide evidence against the hypothesis." | `official/rules.html:429` | Strict inclusion rules C1-C4 in `datadecision.py` (written before the run, `HYPOTHESES.md`). Contrary findings counted at submission level, not excluded (`HYPOTHESES.md`, "Correction, 19 Nov"). | Rules written; submission not built |

## C. Ways to score badly (`official/rules.html:527-548`, "Five scenarios of how submissions can score badly")

| # | Criterion (verbatim) | Source | Our evidence | Status |
|---|---|---|---|---|
| C1 | "Padding the sheet. Include only the papers and findings that genuinely bear on a hypothesis. A submission swollen with general Alzheimer's literature scores worse than a short, focused one. This is not a license to drop a finding that argues against the hypothesis: relevance is about the subject, not the direction of the result. One submission carries at most 50 papers, and the validator enforces it, so order them by relevance from the start and keep the ones that earn their place." | `official/rules.html:529-534` | Pool of 5 passes C1-C4 per `HYPOTHESES.md` (widening to 120 candidates left it at 5). Ordering by relevance not done. | Not run |
| C2 | "Fabrication. Every finding must exist in the paper at the location you cite." | `official/rules.html:535-536` | Extractor keeps a number only as a verbatim quote from one source block (README). Sample check A4 above. | Partial (sample only) |
| C3 | "An estimate presented as a reported value. Where it is only available that way, you should estimate an effect size off a bar chart, or count the plotted points to get a sample size. A P value should not be estimated. Any estimate has to be identified by a leading ~ on the value and the provenance code estimated_from_figure. An estimate recorded as though the paper printed it is a fabrication." | `official/rules.html:537-542` | Figure-only values are not captured; `estimated_from_figure` is not implemented (README). No estimate is recorded as printed. | Honest gap; not implemented |
| C4 | "Invented identifiers. DOIs and PubMed IDs must correspond to real, published sources." | `official/rules.html:543-544` | PMIDs come from PubMed search output (`search.py`). No separate identifier audit run. | Not run |
| C5 | "Working ahead. This is Step 1 only. Assessing confidence, designing experiments and building mechanism schemas all come later." | `official/rules.html:545-547` | Pipeline stops at papers and findings. | Consistent by design; not audited |

## D. Assessment principles in the formal rules (`official/official-rules.html:314-322`)

- "This challenge has no ground truth. There is no withheld answer key, because what the literature contains is itself one of the things being measured."
- "The organizers' assessment decisions are final."

## E. Criteria not found in `official/`

- MISSING: any numeric weights, point scale or ranking formula. The rules state there is none.
- MISSING: prize or award terms for Step 1. Not found in `official/`; needs a web check (NLV: cash prizes mean "needs lawyer").
- MISSING: a results-release date. `official/rules.html:428` says assessment "may take some time".

## F. Dated backlog (hours are estimates from `rules/common/now.md`: about 20 h total build, window 31 Dec 2026 to 14 Jan 2027)

| Date | Task | Hours | Blocked on |
|---|---|---|---|
| Before any paper goes to NotebookLM | Sign research question and C3 definition | unrecorded | Ahmed |
| Before 29 Dec | Confirm HF registration, team name, leader | unrecorded | Ahmed (HF sign-in) |
| 31 Dec to 14 Jan | Re-run pipeline on the signed pool; cap at 50, order by relevance | unrecorded | Signed question |
| 31 Dec to 14 Jan | Physician check of class, strength, relevance; record share checked | unrecorded | Ahmed |
| 31 Dec to 14 Jan | Make repo reproducible offline (committed data, `make verify`) | unrecorded | none |
| 31 Dec to 14 Jan | Fresh-clone test with network blocked | unrecorded | none |
| by Tue 12 Jan | Method README written and signed by Ahmed; pre-publish history scan; go public | unrecorded | Ahmed |
| **Wed 13 Jan 2027 13:00 Valencia** | Submit-by line (48 h early, ERR-2026-024); save platform confirmation to `Hackathons/2026-11-meccog-apoe4/submission/` | unrecorded | Ahmed (team leader submits) |
| Sat 16 Jan 2027 13:00 Valencia | Official deadline (end of 15 Jan AoE) | n/a | n/a |
