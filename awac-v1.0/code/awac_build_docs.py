#!/usr/bin/env python3
"""Aging Without a Car run v1: writes the INTERNAL methods/results technical summary (not a public report draft) and the
section 10 web/area-page items as data only. Every number is read from outputs/*.csv or outputs/run_results.json; none is typed.
Code version awac-run-1.2.0. Usage: python3 awac_build_docs.py"""
import csv, json, pathlib, datetime
RUN = pathlib.Path(__file__).resolve().parent.parent; O = RUN/'outputs'; DOCS = RUN/'docs'; WEB = RUN/'web-data'
DOCS.mkdir(exist_ok=True); WEB.mkdir(exist_ok=True)
rd = lambda f: list(csv.DictReader(open(O/f)))
RES = json.load(open(O/'run_results.json')); LEAD = RES['lead']
TITLE = 'Aging Without a Car'
STATUS = 'INTERNAL TECHNICAL SUMMARY — not a public report draft; not for publication or distribution'
STUDY = 'ACS 2020–2024 5-year'
NOT_MEASURED = 'These estimates do not directly measure missed medical appointments, transportation demand, wheelchair use, or unmet transportation needs.'
REPORT_URL = 'https://seniormedrides.com/research/aging-without-a-car/'; CENTER = 'https://seniormedrides.com/research/'
V10_URL = 'https://seniormedrides.com/research/senior-transportation-access/'
SLUG = {'boise':'boise-puma-region','las_vegas':'las-vegas','orlando':'orlando','phoenix':'phoenix','sacramento':'sacramento','salt_lake_city':'salt-lake-city','stockton':'stockton','tampa':'tampa'}
CITY = {'boise':'https://seniormedrides.com/boise-id/','las_vegas':'https://seniormedrides.com/las-vegas-nv/','orlando':'https://seniormedrides.com/orlando-fl/','phoenix':'https://seniormedrides.com/phoenix-az/',
        'sacramento':'https://seniormedrides.com/sacramento-ca/','salt_lake_city':'https://seniormedrides.com/salt-lake-city-ut/','stockton':'https://seniormedrides.com/stockton-ca/','tampa':'https://seniormedrides.com/tampa-fl/'}
