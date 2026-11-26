# File list: Senior Transportation Access Report v1.0 analysis code

For Dee C's review before any public repository. This file is **ADDED**.

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

The added `RUN.md` in this revision includes Dee C's no-decision correction of the combined disk figure to 4,006,747,158 bytes. The analysis scripts are unchanged from the deposit-time sources.

## Files

| Path | Bytes | SHA-256 | Origin |
|---|---:|---|---|
| RUN.md | 6,658 | a862e0b4b8f41bec8bc7db2f6fc4b36b61087f9264ea39d2358930249fe9702c | added |
| analysis/SHA256SUMS-inputs.txt | 1,483 | 61e49872ea18761c9e0568f6bc2b6010ae3446c72f02ef1f4e180a3de1f41259 | local package (not in the Zenodo deposit) |
| analysis/estimate_joint.py | 10,146 | 0d3aebe9dcb6f56cd159c2644d582dfc29fe6a2253ecb516b2f91b95139ff8ce | local package (not in the Zenodo deposit) |
| analysis/sensitivity/age_sensitivity.py | 11,473 | 8df310dabe42fca227bbd18d9d3e1886e540938dd9f38a82566e99232234c0a2 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/tests/test_age_sensitivity.py | 2,978 | 94355c19df9ea2653b144a5876070d30ea0d65f0f04c855a9cec0cfa0e94a0c4 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/tests/test_with_without_std.py | 2,164 | d5c6820ea31972d60f6d412b73820c34e2efd11722e1df87d9ab47f0246ea3f7 | local package (not in the Zenodo deposit) |
| analysis/sensitivity/with_without_std.py | 4,964 | e37819f2de197d6a9f29eb9dc85e8ea05a08b6d1ca56613bf1f607cf2c947f44 | local package (not in the Zenodo deposit) |
| analysis/supplementary_difference.py | 2,422 | ce86475fc728f81c69b7eb0c386ec8e4c091da3555e58e48c3235c30f56d88f6 | local package (not in the Zenodo deposit) |
| analysis/tests/test_estimate_joint.py | 5,238 | 08b545ca3528dc020c4b8c93c5ea2086b071fce53dc15d4280e2a1687138a4f5 | local package (not in the Zenodo deposit) |
| analysis/tests/test_v11.py | 5,414 | deca0588071e4f32ce05d3b8181623a8eb3bf90cc6375dc2bad251e7216e5d33 | local package (not in the Zenodo deposit) |
| analysis/with_without_contrast.py | 3,333 | 6c8ba3b794806c1f231ab831d4e7e4c1867c8f83ca6ddac3b01d7cbbcdb02873 | local package (not in the Zenodo deposit) |
| requirements.txt | 696 | 87a8800f4178033a0ecb2bf4dc012bf6c491cd2f86ebcc830a39fe5ab927b1c1 | added |

## Scan (code only)

Code files present (excluding added RUN.md, requirements.txt, FILE_LIST.md): .py×9, .txt×1
No data files found (no CSV, Parquet, XLSX, zip, or PUMS microdata).
No credential, password, API key, or private-key material found.
Phase 2 references in comments or tests (no Phase 2 files were opened or copied into this package):
  - analysis/estimate_joint.py:6: Same definitions and code logic as /workspace/smr-phase2/pums_joint.py (feasibility run), extended to
  - analysis/tests/test_estimate_joint.py:53: # stored feasibility figures (/workspace/smr-phase2/pums-joint-feasibility.json, copied to reference/)
Other hardcoded /workspace paths:
  - analysis/tests/test_v11.py:3: Reads bundled v1.1 outputs/ and the frozen v1.0 package at /workspace/smr-phase1-estimates/ (read only)."""
  - analysis/tests/test_v11.py:6: V10 = pathlib.Path('/workspace/smr-phase1-estimates')
  - analysis/tests/test_v11.py:53: p = pathlib.Path('/workspace/verify-2026-11-10/independent/out/indep_estimates.csv')
  - analysis/tests/test_estimate_joint.py:2: Run: python3 -m unittest discover -s tests -v   (from /workspace/smr-phase1-estimates)
  - analysis/sensitivity/tests/test_with_without_std.py:3: B = pathlib.Path(__file__).resolve().parents[1]; V10 = pathlib.Path('/workspace/smr-phase1-estimates/sensitivity')

## Notes for the scan

- Scripts were not edited. Several files still contain leftover “INTERNAL, UNREVIEWED” status strings from the first-phase analysis package.
- `analysis/estimate_joint.py` and `analysis/tests/test_estimate_joint.py` mention `/workspace/smr-phase2/pums_joint.py` (and a feasibility JSON path) in comments. Those paths were not opened and no Phase 2 file was copied.
- `analysis/tests/test_v11.py` and `analysis/sensitivity/tests/test_with_without_std.py` hardcode `/workspace/smr-phase1-estimates` and, in one test, `/workspace/verify-2026-11-10/independent/out/indep_estimates.csv`. Those tests are not required for the start-to-finish command.
- No secrets. No Census microdata. No run outputs. No internal spreadsheets.

This file (`FILE_LIST.md`) is added and is included in the zip.
