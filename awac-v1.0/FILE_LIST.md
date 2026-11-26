# File list: Aging Without a Car v1.0 analysis code

For Dee C's review before any public repository. This file is **ADDED**.

## Provenance (code was not on Zenodo)

Live Zenodo record https://zenodo.org/api/records/24235541 (DOI 10.5281/zenodo.24235541, Version 1.0, publication date November 17, 2026; record created November 14, 2026, 10:07 PM MT) contains **30 files**: report and fact-sheet PDFs, table CSVs, sensitivity CSVs, `study_areas.csv`, `standard_population.csv`, LICENSE.md, DATA_DICTIONARY.md, CITATION.cff, citation.bib, and limitations-and-disclosures.md. **It contains no analysis scripts, no requirements file, and no run script.**

Published table CSVs in the deposit match `data/` in the local publication package `smr-aging-without-a-car-publication-v1.0-final-2026-11-17.zip` (SHA-256 a8ac12676e8fc07c0599c645c0019ea8ccd9a8a19b53b0de20b0c58a4067814f, 98 files). That publication package also has no PUMS analysis scripts (only publication-build scripts, which are not included here). Some Zenodo files differ from the local publication package (design-team PDFs, which are not in the zip; CITATION.cff; citation.bib; DATA_DICTIONARY.md; limitations-and-disclosures.md; and the Excel tables workbook). Those differences do not affect the analysis scripts.

The analysis scripts in this package were copied, byte-for-byte and unedited, from `run-v1.2/code/` in `smr-aging-without-a-car-run-v1.2-2026-11-14.zip` (SHA-256 3f073624fe387e8ab6fc29cb31274be882bf8e764dd35b349338f0aa8681c4c0). That is the source run referenced by the publication package (`source-run-v1.2/`). Code version: awac-run-1.2.0. The reused Version 1.0 scripts under `code/v1_0_analysis/` are byte-identical to the STAR analysis scripts (without the unit-test files).

Nothing was taken from `phase2-*` folders, Stage B or quarantine paths, MANIFEST-ADDENDUM files, or Dee C INTERNAL reports. The `validation-package-dee-c/` tree inside the run zip was not copied.

The added files in this revision include Dee C's two no-decision fixes: an optional python-docx note in `requirements.txt`, and the combined disk figure corrected to 4,006,747,158 bytes in `RUN.md`. The analysis scripts in the first commit were unchanged from the deposit-time sources.

Commit 2 applies David's cleanup: the Phase 2 path comment in `code/v1_0_analysis/estimate_joint.py` was removed (the same edit as in the STAR copy). INTERNAL and UNREVIEWED strings were left unchanged. Hashes below are after that cleanup.

Commit 3 adds `inputs/DATA_DICTIONARY.md` and `inputs/SHA256SUMS-v1.0.1-data.txt`, the two Version 1.0.1 data files that were not on a public Zenodo record, plus `inputs/README.md`. They are required data under CC BY-SA 4.0, not code. The analysis scripts are unchanged. Hashes below include these files.

## Files