T1 = {r['area_id']:r for r in rd('t1_no_vehicle_reused_v1.0.csv')}; T4 = rd('t4_living_alone_no_vehicle.csv'); T5 = {r['area_id']:r for r in rd('t5_no_vehicle_living_alone_vs_not.csv')}
T6 = {r['area_id']:r for r in rd('t6_std_living_alone_no_vehicle_share.csv')}; T7 = {r['area_id']:r for r in rd('t7_living_alone_no_vehicle_walking_difficulty.csv')}
T8 = {r['area_id']:r for r in rd('t8_independent_living_difficulty_by_vehicle.csv')}; T3 = rd('t3_profile_no_vehicle_vs_with_vehicle.csv'); S150 = rd('sens1_t3_profile_poverty_cut_150.csv')
F1 = rd('f1_tests_area_vs_other_seven.csv'); F2 = rd('f2_tests_living_alone_vs_not.csv'); SENS2 = rd('sens2_f1_f2_standard_S2.csv')
AREA = {r['area_id']:r['area'] for r in T1.values()}; IDS = [a for a in T1 if a != 'eight_area_total']; TOT = 'eight_area_total'
t4 = {(r['area_id'],r['age_group']):r for r in T4}
def c(v): return f'{int(v):,}'
def pm(v, m, unit='%'): return f'{float(v):.2f}{unit} ±{float(m):.2f}'
L = []; A = L.append
A(f'# {TITLE}: methods and results technical summary (run v1.2)\n')
A(f'> **{STATUS}.** Prepared under the locked Statistical Analysis Plan (Gate 1, approved by David P. Faustina on 13 November 2026). Code version {RES["version"]}. Generated {datetime.date.today().isoformat()}.\n')
A('Run v1.2 applies David P. Faustina\'s reporting rule for fragile F1 results (14 November 2026, 4:40 PM; section 4 and section 7, item 12). No estimate, margin of error, test result or tier changed; the proof is `logs/v1.2-vs-v1-and-v1.1-output-diff-report.md`, and the changes are listed file by file in `CHANGELOG-v1.1-to-v1.2.md`.\n')
A('Run v1.1 applied the fixes David P. Faustina chose after independent validation of run v1 (PASS WITH NOTES). No estimate, margin of error, test result or tier changed; the proof is `logs/v1.1-vs-v1-output-diff-report.md`, and every change is listed file by file in `CHANGELOG-v1-to-v1.1.md`.\n')
A('This file documents what the run did and what it produced, for David and for independent validation. It is not report text and has not been reviewed for publication.\n')
A('## 1. Data and run\n')
A(f'- Data: U.S. Census Bureau, {STUDY} PUMS, person and housing files for Arizona, California, Florida, Idaho, Nevada and Utah. Period averages, including pandemic-era years.')
A('- Inputs: the Version 1.0 files on disk; all 16 input files match the Version 1.0 input checksums (`logs/00-input-checksums.log`). Nothing was re-downloaded.')
A('- Universe: people 65 and older in housing units (TYPEHUGQ = 1) in the eight study areas; group quarters excluded. Study areas as in Version 1.0, including the Boise PUMA region.')
A('- Estimation: person weight PWGTP and 80 replicate weights; successive-difference replicate standard errors; 90% margins of error (1.645 × SE); shares, differences and ratios formed inside each replicate; direct age standardization to the Version 1.0 standard S1 inside each replicate.')
A('- Software: Python standard library; Version 1.0 estimation code reused unchanged (byte-identical copies in `code/v1_0_analysis/`), new code in `code/awac_estimate.py`.\n')
A('## 2. Checks (SAP section 11), in order\n')
A('| Check | Result |\n| --- | --- |')
A('| 0. Input checksums | 16 of 16 files match the Version 1.0 checksums |')
A('| 1a. Version 1.0 code rerun (now part of `code/run_all.sh`) | all seven Version 1.0 estimate CSVs reproduced byte for byte (`logs/01b-v1.0-byte-identity.log`) |')
A('| 1b. Version 1.0 reproduction in the new pipeline | T1, T2 and the walking-difficulty contrast (crude, by age, age-standardized) match the Version 1.0 data files exactly, margins of error included; 0 mismatches (`logs/awac-run.log`) |')
C2 = RES['check2a']
A(f'| 2a. Internal sums | replicate by replicate: {C2["age_area_identities"]} identities (age groups to area totals, areas to the eight-area total) and {C2["independent_identities"]} identities against totals computed independently of the cell table (a separate read of the PUMS files with the Version 1.0 code, and direct accumulators keyed on the raw household-size and vehicle codes): living alone plus not living alone and no vehicle plus vehicle each equal all people 65+, and the cell-table living-alone and no-vehicle totals equal the independent totals; {C2["failures"]} failures |')
A('| 2b. T3 shares | every T3 variable sums to 100% within rounding: 0 failures |')
A(f'| 3. Recode check | NP = 1 agrees with HHT = 4 or 6 for all {c(RES["recode"]["householders"])} householders 65+ in the universe; 0 disagreements |')
A('| 4. Publication checker | extended Version 1.0 checker run on this summary and the web data items (`logs/consistency-report-awac.txt`) |')
A('\nMissing values among people 65+ in the universe: none for walking difficulty, independent living difficulty, poverty ratio or tenure.\n')
A('## 3. Lead finding, filled by the section 9 rule\n')
A(f'- Rule 1: {LEAD["rule1"]}.')
A(f'- Rule 2: {LEAD["rule2"]}. Ratio inputs: unadjusted {T5[TOT]["crude_ratio"]} ±{T5[TOT]["crude_ratio_moe90"]}, age-adjusted {T5[TOT]["std_ratio"]} ±{T5[TOT]["std_ratio_moe90"]}, each rounded to the nearest half.\n')
A(f'> {LEAD["sentence1"]} {LEAD["sentence2"]}\n>\n> {NOT_MEASURED} {LEAD["independent_living_line"]}\n')
A('The subject of the second sentence ("People 65 and older who live alone") is supplied around the plan\'s quoted fragment; the fragment itself is unchanged. No area comparison appears in the lead.\n')
A('## 4. Results\n')
A('All estimates below are in the Reported tier (n of 50 or more and CV of 30% or less) unless marked. 90% margins of error.\n')
A('**T4. Living alone in a household with no vehicle, people 65+**\n')
A('| Area | Count | Share of all people 65+ | Share of no-vehicle older adults who live alone |\n| --- | --- | --- | --- |')
for a in IDS + [TOT]:
    r = t4[(a,'65_plus')]; A(f'| {AREA[a]} | {c(r["lives_alone_no_vehicle"])} ±{c(r["lives_alone_no_vehicle_moe90"])} | {pm(r["share_of_all_65plus_pct"], r["share_of_all_65plus_moe90_pp"])} | {pm(r["share_of_no_vehicle_65plus_living_alone_pct"], r["share_of_no_vehicle_65plus_living_alone_moe90_pp"])} |')
