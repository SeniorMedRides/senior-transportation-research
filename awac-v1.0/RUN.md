# How to run: Aging Without a Car, Version 1.0

This file is **ADDED**. It is not part of the Zenodo deposit. The analysis scripts themselves were not in the Zenodo record (see `FILE_LIST.md`).

Study: Aging Without a Car, Version 1.0  
DOI: 10.5281/zenodo.24235541 (record 24235541; publication date November 17, 2026)

Python 3.13.5, standard library only (`requirements.txt`). No third-party packages.

## Start-to-finish command

The pipeline script `code/run_all.sh` already existed in run v1.2 (code version awac-run-1.2.0). From this package folder (`awac-v1.0/`, the directory that contains `code/`):

```
code/run_all.sh INPUTS_DIR
```

or:

```
AWAC_INPUTS=INPUTS_DIR code/run_all.sh
```

`INPUTS_DIR` must contain the 16 Census files laid out as in `code/v1_0_analysis/SHA256SUMS-inputs.txt` with the leading `inputs/` stripped (`pums/csv_haz.zip` … `pums/csv_put.zip`, `tract_puma.txt`, `PUMS_Data_Dictionary_2020-2024.csv`, `PUMS_Data_Dictionary_2020-2024.txt`, `2020_2024AccuracyPUMS.pdf`). The run stops if any checksum differs.

Example that builds `INPUTS_DIR` (the last three files are required by `run_all.sh`, unlike the STAR Stage A command):

```
mkdir -p INPUTS_DIR/pums
for s in az ca fl id nv ut; do for t in p h; do
  curl -fsSL -o INPUTS_DIR/pums/csv_$t$s.zip https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/csv_$t$s.zip
done; done
curl -fsSL -o INPUTS_DIR/tract_puma.txt https://www2.census.gov/geo/docs/maps-data/data/rel2020/2020_Census_Tract_to_2020_PUMA.txt
curl -fsSL -o INPUTS_DIR/PUMS_Data_Dictionary_2020-2024.csv https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2020-2024.csv
curl -fsSL -o INPUTS_DIR/PUMS_Data_Dictionary_2020-2024.txt https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2020-2024.txt
curl -fsSL -o INPUTS_DIR/2020_2024AccuracyPUMS.pdf https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2020_2024AccuracyPUMS.pdf
( cd INPUTS_DIR && sed 's#  inputs/#  #' ../code/v1_0_analysis/SHA256SUMS-inputs.txt | sha256sum -c - )
code/run_all.sh INPUTS_DIR
```

`run_all.sh` then: verifies input and bundled-data checksums; reruns the reused Version 1.0 code and compares seven estimate CSVs; runs `awac_estimate.py`, `awac_build_docs.py`, `check_consistency_awac.py` and `test_checker_planted_errors.py`; and, if earlier run folders are present, `compare_outputs.py`. Optional: `AWAC_RUN_V1` and `AWAC_RUN_V1_1` (defaults `../run-v1` and `../run-v1.1`). Those earlier runs are not in this package; without them the comparison step is skipped.

`code/v1_0_publication/` is a copy of Version 1.0.1 publication-consistency code. It is included because it stood in `code/` at the time of the run. It is **not** called by `run_all.sh`.

## Excluded-but-required inputs (not in this package)

`run_all.sh` and `awac_estimate.py` also require a Version 1.0.1 data folder at `v1_0_1_data/` beside `code/` (or another path passed as `--v10-data`). That folder is **data** (reference CSVs, published estimate CSVs, and a data dictionary), so it is excluded from this code-only package. `awac_estimate.py` reads `study_areas.csv` from it for display labels and a PUMA cross-check, and it verifies every file against `SHA256SUMS-v1.0.1-data.txt`.

Required files and SHA-256 (from `run-v1.2/v1_0_1_data/SHA256SUMS-v1.0.1-data.txt`):

| File | SHA-256 |
|---|---|
| DATA_DICTIONARY.md | d5298a1a129672c469d8bc8030ab80fbc465dfeb346ad6cd3e1dd62326940dc4 |
| acs_published_context.csv | 7dd968ec5bcf4e2e9abb7f43b97668f6a5904aac6280bac9aaf8d14932449615 |
| age_specific.csv | 50ada70bf1504f5a839b78f21426e41ca87fbba0361ddcb30816e45fe0b898dc |
| age_standardized.csv | dfb30f3cebc277e0fa5c8d9b086350adb6cb6650b97d5fe0b89e67b5e467bf68 |
| cdc_places_context.csv | d222e0f91392823f49137ab9365a9fd98251062e8bd04a26b29829dc160d3013 |
| comparisons.csv | 0433b38a1c631cab61c55c66f9cada11ebd45eebd7ea07cec24eacdf12271348 |
| headline_figures.csv | 67bcad1bd7fefad496d09f85c125212f38a59183a55c18ac8bb99b572e4dcb0c |
| joint_estimates.csv | f39d3a8f8eff07c5c4042aef2d6bef102adb19a1989adc63fc60e20c900ddf57 |
| part_vs_whole.csv | 2f1c4287077b205a6df0b888a2e9ad7eefe59fae43b32a8331c9d97cb562bbd7 |
| standard_population.csv | 083466ed7f18bf14f39013da5edfbed2dee4dba4a231fbb247d4a86275c00f5f |
| study_areas.csv | a721ab91a941ca8cfb2307ac1d4b3c9fd0e7bb79fb9bd28e45f365155c6e5f87 |
| with_without_by_age.csv | 1cd55a7cf6cb56d17ea018d592a6649f065d3cd430beb37a8bc36026f302f0b4 |
| with_without_contrast.csv | 4df8fbaa55b2249e89c14b9952bb1a1e90263880b78ead5862a824a141b53d7a |
| with_without_std.csv | 485dc8bc9730b57fbe7b70f8c3b22dcfef21d270fc4c6d246a07564b158832d9 |

