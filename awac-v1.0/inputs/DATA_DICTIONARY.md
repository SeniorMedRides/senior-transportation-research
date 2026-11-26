> **Content-locked draft — not for public distribution until publication is authorized.** Senior Transportation Access Report, Version 1.0. Publication date: To be established after final editorial approval and website staging.

# Data dictionary: Senior Transportation Access Report datasets, Version 1.0
All files are UTF-8 CSV with one header row. ± values are 90% margins of error (MOE90 = 1.645 × SDR replicate SE). "pp" means percentage points. All estimates are ACS 2020–2024 5-year period averages (2020–2024) for people 65+ in housing units.

**Study-area identifiers.** area_id values: boise, las_vegas, orlando, phoenix, sacramento, salt_lake_city, stockton, tampa, eight_area_total. The identifier `boise` always means the **Boise PUMA region** (six 2020 PUMAs covering Ada and Canyon counties, ID, which also include parts of Gem, Owyhee, Payette and Washington counties). The `area` label column in the analysis-package files already reads "Boise PUMA region"; no source value was changed. Display labels, display order and PUMA lists are in `study_areas.csv`.

**License.** Original text, charts and other eligible material by the SeniorMedRides Research & Insights Division: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0), https://creativecommons.org/licenses/by-sa/4.0/. Adaptations must be shared under the same or a compatible license. Facts and estimates themselves are not subject to copyright. U.S. Census Bureau source data and other third-party material are not relicensed and remain under their own terms. CC BY-SA 4.0 does not cover the third-party context files `data/acs_published_context.csv` (figures from U.S. Census Bureau published ACS tables B18105 and B25045) and `data/cdc_places_context.csv` (figures from CDC PLACES). They reproduce source figures for context only; those figures are not relicensed and remain under their sources' terms. Cite the data as: SeniorMedRides Research & Insights Division ([PUBLICATION YEAR]), Senior Transportation Access Report datasets, Version 1.0. https://seniormedrides.com/research/senior-transportation-access/ [DOI TO BE ASSIGNED ON ARCHIVE DEPOSIT]

## joint_estimates.csv
Area-level joint estimates. From analysis package v1.1 (`outputs/joint_estimates.csv`; the `total_method` column is filled on the total row only). Counts (older_hh, older_amb, older_amb_noveh, older_noveh) each with _moe90, _unweighted_n and _cv; shares share_amb_in_noveh_hh_pct and share_older_in_noveh_hh_pct with _moe90_pp; geography fields (state_fips, study_counties, pumas, nesting checks); reliability_flag.

## age_specific.csv (one row per area × age_group)
| Field | Definition |
|---|---|
| age_group | 65_74, 75_84, 85_plus |
| older_hh, _moe90, _unweighted_n | Persons in the universe (65+ in housing units) in the age group |
| older_amb, … | Universe persons with walking difficulty (DPHY=1) |
| older_amb_noveh, … | Joint: DPHY=1 and household VEH=0 |
| older_noveh, … | Universe persons in a household with VEH=0 |
| amb_prevalence_pct, _moe90_pp | older_amb / older_hh × 100 |
| share_amb_in_noveh_hh_pct, _moe90_pp | older_amb_noveh / older_amb × 100 |
| share_older_in_noveh_hh_pct, _moe90_pp | older_noveh / older_hh × 100 |
| ratio, ratio_moe90 | share_amb_in_noveh_hh / share_older_in_noveh_hh |
| small_n_flag | "small unweighted n (<50)" if the joint cell has fewer than 50 sample records |

## age_standardized.csv (one row per area)
| Field | Definition |
|---|---|
| crude_share_amb_in_noveh_hh_pct, _moe90_pp | Unadjusted share (a), equal to joint_estimates |
| std_share_amb_in_noveh_hh_pct, _moe90_pp | Share (a) directly standardized to S1 (eight-area 65+ age mix) |
| std_alt_share_amb_in_noveh_hh_pct, _moe90_pp | Share (a) standardized to S2 (eight-area 65+ with walking difficulty age mix), sensitivity |
| crude_share_older_in_noveh_hh_pct, _moe90_pp | Unadjusted share (b) |
| std_share_older_in_noveh_hh_pct, _moe90_pp | Share (b) standardized to S1 |
| crude_ratio, _moe90 / std_ratio, _moe90 | (a)/(b), unadjusted / both standardized to S1 |
| std_gap_pp, _moe90_pp | Standardized (a) minus standardized (b) |
| pct_of_65plus_aged_85plus, _moe90_pp | Share of the universe aged 85+ (age-mix descriptor) |
S1: 65–74 0.591331; 75–84 0.305893; 85+ 0.102776. S2: 0.409652; 0.354223; 0.236126.