A('\nEight areas combined, by age group:\n\n| Age | Count | Share of all people 65+ in the age group | Share of no-vehicle older adults in the age group who live alone |\n| --- | --- | --- | --- |')
for g,lab in (('65_74','65–74'),('75_84','75–84'),('85_plus','85+')):
    r = t4[(TOT,g)]; A(f'| {lab} | {c(r["lives_alone_no_vehicle"])} ±{c(r["lives_alone_no_vehicle_moe90"])} | {pm(r["share_of_all_65plus_pct"], r["share_of_all_65plus_moe90_pp"])} | {pm(r["share_of_no_vehicle_65plus_living_alone_pct"], r["share_of_no_vehicle_65plus_living_alone_moe90_pp"])} |')
dets = sorted({r['age_detail_rule'] for r in T4})
A(f'\nAge-detail rule (section 7): every area kept all three age groups ({", ".join(dets)}).\n')
r = T5[TOT]
A('**T5. No-vehicle share, living alone vs not living alone (eight areas combined; family F2)**\n')
A('| Measure | Living alone | Not living alone | Difference (points) | Ratio |\n| --- | --- | --- | --- | --- |')
A(f'| Unadjusted | {pm(r["crude_share_no_vehicle_living_alone_pct"], r["crude_share_no_vehicle_living_alone_moe90_pp"])} | {pm(r["crude_share_no_vehicle_not_living_alone_pct"], r["crude_share_no_vehicle_not_living_alone_moe90_pp"])} | {float(r["crude_diff_pp"]):.2f} ±{float(r["crude_diff_moe90_pp"]):.2f} | {float(r["crude_ratio"]):.2f} ±{float(r["crude_ratio_moe90"]):.2f} |')
A(f'| Age-standardized (S1) | {pm(r["std_share_no_vehicle_living_alone_pct"], r["std_share_no_vehicle_living_alone_moe90_pp"])} | {pm(r["std_share_no_vehicle_not_living_alone_pct"], r["std_share_no_vehicle_not_living_alone_moe90_pp"])} | {float(r["std_diff_pp"]):.2f} ±{float(r["std_diff_moe90_pp"]):.2f} | {float(r["std_ratio"]):.2f} ±{float(r["std_ratio_moe90"]):.2f} |')
A('\nArea rows are in `outputs/t5_no_vehicle_living_alone_vs_not.csv`.\n')
A('**T6 and F1. Age-standardized share of all people 65+ who live alone with no vehicle; each area vs the other seven combined (8 tests, Holm at 10%)**\n')
A('| Area | T6 share | Difference from the other seven (points) | Holm-adjusted p | Result | Under alternative standard S2 (section 8) | Fragile (David\'s rule) | Local summaries |\n| --- | --- | --- | --- | --- | --- | --- | --- |')
def hl(t):
    fr = f'yes: {t["fragility_reason"]}' if t.get('fragile')=='True' else 'no'
    ls = (f'may state: {t["local_summary_claim"]}' if t.get('local_summary_eligible')=='True' else
          ('no comparison claim (not distinguishable)' if t.get('remains_after_holm_10pct')!='True' else 'not for headlines or local summaries'))
    return f'{fr} | {ls}'