Most of these CSVs, including `study_areas.csv` and `standard_population.csv`, appear with the same SHA-256 in the STAR Zenodo zip (`senior-transportation-access-report-v1.0.zip`, DOI 10.5281/zenodo.24210261) and in `smr-production-v1.0.1-content-locked-2026-11-11.zip`. **Do not** use the `DATA_DICTIONARY.md` from the STAR Zenodo zip for this check: that file differs (Zenodo SHA-256 07821efd21f2d034c7d949582b2e75bb2a63f54ba5baa23855936b5d12a8c41f). Use the Version 1.0.1 dictionary hashed above, from the production-v1.0.1 package.

Expected layout:

```
awac-v1.0/
  code/            (this package)
  v1_0_1_data/     (excluded; required for run_all.sh and awac_estimate.py)
```

## Census download disk space

Both studies use the same ACS 2020–2024 5-year PUMS files for Arizona, California, Florida, Idaho, Nevada and Utah, plus the 2020 tract-to-PUMA relationship file. Aging Without a Car's `code/run_all.sh` also checksums the PUMS data dictionary (CSV and text) and the PUMS accuracy document.

Sizes below were measured from the frozen local copies at `/workspace/smr-phase1-estimates-v1.1/inputs/`, which match every hash in `SHA256SUMS-inputs.txt`. On November 25, 2026 (America/Denver), live HTTP HEAD requests to the same Census URLs returned identical `Content-Length` values and the same `Last-Modified` timestamps (PUMS, dictionaries and accuracy file: March 5, 2026, 5:10–5:15 AM MT; tract-to-PUMA file: August 18, 2022, 6:54 AM MT).

The analysis scripts read the PUMS CSVs from the zip files in place and do not write unzipped copies. Download disk for the 16 files is therefore **727,887,081 bytes (727.89 MB)**. If the 12 PUMS zips are unzipped, the CSVs and bundled README PDFs add **3,278,860,077 bytes (3.279 GB)** uncompressed. The Version 1.0 reproducibility note's "about 3 GB disk" matches the unzipped PUMS size.

### PUMS zip files (ACS 2020–2024 5-year)

Base URL: `https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/`

| File | State | Record type | Compressed (bytes) | Uncompressed (bytes) | Zip members |
|---|---|---|---:|---:|---|
| csv_haz.zip | Arizona | Housing | 20,981,351 | 93,922,820 | psam_h04.csv, ACS2020_2024_PUMS_README.pdf |
| csv_paz.zip | Arizona | Person | 49,891,543 | 229,333,677 | psam_p04.csv, ACS2020_2024_PUMS_README.pdf |
| csv_hca.zip | California | Housing | 99,081,700 | 441,564,445 | psam_h06.csv, ACS2020_2024_PUMS_README.pdf |
| csv_pca.zip | California | Person | 268,363,882 | 1,223,811,970 | psam_p06.csv, ACS2020_2024_PUMS_README.pdf |
| csv_hfl.zip | Florida | Housing | 62,465,815 | 277,075,308 | psam_h12.csv, ACS2020_2024_PUMS_README.pdf |
| csv_pfl.zip | Florida | Person | 143,820,354 | 644,796,735 | psam_p12.csv, ACS2020_2024_PUMS_README.pdf |
| csv_hid.zip | Idaho | Housing | 5,443,412 | 24,067,920 | psam_h16.csv, ACS2020_2024_PUMS_README.pdf |
| csv_pid.zip | Idaho | Person | 13,192,220 | 61,164,376 | psam_p16.csv, ACS2020_2024_PUMS_README.pdf |
| csv_hnv.zip | Nevada | Housing | 8,839,969 | 37,825,507 | psam_h32.csv, ACS2020_2024_PUMS_README.pdf |
| csv_pnv.zip | Nevada | Person | 21,230,014 | 95,912,546 | psam_p32.csv, ACS2020_2024_PUMS_README.pdf |
| csv_hut.zip | Utah | Housing | 8,448,202 | 37,734,976 | psam_h49.csv, ACS2020_2024_PUMS_README.pdf |
| csv_put.zip | Utah | Person | 23,346,628 | 111,649,797 | psam_p49.csv, ACS2020_2024_PUMS_README.pdf |
| **PUMS total** | | | **725,105,090** | **3,278,860,077** | |

### Other Census files

| File | URL | Size (bytes) |
|---|---|---:|
| tract_puma.txt | https://www2.census.gov/geo/docs/maps-data/data/rel2020/2020_Census_Tract_to_2020_PUMA.txt | 1,709,076 |
| PUMS_Data_Dictionary_2020-2024.csv | https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2020-2024.csv | 330,431 |
| PUMS_Data_Dictionary_2020-2024.txt | https://www2.census.gov/programs-surveys/acs/tech_docs/pums/data_dict/PUMS_Data_Dictionary_2020-2024.txt | 307,894 |
| 2020_2024AccuracyPUMS.pdf | https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2020_2024AccuracyPUMS.pdf | 434,590 |
| **Other total** | | **2,781,991** |

**All 16 downloads: 727,887,081 bytes (727.89 MB).** If PUMS zips are also unzipped and kept: 4,006,747,158 bytes (4.007 GB).

After download, check hashes. If any file differs from `SHA256SUMS-inputs.txt`, stop: Census may have re-issued a file and Version 1.0 results may not reproduce.