| Path | Bytes | SHA-256 | Origin |
|---|---:|---|---|
| RUN.md | 11,039 | ed7198762bbf0c8a57143ca8cb1ced56c6152c24ce25d68d7be6b05be4983b1b | added |
| code/awac_build_docs.py | 29,192 | a47e8a385f9d070052f739bd19a1a8ac280daaa7b4936e5f00d8919ab6ef63e8 | local package (not in the Zenodo deposit) |
| code/awac_estimate.py | 49,105 | 7d7eb86cf9d40c03fdd103af686c51124da69151316cd7aac866d59baf895c3b | local package (not in the Zenodo deposit) |
| code/check_consistency_awac.py | 21,186 | 87c6c8fad604c1ac9ae63a5c3ffea38f1955953dbceae00aec57743dc7acabb3 | local package (not in the Zenodo deposit) |
| code/compare_outputs.py | 4,438 | 9bd516579bc59c74f3f585407c9e3d5fd29fdcba5b7cd2928033dc7804b713a4 | local package (not in the Zenodo deposit) |
| code/run_all.sh | 3,056 | b1fb78b9ea88a8669736e26103969e191bc17c3a4d309fe31c1a542aa40c803e | local package (not in the Zenodo deposit) |
| code/test_checker_planted_errors.py | 4,692 | 044b399cd41ba6e94d357144638975285771d232f5fc96e6621d6642abb15d25 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/SHA256SUMS-inputs.txt | 1,483 | 61e49872ea18761c9e0568f6bc2b6010ae3446c72f02ef1f4e180a3de1f41259 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/estimate_joint.py | 10,027 | 3728591a4513a39f0141f2c5579df15695b4ddacbfbebc10ecf796bba4d1e017 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/sensitivity/age_sensitivity.py | 11,473 | 8df310dabe42fca227bbd18d9d3e1886e540938dd9f38a82566e99232234c0a2 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/sensitivity/with_without_std.py | 4,964 | e37819f2de197d6a9f29eb9dc85e8ea05a08b6d1ca56613bf1f607cf2c947f44 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/supplementary_difference.py | 2,422 | ce86475fc728f81c69b7eb0c386ec8e4c091da3555e58e48c3235c30f56d88f6 | local package (not in the Zenodo deposit) |
| code/v1_0_analysis/with_without_contrast.py | 3,333 | 6c8ba3b794806c1f231ab831d4e7e4c1867c8f83ca6ddac3b01d7cbbcdb02873 | local package (not in the Zenodo deposit) |
| code/v1_0_publication/check_consistency.py | 19,996 | 2b350939406503004c29e380fcbfb521c4846d4637987dbdaafe409745696521 | local package (not in the Zenodo deposit) |
| code/v1_0_publication/common.py | 4,501 | 2f0eb74c57229c03ebda7902ef3cfa106df4e44cfe30d3c4f9cc8324121d6f78 | local package (not in the Zenodo deposit) |
| inputs/DATA_DICTIONARY.md | 8,883 | d5298a1a129672c469d8bc8030ab80fbc465dfeb346ad6cd3e1dd62326940dc4 | added (required data, not code) |
| inputs/README.md | 2,397 | 9a43de6e8051574345ec01195fd5e965d2da54cefa695f028ec720f05f4b8ed7 | added |
| inputs/SHA256SUMS-v1.0.1-data.txt | 1,216 | 1b87b2dbb51d0f69bee17854ceaeedb0c13c3c4b16b083dfcf388797ca6a830a | added (required data, not code) |
| requirements.txt | 1,214 | 53bfaf12e6db1e1cfddb3257125b1117571f11688c11bfe2bd870315f173d473 | added |

## Scan (code only)

Code files present (excluding added RUN.md, requirements.txt, FILE_LIST.md, and inputs/): .py×12, .sh×1, .txt×1
No Census microdata, Parquet, XLSX, zip, or run-output CSVs. Commit 3 adds two required data inputs under `inputs/` (DATA_DICTIONARY.md and SHA256SUMS-v1.0.1-data.txt), not code.
No credential, password, API key, or private-key material found.
No Phase 2 path comments remain.

## Notes for the scan

- Commit 2 removed the Phase 2 path comment in `code/v1_0_analysis/estimate_joint.py`. INTERNAL and UNREVIEWED strings, agent names, message ids, and decision quotes were left unchanged.
- Several files still contain leftover “INTERNAL” status strings (including `awac_estimate.py` and the reused Version 1.0 copies). `awac_build_docs.py` writes an INTERNAL TECHNICAL SUMMARY label into its output, and `check_consistency_awac.py` requires that label.
- `code/test_checker_planted_errors.py` refers to a folder name `validation-package-dee-c` only as an ignore pattern when copying a temporary run tree. That folder was not copied into this package.
- No secrets. No Census microdata. No run outputs. No internal spreadsheets. No Phase 2, Stage B, quarantine, or MANIFEST-ADDENDUM files.

This file (`FILE_LIST.md`) is added and is included in the repository.