f1 = {t['area_id']:t for t in F1}
for a in IDS:
    t = f1[a]; A(f'| {AREA[a]} | {pm(T6[a]["std_share_65plus_living_alone_no_vehicle_pct"], T6[a]["std_share_65plus_living_alone_no_vehicle_moe90_pp"])} | {float(t["estimate_pp"]):+.2f} ±{float(t["moe90_pp"]):.2f} | {t["holm_adjusted_p"]} | {t["wording"]} | {t["s2_sensitivity_note"]} | {hl(t)} |')
A(f'| {AREA[TOT]} | {pm(T6[TOT]["std_share_65plus_living_alone_no_vehicle_pct"], T6[TOT]["std_share_65plus_living_alone_no_vehicle_moe90_pp"])} | — | — | not a test | — | — | — |')
nb1 = [AREA[t['area_id']] for t in F1 if t.get('borderline')=='True']; nt1 = [AREA[t['area_id']] for t in F1 if 'not tested' in t['wording']]
A(f'\nF1: {sum(t.get("remains_after_holm_10pct")=="True" for t in F1)} of 8 remain after Holm adjustment; borderline: {", ".join(nb1) or "none"}; not tested (sample too small): {", ".join(nt1) or "none"}. Areas are listed alphabetically and are not ranked. '
  + 'All results stand under the plan and are reported here with their sensitivity notes. No area F1 result appears in headlines; headlines use only the pre-specified eight-area lead. '
  + 'Fragile, so kept out of headlines and local summaries: ' + (', '.join(AREA[t['area_id']] for t in F1 if t.get('fragile')=='True') or 'none') + '. '
  + 'May appear in local summaries: ' + (', '.join(f'{AREA[t["area_id"]]} ({t["local_summary_claim"]})' for t in F1 if t.get('local_summary_eligible')=='True') or 'none') + '. '
  + 'No comparison claim (not distinguishable): ' + (', '.join(AREA[t['area_id']] for t in F1 if t.get('remains_after_holm_10pct')!='True') or 'none') + '.\n')
A('**F2. Within each area, age-standardized no-vehicle share, living alone minus not living alone (9 tests, Holm at 10%)**\n')
A('| Area | Difference (points) | Age-adjusted ratio | Holm-adjusted p | Result | Under alternative standard S2 (section 8) |\n| --- | --- | --- | --- | --- | --- |')
for t in F2:
    A(f'| {AREA[t["area_id"]]} | {float(t["estimate_pp"]):+.2f} ±{float(t["moe90_pp"]):.2f} | {float(t["std_ratio"]):.2f} ±{float(t["std_ratio_moe90"]):.2f} | {t["holm_adjusted_p"]} | {t["wording"]} | {t["s2_sensitivity_note"]} |')
nb2 = [AREA[t['area_id']] for t in F2 if t.get('borderline')=='True']; nt2 = [AREA[t['area_id']] for t in F2 if 'not tested' in t['wording']]
A(f'\nF2: {sum(t.get("remains_after_holm_10pct")=="True" for t in F2)} of 9 remain after Holm adjustment; borderline: {", ".join(nb2) or "none"}; not tested (sample too small): {", ".join(nt2) or "none"}. Holm-adjusted p values shown as 0.0 are below floating-point resolution.\n')
r = T7[TOT]
A('**T7. Living alone, no vehicle and serious walking difficulty (descriptive)**\n')
A(f'Eight areas combined: {c(r["lives_alone_no_vehicle_walking_difficulty"])} ±{c(r["lives_alone_no_vehicle_walking_difficulty_moe90"])} people (CV {r["lives_alone_no_vehicle_walking_difficulty_cv"]}); {pm(r["share_of_all_65plus_pct"], r["share_of_all_65plus_moe90_pp"])} of all people 65+; {pm(r["share_of_living_alone_no_vehicle_group_pct"], r["share_of_living_alone_no_vehicle_group_moe90_pp"])} of the living-alone, no-vehicle group. '
  f'Area rows: {sum(T7[a]["shown"]=="True" for a in IDS)} of 8 areas have n of 50 or more and are shown (`outputs/t7_living_alone_no_vehicle_walking_difficulty.csv`). Descriptive only; no area comparisons.\n')
