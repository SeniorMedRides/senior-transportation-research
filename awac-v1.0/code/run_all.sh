#!/usr/bin/env bash
# Aging Without a Car run v1.2: full pipeline in SAP section 11 order. Stops at the first failure.
# Usage: code/run_all.sh INPUTS_DIR     (or set AWAC_INPUTS). INPUTS_DIR holds pums/csv_[hp]{az,ca,fl,id,nv,ut}.zip, tract_puma.txt,
#        PUMS_Data_Dictionary_2020-2024.csv/.txt and 2020_2024AccuracyPUMS.pdf, as listed in code/v1_0_analysis/SHA256SUMS-inputs.txt.
# The Version 1.0.1 data folder needed for the reproduction check is bundled at ../v1_0_1_data (verified against its checksum list).
set -euo pipefail
INPUTS="$(cd "${1:-${AWAC_INPUTS:?usage: run_all.sh INPUTS_DIR (or set AWAC_INPUTS)}}" && pwd)"
CODE="$(cd "$(dirname "$0")" && pwd)"; RUN="$(dirname "$CODE")"; V10="$RUN/v1_0_1_data"; LOGS="$RUN/logs"; mkdir -p "$LOGS"
cd "$CODE"
# 0. input and bundled-data checksums
( cd "$INPUTS" && sed 's#  inputs/#  #' "$CODE/v1_0_analysis/SHA256SUMS-inputs.txt" | sha256sum -c - ) > "$LOGS/00-input-checksums.log" 2>&1
( cd "$V10" && sha256sum -c SHA256SUMS-v1.0.1-data.txt ) >> "$LOGS/00-input-checksums.log" 2>&1
# 1a. Version 1.0 reproduction: rerun the unchanged Version 1.0 code in a scratch copy and compare its seven estimate CSVs byte for byte
R10="$RUN/repro_v1_0"; rm -rf "$R10"; mkdir -p "$R10"; cp -r "$CODE/v1_0_analysis/." "$R10/"; mkdir -p "$R10/sensitivity/outputs"; ln -s "$INPUTS" "$R10/inputs"
( cd "$R10" && date '+started %F %T %Z' && python3 estimate_joint.py --out outputs && python3 with_without_contrast.py --out outputs --overwrite-bundled \
  && python3 supplementary_difference.py --out outputs --overwrite-bundled && (cd sensitivity && python3 age_sensitivity.py && python3 with_without_std.py) && date '+ended %F %T %Z' ) > "$LOGS/01a-v1.0-code-rerun.log" 2>&1
{ echo "Check 1a: Version 1.0 code rerun vs bundled Version 1.0.1 data (cmp)"; date '+%F %T %Z'
  for f in joint_estimates.csv with_without_contrast.csv; do cmp "$R10/outputs/$f" "$V10/$f" && echo "IDENTICAL $f"; done
  for f in age_specific.csv age_standardized.csv comparisons.csv with_without_std.csv with_without_by_age.csv; do cmp "$R10/sensitivity/outputs/$f" "$V10/$f" && echo "IDENTICAL $f"; done; } > "$LOGS/01b-v1.0-byte-identity.log"
[ "$(grep -c IDENTICAL "$LOGS/01b-v1.0-byte-identity.log")" = 7 ] || { echo "STOP: Version 1.0 reproduction failed"; exit 2; }
rm "$R10/inputs"
# 1b-3, tables, tests, sensitivity, lead
python3 awac_estimate.py --inputs "$INPUTS" > "$LOGS/awac-estimate-stdout.log" 2>&1
python3 awac_build_docs.py
python3 check_consistency_awac.py
python3 test_checker_planted_errors.py > "$LOGS/checker-planted-error-tests.txt"
# proof of no estimate change vs run v1 and run v1.1, when available (AWAC_RUN_V1 / AWAC_RUN_V1_1, default ../../run-v1, ../../run-v1.1)
RV1="${AWAC_RUN_V1:-$RUN/../run-v1}"; RV11="${AWAC_RUN_V1_1:-$RUN/../run-v1.1}"
if [ -d "$RV1/outputs" ] && [ -d "$RV11/outputs" ]; then python3 compare_outputs.py "$RV1" "$RV11" > /dev/null; echo "compare_outputs: no estimate changed vs run v1 and v1.1"; else echo "compare_outputs: skipped (earlier runs not found)"; fi
echo "run_all: PASS"
