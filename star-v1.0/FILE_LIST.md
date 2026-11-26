# File list: Senior Transportation Access Report v1.0 analysis code

Provenance and checksums for every file in this folder.

## Provenance (code was not on Zenodo)

Live Zenodo record https://zenodo.org/api/records/24210261 (DOI 10.5281/zenodo.24210261, Version 1.0, published November 13, 2026; created November 13, 2026, 7:36 PM MT) contains **one** file:

- `senior-transportation-access-report-v1.0.zip` (3,685,847 bytes; md5 46a918921e12a084ae34f80014025ea7; SHA-256 cbca63c6ad89f88f0cafcfb7dd1405ed6b4f8b06b0f6f00e0ae9c6e68268d800)

That zip was downloaded from the public API and the md5 matched. It holds the report PDF, fact-sheet PDFs, methodology, limitations, data dictionary, estimate CSVs, `study_areas.csv`, `standard_population.csv`, chart CSVs, and macOS `.__MACOSX` / `.DS_Store` entries. **It contains no analysis scripts, no requirements file, and no run script.**

The estimate CSVs in the Zenodo zip are byte-identical to those in both local production packages:

- `smr-production-v1.0-content-locked-2026-11-10.zip` (SHA-256 869fdded7dd46363ab7df6efda1448881feadcd42af328d0cfa9cac0a6f4a796)
- `smr-production-v1.0.1-content-locked-2026-11-11.zip` (SHA-256 7d6f769896815c538e665090e49cbb4212795802e168aad54045cd3550c68c41)

Editorial files in the Zenodo zip (methodology, limitations, data dictionary, and the design-team PDFs) differ from both production packages. That does not affect the analysis scripts.

The analysis scripts in this package were copied, byte-for-byte and unedited, from `code/analysis/` in `smr-production-v1.0.1-content-locked-2026-11-11.zip` (SHA-256 7d6f769896815c538e665090e49cbb4212795802e168aad54045cd3550c68c41). They are also byte-identical in:

- the same path in the Version 1.0 production zip (SHA-256 869fdded7dd46363ab7df6efda1448881feadcd42af328d0cfa9cac0a6f4a796)
- the validated analysis package `smr-phase1-validation-package-v1.1-2026-11-10.zip` (SHA-256 45b296ccf1efecf7d76e64960129c67094d910ef1e4d38a5ada9d5c94099751c), which `README-REPRODUCIBILITY.md` names as the source of the copies

Version 1.0.1 is the last content-locked production package before the November 13, 2026 publication. Only publication-generator scripts (not included here) differ between v1.0 and v1.0.1.

The v1.1 validation package also contains `reference/pums_joint.py`. That file is not in `code/analysis/` of the production packages and was **not** copied here.

The added `RUN.md` in this revision includes Dee C's no-decision correction of the combined disk figure to 4,006,747,158 bytes. The analysis scripts in the first commit were unchanged from the deposit-time sources.
Commit 2 applies David's cleanup: the two Phase 2 path comments were removed, and STAR test-file paths were made relative. INTERNAL and UNREVIEWED strings were left unchanged. Hashes below are after that cleanup.

## Files

| Path | Bytes | SHA-256 | Origin |
|---|---:|---|---|
| RUN.md | 7,921 | f1b9d203fd58b41da4e76e185970b40b06ed2e4beb19aafe5e5799fd923b80b6 | added |
| analysis/SHA256SUMS-inputs.txt | 1,483 | 61e49872ea18761c9e0568f6bc2b6010ae3446c72f02ef1f4e180a3de1f41259 | local package (not in the Zenodo deposit) |
| analysis/estimate_joint.py | 10,027 | 3728591a4513a39f0141f2c5579df15695b4ddacbfbebc10ecf796bba4d1e017 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/age_sensitivity.py | 11,473 | 8df310dabe42fca227bbd18d9d3e1886e540938dd9f38a82566e99232234c0a2 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/tests/test_age_sensitivity.py | 2,978 | 94355c19df9ea2653b144a5876070d30ea0d65f0f04c855a9cec0cfa0e94a0c4 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/tests/test_with_without_std.py | 2,181 | 2b545f6c175b1a401eeb5ce8057e8797db99ae1a69a851221090760dcc26a9be | local package (not in the Zenodo deposit) |
| analysis/sensitivity/with_without_std.py | 4,964 | e37819f2de197d6a9f29eb9dc85e8ea05a08b6d1ca56613bf1f607cf2c947f44 | local package (not in the Zenodo deposit) |
| analysis/supplementary_difference.py | 2,422 | ce86475fc728f81c69b7eb0c386ec8e4c091da3555e58e48c3235c30f56d88f6 | local package (not in the Zenodo deposit) |
| analysis/tests/test_estimate_joint.py | 5,178 | fad67651b8b20f2153d6324100865f03fc1e81da66594575c40dffff2f0bbcf6 | local package (not in the Zenodo deposit) |
| analysis/tests/test_v11.py | 5,436 | 1c90907ffb790a411934cee601adda560bb6c8c57aa4beab9213726066abfb72 | local package (not in the Zenodo deposit) |
| analysis/with_without_contrast.py | 3,333 | 6c8ba3b794806c1f231ab831d4e7e4c1867c8f83ca6ddac3b01d7cbbcdb02873 | local package (not in the Zenodo deposit) |
| requirements.txt | 696 | 87a8800f4178033a0ecb2bf4dc012bf6c491cd2f86ebcc830a39fe5ab927b1c1 | added |

## Scan (code only)

Code files present (excluding added RUN.md, requirements.txt, FILE_LIST.md): .py×9, .txt×1
No data files found (no CSV, Parquet, XLSX, zip, or PUMS microdata).
No credential, password, API key, or private-key material found.
No Phase 2 path comments remain, and no hardcoded `/workspace/...` test paths remain.

## Notes for the scan

- Commit 2 removed the two Phase 2 path comments and made STAR test-file paths relative (documented in `RUN.md`). INTERNAL and UNREVIEWED strings, agent names, message ids, and decision quotes were left unchanged.
- Several files still contain leftover “INTERNAL, UNREVIEWED” status strings from the first-phase analysis package.
- No secrets. No Census microdata. No run outputs. No internal spreadsheets.

This file (`FILE_LIST.md`) is added and is included in the repository.
