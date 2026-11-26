# SeniorMedRides.com research code: older adults and vehicle access

Open-source code behind the SeniorMedRides.com research series on older adults (65+) and household vehicle access in eight U.S. study areas: Boise, Las Vegas, Orlando, Phoenix, Sacramento, Salt Lake City, Stockton and Tampa. All studies use the U.S. Census Bureau's American Community Survey (ACS) 2020–2024 5-year Public Use Microdata Sample (PUMS).

The studies are published by [SeniorMedRides.com](https://seniormedrides.com/research/) and Point Beyond Publishing, LLC. Read the reports, area summaries and methods at **[seniormedrides.com/research](https://seniormedrides.com/research/)**.

## Studies

| Study | What it measures | Report DOI | Folder |
| --- | --- | --- | --- |
| Senior Transportation Access Report, Version 1.0 | How often serious walking difficulty and having no household vehicle occur together among adults 65+ | [10.5281/zenodo.24210261](https://doi.org/10.5281/zenodo.24210261) | [`star-v1.0/`](star-v1.0/) |
| Aging Without a Car, Version 1.0 | Older adults living alone in a household with no vehicle | [10.5281/zenodo.24235541](https://doi.org/10.5281/zenodo.24235541) | [`awac-v1.0/`](awac-v1.0/) |

Each folder holds the analysis code that produced that study's published estimates. Each folder's `RUN.md` gives the full start-to-finish command, and its `FILE_LIST.md` gives the provenance and SHA-256 of every file.

## What the code does

- Downloads ACS 2020–2024 5-year person and housing PUMS files for Arizona, California, Florida, Idaho, Nevada and Utah, plus the 2020 tract-to-PUMA relationship file, and checks every download against a published SHA-256 list.
- Builds the analysis universe: people 65 and older in housing units.
- Computes weighted estimates with replicate-weight margins of error (successive difference replication, 80 replicate weights).
- Age-standardizes rates, runs each study's pre-registered tests and assigns reliability tiers.
- Runs consistency checks on its own output.

Each study followed a pre-registered plan and was independently re-built and verified before publication.

## Requirements

- **Python 3.13.5.** The analysis uses the Python standard library only. See each folder's `requirements.txt` for the one optional package used by a document checker.
- **Disk space:** about 728 MB for the 16 Census downloads. The scripts read the PUMS zip files in place. Unzipping them would take about 3.3 GB more.
- A Unix-like shell with `curl` and `sha256sum` (macOS or Linux; on Windows, use WSL).

## Quick start

```bash
git clone https://github.com/SeniorMedRides/senior-transportation-research.git
cd senior-transportation-research
```

**Senior Transportation Access Report:** from `star-v1.0/analysis/`, run the single command in [`star-v1.0/RUN.md`](star-v1.0/RUN.md). It downloads the Census files, checks their hashes and runs the scripts in order.

**Aging Without a Car:** follow [`awac-v1.0/RUN.md`](awac-v1.0/RUN.md). In short:

1. Download the 16 Census files into an inputs folder (the commands are in `RUN.md`).
2. Build the `v1_0_1_data/` folder beside `code/`. Thirteen of its files come from the public Zenodo records. The other two, `DATA_DICTIONARY.md` and `SHA256SUMS-v1.0.1-data.txt`, are in [`awac-v1.0/inputs/`](awac-v1.0/inputs/) because no public record carries these exact versions. See [`awac-v1.0/inputs/README.md`](awac-v1.0/inputs/README.md).
3. Run `code/run_all.sh INPUTS_DIR`.

If any downloaded file's hash differs from the published list, the run stops. That usually means the Census Bureau has re-issued a file, and Version 1.0 results may not reproduce.

## Reproducing the published figures

A successful run reproduces each study's published estimates. Compare the output with the data files in that study's Zenodo record.

## Notes on the code

- **Status labels.** Some scripts carry labels such as "INTERNAL, UNREVIEWED" or "not for publication". These were written while the analysis was under way and are kept unchanged: some are written into output files, and one is required by a consistency check. Both studies were independently verified before publication.
- **Process notes.** Some comments name project team members or quote design decisions. They are kept as a record of how the analysis was built.
- **Suppressed cells.** Census PUMS are public data, so the code computes every cell, including those suppressed in the published reports because they did not meet the reliability criteria. Please do not report suppressed estimates as findings.

## Version history

| Tag | What it is |
| --- | --- |
| `star-v1.0-deposit-exact`, `awac-v1.0-deposit-exact` | The scripts exactly as they stood when each study was published |
| `senior-transportation-access-v1.0`, `aging-without-a-car-v1.0` | The public release: the two comments naming internal file paths removed, test paths made relative, and the two required AWAC input files added |

To see every change from the original scripts, compare the tags, for example: `git diff awac-v1.0-deposit-exact aging-without-a-car-v1.0`.

## Citing

If you use this code, please cite the relevant report DOI above and this repository.

## License

Code: [MIT License](LICENSE). The two data files in `awac-v1.0/inputs/` are published study data under CC BY-SA 4.0, like the reports and data deposits on Zenodo.

## Contact

Questions, corrections or collaboration: [seniormedrides.com/research](https://seniormedrides.com/research/)