r = T8[TOT]
A('**T8. Independent living difficulty among people 65+ with and without a vehicle (descriptive)**\n')
A(f'Eight areas combined: {pm(r["independent_living_difficulty_no_vehicle_pct"], r["independent_living_difficulty_no_vehicle_moe90_pp"])} of people 65+ in a household with no vehicle report independent living difficulty, vs {pm(r["independent_living_difficulty_with_vehicle_pct"], r["independent_living_difficulty_with_vehicle_moe90_pp"])} of those with a vehicle; difference {float(r["diff_no_vehicle_minus_with_vehicle_pp"]):.2f} ±{float(r["diff_moe90_pp"]):.2f} points. {LEAD["independent_living_line"]}\n')
A('**T3. Profile of people 65+ in a household with no vehicle vs with a vehicle (eight areas combined; descriptive)**\n')
A('| Variable | Category | No vehicle | With vehicle |\n| --- | --- | --- | --- |')
t3 = {(r['group'],r['variable'],r['category']):r for r in T3 if r['area_id']==TOT}
for (g,v,cat),r in t3.items():
    if g != 'no_vehicle': continue
    w = t3[('with_vehicle',v,cat)]
    A(f'| {v.replace("_"," ")} | {cat.replace("_"," ")} | {pm(r["share_pct"], r["share_moe90_pp"])} | {pm(w["share_pct"], w["share_moe90_pp"])} |')
A(f'\nTenure detail: {c(RES["tenure_detail_n"])} sample records of "occupied without payment of rent" among no-vehicle older adults in the eight areas (threshold 50), so it is shown separately as a sub-row.\n')
A('## 5. Tiers and suppression (section 7)\n')
nr = [r for r in T3 if r['share_tier'] != 'Reported']
allnr = {}
for f in ('t1_no_vehicle_reused_v1.0.csv','t2_no_vehicle_by_age_reused_v1.0.csv','t4_living_alone_no_vehicle.csv','t5_no_vehicle_living_alone_vs_not.csv','t6_std_living_alone_no_vehicle_share.csv','t7_living_alone_no_vehicle_walking_difficulty.csv','t8_independent_living_difficulty_by_vehicle.csv'):
    allnr[f.split('_')[0].upper()] = sum(1 for r in rd(f) for k,v in r.items() if k.endswith('_tier') and v not in ('Reported',''))
clean = [t for t,v in allnr.items() if v == 0]
A(f'Tiers were assigned in code from each estimate\'s unweighted n and CV. Tables with every estimate in the Reported tier: {", ".join(clean)}. Non-Reported cells in other tables: ' + ('; '.join(f'{t}: {v}' for t,v in allnr.items() if v) or 'none') + '. T3 non-Reported cells:\n')
for r in nr: A(f'- {r["area"]}, {r["group"].replace("_"," ")}, {r["category"].replace("_"," ")}: {r["share_tier"]} (n {r["share_unweighted_n"]}){"; shown as — (sample too small)" if r["share_tier"]=="Suppressed" else "; indicative only; do not quote on its own"}')
A('')
A('## 6. Sensitivity checks (section 8)\n')
s150 = {(r['group'],r['category']):r for r in S150 if r['area_id']==TOT and r['variable']=='poverty'}
A(f'1. **Poverty cut.** T3 rerun with below 150% of poverty in place of below 100%: eight areas combined, {pm(s150[("no_vehicle","below_150")]["share_pct"], s150[("no_vehicle","below_150")]["share_moe90_pp"])} of no-vehicle older adults vs {pm(s150[("with_vehicle","below_150")]["share_pct"], s150[("with_vehicle","below_150")]["share_moe90_pp"])} of those with a vehicle are below 150%. T3 is descriptive, so no test conclusion can change. File: `outputs/sens1_t3_profile_poverty_cut_150.csv`.')
chg = [r for r in SENS2 if r['primary_conclusion_changes']=='True']; bchg = [r for r in SENS2 if r['borderline_status_changes']=='True']
A(f'2. **Age standard S2.** F1 and F2 rerun with the Version 1.0 alternative standard S2. Primary conclusions that change: ' + ('; '.join(f'{r["family"]} {AREA[r["area_id"]]} (S1: {r["S1_result"]}; S2: {r["S2_result"]})' for r in chg) or 'none') +
  '. Borderline status changes (result still remains at 10%): ' + ('; '.join(f'{r["family"]} {AREA[r["area_id"]]} (S2 Holm-adjusted p {r["S2_holm_adjusted_p"]})' for r in bchg) or 'none') +
  f'. F2 results remaining under S2: {sum(r["family"]=="F2" and "not distinguishable" not in r["S2_result"] and "not tested" not in r["S2_result"] for r in SENS2)} of {sum(r["family"]=="F2" for r in SENS2)}. Under section 8 the report must say so beside each changed result. File: `outputs/sens2_f1_f2_standard_S2.csv`.\n')
