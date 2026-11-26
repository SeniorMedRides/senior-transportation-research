"""Shared constants for the Version 1.0 production package (content-locked draft).
Decision text comes from David's production direction of November 10, 2026 (licensing direction t19u supersedes t18u)."""
import pathlib
C = pathlib.Path(__file__).resolve().parent; R = C.parent; W = R.parent
for _d in ("data","disclosures","charts/reference","charts/data","charts/specs","report","fact-sheets","methodology","media/local-briefs","web","citation","archive-prep","logs"): (R/_d).mkdir(parents=True, exist_ok=True)
DIV = "SeniorMedRides Research & Insights Division"
FLAG = "Senior Transportation Access Report"
SUBTITLE = "Walking Difficulty and Household Vehicle Access Among Older Adults in Eight U.S. Study Areas"
TITLE = f"{FLAG}: {SUBTITLE}"
EDITION = "Version 1.0"
URL = "https://seniormedrides.com/research/senior-transportation-access/"
CENTER = "https://seniormedrides.com/research/"
SPOKES = "David P. Faustina, SeniorMedRides.com"
PUBDATE = "To be established after final editorial approval and website staging"
DOI_PH = "[DOI TO BE ASSIGNED ON ARCHIVE DEPOSIT]"
YEAR_PH = "[PUBLICATION YEAR]"
DATE_PH = "[PUBLICATION DATE]"
LOCK = "Content-locked draft — not for public distribution until publication is authorized"
NOTICE = f"> **{LOCK}.** {FLAG}, {EDITION}. Publication date: {PUBDATE}.\n"
MEDIA_LOCK = "DRAFT — NOT FOR DISTRIBUTION"
MEDIA_NOTICE = f"> **{MEDIA_LOCK}.** Draft media material for the {FLAG}, {EDITION}. Proposed text only; requires David P. Faustina's approval. Publication date: {PUBDATE}.\n"
STUDY = "ACS 2020–2024 5-year"
SOURCE_LINE = "Source: SeniorMedRides.com analysis of ACS 2020–2024 5-year PUMS"
CC = "CC BY-SA 4.0"
CC_NAME = "Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)"
CC_URL = "https://creativecommons.org/licenses/by-sa/4.0/"
LICENSE_SHORT = (f"Original text, charts and other eligible material by the {DIV}: {CC_NAME}, {CC_URL}. "
                 "Adaptations must be shared under the same or a compatible license. Facts and estimates themselves are not subject to copyright. "
                 "U.S. Census Bureau source data and other third-party material are not relicensed and remain under their own terms.")
THIRD_PARTY_FILES = ("acs_published_context.csv", "cdc_places_context.csv")
THIRD_PARTY_DATA_NOTE = ("CC BY-SA 4.0 does not cover the third-party context files `data/acs_published_context.csv` (figures from U.S. Census Bureau published ACS tables B18105 and B25045) "
                         "and `data/cdc_places_context.csv` (figures from CDC PLACES). They reproduce source figures for context only; those figures are not relicensed and remain under their sources' terms.")
LICENSE_CODE = "Original research code: MIT License approved in principle; to be distributed separately after ownership and dependency review (pending)."
NOT_MEASURED = "These estimates do not directly measure missed medical appointments, transportation demand, wheelchair use, or unmet transportation needs."
CENSUS_DISCLAIMER = ("Source data: U.S. Census Bureau, American Community Survey (ACS) 2020–2024 5-year Public Use Microdata Sample (PUMS). "
                     "The Census Bureau has not reviewed, endorsed or certified this analysis or its findings.")
CITE_APA = f"{DIV}. ({YEAR_PH}). *{TITLE}* ({EDITION}). SeniorMedRides.com. {URL} {DOI_PH}"
CITE_CHI = f"{DIV}. *{TITLE}*. {EDITION}. SeniorMedRides.com, {DATE_PH}. {URL}. {DOI_PH}."
CITE_SHORT = f"{DIV} ({YEAR_PH}), {FLAG}, {EDITION}, {URL}"
def cite_fs(area): return f"{DIV}. ({YEAR_PH}). *{FLAG}, {EDITION}: {area} fact sheet*. SeniorMedRides.com. {URL} {DOI_PH}"
HOLM_REF = "Holm, S. (1979). A simple sequentially rejective multiple test procedure. Scandinavian Journal of Statistics, 6(2), 65–70."
ACC_URL = "https://www2.census.gov/programs-surveys/acs/tech_docs/pums/accuracy/2020_2024AccuracyPUMS.pdf"
TYPE_SYSTEM = "Source Sans 3 / Source Serif 4 / Source Code Pro"
# Study areas in alphabetical order of their display label: a fixed, value-independent order that avoids implied ranking.
NAME = {'boise':'Boise PUMA region','las_vegas':'Las Vegas','orlando':'Orlando','phoenix':'Phoenix','sacramento':'Sacramento','salt_lake_city':'Salt Lake City','stockton':'Stockton','tampa':'Tampa','eight_area_total':'Eight areas combined'}
IDS = sorted([k for k in NAME if k != 'eight_area_total'], key=lambda a: NAME[a]); TOT = 'eight_area_total'
SLUG = {a: NAME[a].lower().replace(' ', '-') for a in IDS}
def fs_name(i, a): return f"{i+1:02d}-{SLUG[a]}-v1.0"
