# SPEC.md: MecCog APOE4 pilot (Step 1)

Status: FROZEN (`26 Nov 2026`) on `H5`, `Strict C3`, 6-paper pool (21 findings), 100% physician `A3` audit, `data/` SHA-256 manifest, public repo, and `make validate`; HF Space registration/upload pending Ahmed's click.

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

## Checklist
- [ ] HF account registered for the challenge (Ahmed's click; institutional address `ahmed.zayed@rwth-aachen.de`)
- [ ] Team created, team name recorded: ______
- [ ] Ahmed set as team leader (only the leader can submit)
- [ ] Registration receipt saved to `Hackathons/2026-11-meccog-apoe4/submission/`
- [ ] Rules re-read on the live HF Space page and diffed against `official/` (18 Nov snapshot); verify live rules for any prize terms (challenge products in snapshot: open-source pipeline, scientific paper, co-authorship per `official/rules.html:427`)
- [x] Method repo URL decided and made public after history/secrets scan (`https://github.com/DrAhmed7887/hack-meccog-apoe4`)
- [x] Research question (`H5`), `Strict C3`, pool, and `~` / `estimated_from_figure` policy signed by Ahmed (25 Nov 2026)
- [x] Extraction, 100% physician `A3` audit (`docs/PHYSICIAN_AUDIT_H5.md`), `FREEZE.md` (`data/`), `make test && make verify && make validate` completed (26 Nov 2026)
- [x] AI-use disclosure included in `README.md` (`Who did the work: both`; `qwen3.8-27b` + orchestrator agents)
- [ ] Team cells populated in `Method` sheet (if team name chosen) and final workbook uploaded by `Wed 13 Jan 2027 13:00 Valencia`

## Signed scope & decisions (25–26 Nov 2026)
- **Step 1 only:** find papers, extract experimental findings.
- **Signed Hypothesis `H5`:** *In some types of non-Alzheimer's, non-aged human brain cells, APOE4 disruption of lipid metabolism, compared with APOE3, results in impaired late endosome/lysosome function.*
- **Signed `Strict C3`:** Measured late-endosome/lysosome readout only (do NOT widen to general lipid handling or pad per `official/rules.html:429,529-534`).
- **Signed pool (cap 50):** Focused strict `C1–C4` pool of 5 free-full-text papers (`34919811`, `35750033`, `40457456` [preserving contrary `C5=yes` finding], `42636814`, plus borderline `39532095` kept with its exact exogenous-ApoE human-neuron experimental system and lower directness class per `official/rules.html:469`) + anchor paper `37777962` (abstract-only; note `C4: no`).
- **Signed Rule `C3` figure-estimate policy (`official/rules.html:537-542`):** Support for `~` prefix + `estimated_from_figure` provenance implemented and tested (`0` visual figure estimates used in this text-only pass).