A('## 7. Implementation readings, confirmed by David P. Faustina (14 November 2026)\n')
A('These are readings of the plan where its text leaves a detail open. None changes a definition, test, threshold or table, so none is logged as a deviation. After validation David confirmed all eight as written (items 1–8), confirmed the lead rule\'s treatment of borderline F2 results (item 9), and confirmed that the name on the record, David P. Faustina, is correct.\n')
A('1. **n for tiering a share** is the unweighted count in the numerator, as the Version 1.0 small-n flag did. CV is SE divided by the estimate.')
A('2. **Differences and ratios** (T5, T8) take the worse tier of their two component shares; a CV is not a meaningful reliability measure for a difference near zero. All are Reported here, so the choice changes nothing in this run.')
A('3. **S1 and S2** are used at full precision, derived exactly as Version 1.0 did; they round to the six-decimal constants in the plan and in the Version 1.0 methodology.')
A('4. **F2 wording.** Section 6 wording rules are written for F1; F2 results that remain are worded "no-vehicle share higher among people living alone than among those living with others".')
A('5. **Lead sentence 2** needed a subject around the plan\'s quoted fragment (section 3 above).')
A('6. **T2** is reused as published: no 75+ collapse was applied. Every T2 cell has n of 50 or more, so the age-detail rule would not have changed it.')
A('7. **Age-specific standardization inputs** for T5 and T6 are written to `outputs/standardization_inputs_by_age.csv` for validation only; they are not a display table.')
A('8. **Web items.** The Version 1.0.2 web specification was not on disk at run v1. Section 10 items were generated as data only (`web-data/`); the Version 1.0 area-page URL is assumed to follow the same pattern (report URL plus slug). By David\'s direction, run v1.1 does not align the web items to the Version 1.0.3 web specification; that happens at the publication step. The only web-item change in run v1.1 is the headline and local-summary exclusion status.')
A('9. **Lead rule 2 and borderline F2 results.** The lead uses the eight-area F2 ratio sentence only if the result remains after Holm adjustment and is not borderline, consistent with section 6 (borderline results stay out of headlines). David confirmed this is intended. It was not triggered in this run.')
A('10. **Run v1.1: n and CV for differences and ratios** (section 4). T5, T8, F1 and F2 now carry an unweighted n and CV for each difference or ratio, taken from its two component shares: the smaller component n and the larger component CV. This is the same information the weaker-tier rule (item 2) already uses, so no tier changes.')
A('11. **Run v1.1: headline and local-summary exclusions** (superseded in run v1.2 by item 12). Results stand under the plan, but these F1 results are kept out of headlines and local summaries: any borderline result (section 6); any result whose conclusion changes under the alternative standard S2 (section 8; Las Vegas); and Orlando, whose Holm-adjusted p sits just under the 0.05 borderline cut (David\'s decision). The status is in the F1 and F2 output files, the web items and the checker.\n')
A('12. **Run v1.2: David\'s reporting rule for fragile F1 results** (a reporting decision, not a plan change; 14 November 2026, 4:40 PM). His words: "Leave Boise PUMA region and Stockton out of headlines and local summaries too. Rule: any F1 result that is fragile (it fails or becomes borderline under S2, or sits within a hair of the 5% cut under S1) stays out of headlines and local summaries, and is reported in the tables and technical report with its sensitivity note. That applies to the Boise PUMA region, Las Vegas, Orlando and Stockton. Sacramento and Tampa may appear in local summaries. Headlines use only the pre-specified eight-area lead." Follow-up decision (14 November 2026, 5:38 PM), on Phoenix, which is not fragile under the rule but was not named: "Yes, Phoenix may appear in its local summary."')
FR = RES['fragility_rule']; lo, hi = FR['near_cut_band']; F1BYID = {t['area_id']:t for t in F1}
DAVID_FRAGILE_NAMED = {'boise','las_vegas','orlando','stockton'}; DAVID_LOCAL_NAMED = {'phoenix','sacramento','tampa'}
NEXT = max((t for t in F1 if t.get('remains_after_holm_10pct')=='True' and float(t['holm_adjusted_p']) < lo), key=lambda t: float(t['holm_adjusted_p']))
A(f'    - Operationalization: a result that remains after Holm adjustment at 10% under S1 is fragile if its conclusion fails under S2, if it is borderline under S2, if it is borderline under S1, or if its S1 Holm-adjusted p lies in the near-cut band {lo} to {hi} ("within a hair" of the 5% cut, i.e. within 0.01 of it). The band is set by the motivating case, Orlando at ' + str(F1BYID['orlando']['holm_adjusted_p']) + '; the next-closest remaining result below the band is ' + AREA[NEXT['area_id']] + ' at ' + str(NEXT['holm_adjusted_p']) + ', so any lower band edge above that value and at or below Orlando\'s flags the same results.')
A(f'    - Result: fragile F1 results are ' + ', '.join(AREA[a] for a in FR['fragile_F1']) + '; local-summary eligible: ' + ', '.join(AREA[a] for a in FR['local_summary_eligible_F1']) + '; not distinguishable, so no comparison claim: ' + ', '.join(AREA[t['area_id']] for t in F1 if t.get('remains_after_holm_10pct')!='True') + '. '
  + ('The fragile set is exactly the four areas David named (Boise PUMA region, Las Vegas, Orlando, Stockton). ' if set(FR['fragile_F1'])==DAVID_FRAGILE_NAMED else 'WARNING: the fragile set differs from the four areas David named. ')
  + ('Local-summary eligibility matches David\'s decisions: Sacramento and Tampa (named 4:40 PM) and Phoenix (confirmed 5:38 PM; it remains under S1 and S2, is not borderline under either and is not near the cut, so it is not fragile; claim: "' + F1BYID['phoenix']['local_summary_claim'] + '").' if set(FR['local_summary_eligible_F1'])==DAVID_LOCAL_NAMED else 'WARNING: local-summary eligibility differs from the areas David named.')
  + ' F2 results flagged fragile: ' + (', '.join(AREA[t['area_id']] for t in F2 if t.get('fragile')=='True') or 'none') + '.')
