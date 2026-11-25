# SPEC.md: MecCog APOE4 pilot (Step 1)

Status: SIGNED (25 Nov 2026) on `H5`, `Strict C3`, pool, and figure-estimate policy; January build/submission items open.

## Buyer line
The MecCog group (organizers of the MecCog Challenge, a Hugging Face Space) need, for one APOE4 endosome hypothesis, a short list of papers and the experimental findings in them, each traceable to a location in the paper, so that they can compare groups and check the specifics. (Organizer and shape: `official/README.md`, `official/rules.html`.) There is no commercial buyer and no sponsor product; the sponsor-primitive gate is n/a.

## Judge line
Quote, `official/rules.html:429`: "Accuracy and relevance over volume. A shorter submission containing only relevant material will score better than one padded with general Alzheimer's literature. Do not exclude findings that provide evidence against the hypothesis."
All criteria with evidence: `JUDGES.md`.

## Hours so far
Unrecorded in the repo. `HYPOTHESES.md` states a feasibility target of "~20 h"; `now.md` carries the same ~20 h with a build window of 31 Dec to 14 Jan. No hours log exists.

## Dates (Valencia time)
- Opens: 00:00 UTC 17 Nov 2026 (`official/rules.html:999`).
- Official deadline: "the end of January 15th, 2027, anywhere on Earth" (`official/rules.html:1001`) = Sat 16 Jan 2027 13:00 Valencia.
- **Submit-by line: Wed 13 Jan 2027 13:00 Valencia** (48 h early, ERR-2026-024).
- One live submission per hypothesis, replaceable until the deadline; the team leader submits (`official/rules.html:988-990`).

## Register-day-0 & January checklist (remaining human/January items open)
- [ ] HF account registered for the challenge (Ahmed's click; institutional address `ahmed.zayed@rwth-aachen.de`)
- [ ] Team created, team name recorded: ______
- [ ] Ahmed set as team leader (only the leader can submit)
- [ ] Registration receipt saved to `Hackathons/2026-11-meccog-apoe4/submission/`
- [ ] Rules re-read on the live HF Space page and diffed against `official/` (18 Nov snapshot); verify live rules for any prize terms (challenge products in snapshot: open-source pipeline, scientific paper, co-authorship per `official/rules.html:427`)
- [ ] Method repo URL decided (repo is private; going public only on Ahmed's click after a history and secrets scan)
- [x] Research question (`H5`), `Strict C3`, pool, and `~` / `estimated_from_figure` policy signed by Ahmed (25 Nov 2026)
- [ ] January pass: extraction (with `~` + `estimated_from_figure` enabled), physician `A3` audit (class, strength, relevance; share recorded), `FREEZE.md`, `make validate`, and submission by `Wed 13 Jan 2027 13:00 Valencia`
- [ ] AI-use disclosure included in the Method README (the pipeline uses AI models)

## Signed scope & decisions (25 Nov 2026)
- **Step 1 only:** find papers, extract experimental findings.
- **Signed Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Signed `Strict C3`:** Measured late-endosome/lysosome readout only (do NOT widen to general lipid handling or pad per `official/rules.html:429,529-534`).
- **Signed pool (cap 50):** Focused strict `C1–C4` pool of 5 free-full-text papers (`34919811`, `35750033`, `40457456` [preserving contrary `C5=yes` finding], `42636814`, plus borderline `39532095` kept with its exact exogenous-ApoE human-neuron experimental system and lower directness class per `official/rules.html:469`) + anchor paper `37777962` (if abstract-only/non-OA permitted; note `C4: no`).
- **Signed Rule `C3` figure-estimate policy (`official/rules.html:537-542`):** Approved enabling `~` prefix + `estimated_from_figure` provenance for bar-chart effect sizes and plotted-point sample sizes (never P values) in the January extraction pass.
