# make dry-run: top hypothesis, <=20 PubMed hits, 5 extractions, official validator on our own output.
HYP ?= H5
PY ?= python3
VENV_PY ?= $(CURDIR)/.venv/bin/python
VALIDATOR := $(CURDIR)/official/resources/validate_submission.py
SCRATCH ?= /private/tmp

.PHONY: test dry-run validate
test:
	$(PY) -W ignore -m unittest discover -s tests

dry-run:
	mkdir -p out
	$(PY) search.py --hyp $(HYP) --max 20 --out out/search.json
	$(PY) snowball.py --seed $$($(PY) -c "import json;print(json.load(open('hypotheses.json'))['$(HYP)']['start_pmid'])") --max 20 --out out/snowball.json
	$(PY) screen.py --in out/search.json --out out/screened.json --batch 10
	$(PY) extract.py --in out/screened.json --max 5 --out out/extracted.json
	$(PY) to_template.py --in out/extracted.json --out out/dry_run.xlsx
	$(PY) check_schema.py out/dry_run.xlsx
	$(MAKE) validate

# Official validator: run isolated (-I) from outside its folder, on our own file only. Needs openpyxl (.venv).
validate:
	cd $(SCRATCH) && $(VENV_PY) -I $(VALIDATOR) $(CURDIR)/out/dry_run.xlsx | tee $(CURDIR)/out/validator_output.txt