## comparisons.csv (one row per test)
| Field | Definition |
|---|---|
| family | 1 = area vs other seven pooled (24 tests); 2 = pairwise on standardized (a) (28); 3 = within-area standardized gap (9) |
| measure, comparison | What is compared; "X minus Y" |
| estimate, moe90 | Difference (pp for shares; ratio units for ratio) and its MOE90 |
| z, p | z = estimate/SE; two-sided normal p (unadjusted) |
| holm_threshold, holm_adjusted_p | Holm step-down threshold for the test's position in the Holm order, and adjusted p (familywise alpha 0.10) |
| holm_significant | True if the difference remains after Holm adjustment |

## with_without_contrast.csv (one row per area plus the total)
| Field | Definition |
|---|---|
| older_without_amb, _moe90 | Persons 65+ in the universe without walking difficulty (DPHY=2) |
| older_without_amb_noveh, _moe90 | Those without walking difficulty in a household with VEH=0 |
| share_with_amb_in_noveh_hh_pct, _moe90_pp | Share (a): joint ÷ persons with walking difficulty |
| share_without_amb_in_noveh_hh_pct, _moe90_pp | No-vehicle share among persons without walking difficulty |
| diff_with_minus_without_pp, _moe90_pp | Difference, percentage points |
| ratio_with_to_without, _moe90 | Ratio |
| diff_exceeds_moe90 | True if the absolute difference is larger than its MOE |

## with_without_std.csv (one row per area plus the total)
crude_/std_ share_with, share_without (pct, moe90_pp); crude_/std_ diff_pp, diff_moe90_pp, diff_exceeds_moe90, ratio, ratio_moe90. Standardized to S1 (both shares).

## with_without_by_age.csv (area × age group)
Age-specific share_with / share_without (pct, moe90_pp), diff_with_minus_without_pp (and MOE), ratio_with_to_without (and MOE), with_amb_noveh_unweighted_n, small_n_flag.

## part_vs_whole.csv (supporting framing; one row per area plus the total)
Extract of `age_standardized.csv`: share (a) among older adults with walking difficulty and share (b) among all older adults, unadjusted and standardized to S1, with the part-vs-whole ratio. Supporting table only; the primary framing is with vs without.

## headline_figures.csv
Every rounded or derived figure used in headlines, summaries and outreach, with the source value and the rule used to derive it (for example one-decimal rounding of a two-decimal share, or a share computed from two counts in `age_specific.csv`). Derived shares without a margin of error are labeled as such.

## standard_population.csv
The age standards S1 and S2 used for direct standardization.

## study_areas.csv (one row per area plus the total)
area_id; display_label (use this in all publications); display_order (alphabetical by label, total last; never by value); study_definition; state_fips; county_fips; pumas_2020; pumas_exactly_nest_in_counties; extra_counties_in_pumas; source_area_label (the `area` value in the analysis-package files). Values are copied from `joint_estimates.csv`.

## Chart data (`charts/data/*.csv`)
One file per chart: chart_id, row_order, row_id, row_label, series, series_label, estimate, moe90, lower_90, upper_90, value_label, unit, source_file, estimate_field, moe90_field. estimate and moe90 are copied from the named source file and field; lower_90 and upper_90 are estimate ∓ moe90 (lower end clipped at 0).

## acs_published_context.csv and cdc_places_context.csv
Context figures from ACS 2020–2024 5-year published tables B18105 and B25045 (study-area county unions; for the Boise PUMA region the published-table geography is Ada plus Canyon counties exactly, labeled in `geography_label`, and is not the Boise PUMA region; the source `name` value "Boise" is kept unchanged) and the CDC PLACES 2025 county measure "lack of reliable transportation" (2023 data, modeled, adults 18+). Different universes from the PUMS estimates; context only.

## Third-party data
The estimates are derived from U.S. Census Bureau ACS PUMS files. Source data: U.S. Census Bureau, American Community Survey (ACS) 2020–2024 5-year Public Use Microdata Sample (PUMS). The Census Bureau has not reviewed, endorsed or certified this analysis or its findings. Census Bureau data and CDC PLACES data are not relicensed by SeniorMedRides and keep their own terms. CC BY-SA 4.0 does not cover the third-party context files `data/acs_published_context.csv` (figures from U.S. Census Bureau published ACS tables B18105 and B25045) and `data/cdc_places_context.csv` (figures from CDC PLACES). They reproduce source figures for context only; those figures are not relicensed and remain under their sources' terms.
