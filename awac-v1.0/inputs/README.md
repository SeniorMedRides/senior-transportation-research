# Required Version 1.0.1 data inputs

These files are **required data inputs**, not analysis code. They are included so the Aging Without a Car Version 1.0 run can be reproduced from public material.

**License.** Original text is offered under Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0), https://creativecommons.org/licenses/by-sa/4.0/. Adaptations must be shared under the same or a compatible license. Facts, estimates and SHA-256 checksums are not subject to copyright. U.S. Census Bureau source data and other third-party material are not relicensed and remain under their own terms.

| File | Bytes | SHA-256 |
|---|---:|---|
| DATA_DICTIONARY.md | 8,883 | d5298a1a129672c469d8bc8030ab80fbc465dfeb346ad6cd3e1dd62326940dc4 |
| SHA256SUMS-v1.0.1-data.txt | 1,216 | 1b87b2dbb51d0f69bee17854ceaeedb0c13c3c4b16b083dfcf388797ca6a830a |

`DATA_DICTIONARY.md` is the Version 1.0.1 dictionary that `run_all.sh` and `awac_estimate.py` check. It is **not** the `DATA_DICTIONARY.md` on Zenodo records 24210261 or 24235541, which have different hashes. `SHA256SUMS-v1.0.1-data.txt` is the checksum list those scripts use to verify the 14-file Version 1.0.1 data folder.

## How to assemble `v1_0_1_data/`

The analysis scripts are unchanged. They still expect the 14-file folder at `v1_0_1_data/` beside `code/` (or another path passed as `--v10-data`).

1. From `awac-v1.0/`, create that folder and copy the two files from this `inputs/` directory:

```
mkdir -p v1_0_1_data
cp inputs/DATA_DICTIONARY.md inputs/SHA256SUMS-v1.0.1-data.txt v1_0_1_data/
```

2. Download the Senior Transportation Access Report Version 1.0 deposit (DOI 10.5281/zenodo.24210261), file `senior-transportation-access-report-v1.0.zip`. From `senior-transportation-access-report-v1.0/data/` in that zip, copy the 13 CSV files named in the checksum list (every file except `DATA_DICTIONARY.md`) into `v1_0_1_data/`. Those 13 files on that record have the exact SHA-256 values the run checks. `study_areas.csv` and `standard_population.csv` are also on the Aging Without a Car record (DOI 10.5281/zenodo.24235541) with the same hashes.

3. Verify the folder:

```
( cd v1_0_1_data && sha256sum -c SHA256SUMS-v1.0.1-data.txt )
```

Every file should report OK. Then run `code/run_all.sh INPUTS_DIR` as described in `RUN.md`.

Do not substitute a `DATA_DICTIONARY.md` from either public Zenodo record.
