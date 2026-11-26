# How to run: Senior Transportation Access Report, Version 1.0

This file is **ADDED**. It is not part of the Zenodo deposit. The analysis scripts themselves were not in the Zenodo record (see `FILE_LIST.md`).

Study: Senior Transportation Access Report, Version 1.0  
DOI: 10.5281/zenodo.24210261 (record 24210261; published November 13, 2026)

Python 3.13.5, standard library only (`requirements.txt`). No third-party packages.

## Start-to-finish command

From the `analysis/` directory (the folder that holds `estimate_joint.py` and `SHA256SUMS-inputs.txt`):

```
mkdir -p inputs/pums && for s in az ca fl id nv ut; do for t in p h; do curl -fsSL -o inputs/pums/csv_$t$s.zip https://www2.census.gov/programs-surveys/acs/data/pums/2024/5-Year/csv_$t$s.zip; done; done && curl -fsSL -o inputs/tract_puma.txt https://www2.census.gov/geo/docs/maps-data/data/rel2020/2020_Census_Tract_to_2020_PUMA.txt && sha256sum -c SHA256SUMS-inputs.txt --ignore-missing && python3 estimate_joint.py --out outputs && python3 with_without_contrast.py --out outputs --overwrite-bundled && python3 supplementary_difference.py --out outputs --overwrite-bundled && (cd sensitivity && python3 age_sensitivity.py && python3 with_without_std.py)
```

This is the Stage A command from `README-REPRODUCIBILITY.md` in the Version 1.0.1 production package, written as a single command. No `run_all.sh` existed in the analysis folder; none was added.

`--ignore-missing` is in the original command because Stage A downloads only the 12 PUMS zips and `tract_puma.txt`. `SHA256SUMS-inputs.txt` also lists the PUMS data dictionary (CSV and text) and `2020_2024AccuracyPUMS.pdf`. Those three files are not required to run the scripts. URLs and sizes are in the disk-space section below.

The scripts write new files under `analysis/outputs/` and `analysis/sensitivity/outputs/`. They do not need `study_areas.csv` or `standard_population.csv`: area definitions are in `estimate_joint.py`, and the age standards S1 and S2 are computed from the PUMS weights.

## Excluded-but-required or useful inputs (not in this package)

Code-only package: Census files are downloaded by the command above, not shipped. The following reference files were on the Zenodo deposit and in the production packages but are **data**, so they are excluded here. They are **not required** to run Stage A.

| File | Role | SHA-256 (Version 1.0 / 1.0.1, also on the Zenodo zip) |
|---|---|---|
| study_areas.csv | Area labels and 2020 PUMA lists | a721ab91a941ca8cfb2307ac1d4b3c9fd0e7bb79fb9bd28e45f365155c6e5f87 |
| standard_population.csv | Published S1 age-standard shares | 083466ed7f18bf14f39013da5edfbed2dee4dba4a231fbb247d4a86275c00f5f |

Unit tests in `analysis/tests/` and `analysis/sensitivity/tests/` expect the original package `reference/` and `outputs/` folders and contain hardcoded `/workspace/...` paths (see `FILE_LIST.md`). They are not part of the start-to-finish command.

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

