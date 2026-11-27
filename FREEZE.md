# FREEZE.md: what is committed, and what is optional to regenerate

Status: **FROZEN H5 v3 & H2 v1 (27 Nov 2026).**
- **Flagship `H5 v3` (`data/`):** 19 primary records (`18` peer-reviewed + `1` `PubMed preprint` [`42182449`]; **10 Tier 1 + 9 Tier 2**), **67 findings** (`53 supporting, 14 contradicting`), `19/19` live verified (`0` retractions), `14/14` (`20/20` fields) verbatim in `data/verify_sample.md`, audited in `docs/PHYSICIAN_AUDIT_H5.md`.
- **Secondary `H2 v1` (`data/H2/`):** 11 primary `PubMed published` Tier 2 records with explicit caveats, **53 findings** (`38 supporting, 15 contradicting` across 8 papers), `11/11` live verified (`0` retractions), `17/17` (`31/31` fields) verbatim in `data/H2/verify_sample.md`, audited in `docs/PHYSICIAN_AUDIT_H2.md`.
All 17 frozen files across `data/` and `data/H2/` are SHA-256-pinned in `data/FREEZE.json`, and `make verify` passes **0 FAIL, 0 WARN** offline.

## Verify path (needs nothing but Python 3 and this repo)

```sh
make test      # 68 offline unit tests
make verify    # SHA-256, schema, report, ID, and CLAIMS.md checks on data/ and data/H2/
make validate  # official organizer validator --strict
```

## Frozen manifest (`data/FREEZE.json`, 17 files)

| Committed in `data/` | Purpose | Status |
|---|---|---|
| `data/dd/{report.json,pool_H5.json,screen_H5.json,ft_H5.json,widen_run.log}` | Early H1/H5 widening benchmark counts & logs | Frozen |
| `data/{extracted.json,dry_run.xlsx,id_verification.json,fulltext_report.json,verify_sample.md,validator_output.txt}` | Flagship `H5 v3` (`19` papers, `67` findings, `--strict` PASS) | Frozen (v3) |
| `data/H2/{extracted.json,dry_run_H2.xlsx,id_verification.json,fulltext_report.json,verify_sample.md,validator_output.txt}` | Secondary `H2 v1` (`11` papers, `53` findings, `--strict` PASS) | Frozen (v1) |
| **not committed** | `out/fulltext/` (gitignored OA XML/HTML/JSON blocks per publisher licences) & `out/release_method.json` | Excluded |