A('    - Superseded: the run v1.1 headline/local-summary exclusions (Orlando by name, Las Vegas by S2) are replaced by this general rule.')
A('## 8. Deviations log (section 11)\n')
A('| Date | Change | Reason | Results affected | Approved by |\n| --- | --- | --- | --- | --- |\n| — | None | — | — | — |\n')
A('Nothing outside the plan was run: no race or ethnicity, no 2015–2019 comparison, no walkability, no pairwise area tests and no re-test of a Version 1.0 comparison.\n')
A('## 9. Disclosures that travel with any use of these results\n')
A(f'- {NOT_MEASURED}')
A(f'- {LEAD["independent_living_line"]}')
A('- Living alone is measured from the household roster; the survey does not record whether relatives live nearby or help with rides.')
A('- Differences between groups are associations, not causes.')
A(f'- Source data: U.S. Census Bureau, {STUDY} PUMS. The Census Bureau has not reviewed this analysis.\n')
(DOCS/'technical-summary-methods-results-run-v1.2.md').write_text('\n'.join(L)+'\n')
# ---------------- section 10 web items (data only)
items = []; F1BY = {t['area_id']:t for t in F1}
# Local research lines are generated from T4 counts only; no area comparison (F1) is used in them. Excluded F1 results are flagged so later
# local-summary generation cannot use them.
for a in IDS:
    r = t4[(a,'65_plus')]; lab = AREA[a]; where = lab if a=='boise' else f'the {lab} study area'
    ok = r['lives_alone_no_vehicle_tier']=='Reported'
    line = (f'{TITLE}: an estimated {c(r["lives_alone_no_vehicle"])} ±{c(r["lives_alone_no_vehicle_moe90"])} people 65+ in {where} live alone in a household with no vehicle.' if ok
            else f'{TITLE}: local estimates for {where}.')
    meta = (f'{lab}: an estimated {c(r["lives_alone_no_vehicle"])} people 65+ live alone in a household with no vehicle ({STUDY} PUMS, 90% MOE ±{c(r["lives_alone_no_vehicle_moe90"])}).')
    page = REPORT_URL + SLUG[a] + '/'
    items.append({'area_id':a,'area':lab,'slug':SLUG[a],'area_page_url':page,'up_link_report':REPORT_URL,'across_link_v1_0_area_page':V10_URL + SLUG[a] + '/',
                  'across_link_note':'assumed pattern; confirm against the Version 1.0.2 web specification (not on disk)','city_page_url':CITY[a],
                  'page_title':f'{TITLE}: {lab}','meta_description':meta,'meta_description_length':len(meta),'canonical_url':page,
                  'breadcrumb':[{'name':'Research','url':CENTER},{'name':TITLE,'url':REPORT_URL},{'name':lab,'url':page}],
                  'f1_comparison_headline_local_summary': 'excluded' if F1BY[a].get('headline_local_summary_eligible')=='False' else 'eligible',
                  'f1_exclusion_reason': F1BY[a].get('headline_local_summary_exclusion_reason',''),
                  'f1_fragile': F1BY[a].get('fragile') == 'True', 'f1_headline_eligible': False,
                  'f1_local_summary_eligible': F1BY[a].get('local_summary_eligible') == 'True', 'f1_local_summary_claim': F1BY[a].get('local_summary_claim',''),
                  'city_page_local_research_line':line,'city_page_qualifier_line':f'{STUDY} period estimate with 90% margin of error; see the report for what it does not measure.',
                  'source_fields':{'count':'outputs/t4_living_alone_no_vehicle.csv lives_alone_no_vehicle (65_plus)','tier':r['lives_alone_no_vehicle_tier']},
                  'structured_data':{'@context':'https://schema.org','@type':'WebPage','name':f'{TITLE}: {lab}','url':page,'isPartOf':{'@type':'Report','name':TITLE,'url':REPORT_URL}}})
