# make dry-run: top hypothesis, <=20 PubMed hits, full text + extraction on up to 13 included papers, official validator on our own output.
HYP ?= H5
PY ?= python3
VENV_PY ?= $(CURDIR)/.venv/bin/python
VALIDATOR := $(CURDIR)/official/resources/validate_submission.py
SCRATCH ?= /private/tmp

.PHONY: test dry-run validate verify
test:
	$(PY) -W ignore -m unittest discover -s tests

# Offline check of the committed data in data/ (no network, no keys, no rwth-ask). See FREEZE.md.
# Pre-freeze local check on the git-ignored out/: make verify DATA=out
DATA ?= data
verify:
	$(PY) scripts/verify.py --data $(DATA)

dry-run:
	mkdir -p out
	$(PY) search.py --hyp $(HYP) --max 20 --out out/search.json
	$(PY) snowball.py --seed $$($(PY) -c "import json;print(json.load(open('hypotheses.json'))['$(HYP)']['start_pmid'])") --max 20 --out out/snowball.json
	$(PY) screen.py --in out/search.json --out out/screened.json --batch 10
	$(PY) fulltext.py --in out/screened.json --out out/fulltext_report.json --max 13
	$(PY) extract.py --in out/screened.json --max 13 --budget-min 40 --out out/extracted.json
	$(PY) to_template.py --in out/extracted.json --out out/dry_run.xlsx
	$(PY) check_schema.py out/dry_run.xlsx
	$(MAKE) validate

# Official validator: run isolated (-I) from outside its folder, on our own file only. Needs openpyxl (.venv).
validate:
	cd $(SCRATCH) && $(VENV_PY) -I $(VALIDATOR) $(CURDIR)/out/dry_run.xlsx | tee $(CURDIR)/out/validator_output.txt