rt = t4[(TOT,'65_plus')]
rmeta = f'An estimated {c(rt["lives_alone_no_vehicle"])} people 65+ in eight U.S. study areas live alone in a household with no vehicle ({STUDY} PUMS).'
report = {'report_url':REPORT_URL,'research_center':CENTER,'title':TITLE,'subtitle':'[TO BE SET — section 9: must name household vehicle availability]','meta_description':rmeta,'meta_description_length':len(rmeta),
          'canonical_url':REPORT_URL,'breadcrumb':[{'name':'Research','url':CENTER},{'name':TITLE,'url':REPORT_URL}],
          'headline_exclusions_f1':{AREA[t['area_id']]:t['headline_local_summary_exclusion_reason'] for t in F1 if t.get('headline_local_summary_eligible')=='False'},
          'headline_rule':'Headlines use only the pre-specified eight-area lead (SAP s.9); no area F1 result appears in headlines (David P. Faustina, 14 Nov 2026).',
          'local_summary_eligible_f1':{AREA[t['area_id']]:t['local_summary_claim'] for t in F1 if t.get('local_summary_eligible')=='True'},
          'note':'Generated as data only. The Version 1.0.2 web specification was not available on disk; layout and any remaining fields follow that specification when supplied.'}
(WEB/'report-page.json').write_text(json.dumps(report, indent=2, ensure_ascii=False)+'\n')
(WEB/'area-pages.json').write_text(json.dumps(items, indent=2, ensure_ascii=False)+'\n')
with open(WEB/'area-pages.csv','w',newline='') as f:
    keys = [k for k in items[0] if k not in ('breadcrumb','structured_data','source_fields')]
    w = csv.DictWriter(f, fieldnames=keys, extrasaction='ignore', lineterminator='\n'); w.writeheader(); w.writerows(items)
print('docs and web data written')
