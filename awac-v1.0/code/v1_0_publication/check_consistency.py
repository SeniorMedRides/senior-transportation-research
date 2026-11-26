#!/usr/bin/env python3
"""Consistency check for the Version 1.0 production package. Exit 0 only if every check passes. Writes logs/consistency-report.txt.
Checks:
 N  every statistic-like number in every Markdown document, chart SVG and web-metadata text matches a value in data/*.csv (standard roundings allowed)
 C  chart CSVs equal their source data fields; SVG value labels equal chart CSV values; titles/desc/role/source line; PNGs exist; no draft labels in images; alphabetical order
 F  fact sheets repeat the flagship's Table 1 and Table 2 rows for their area exactly (punch-list 9)
 B  banned or risky phrasing (negated standard disclosures and 'Do not say' sections excluded)
 K  ranking language and 'significant' wording (punch-list 7)
 G  'Boise' only as 'Boise PUMA region' (allowlisted explanatory phrases only) (punch-list 8)
 L  license: CC BY-SA 4.0 everywhere required; no CC BY 4.0 / 'to be confirmed' / old URL placeholder
 P  study period wording 'ACS 2020–2024 5-year' (punch-list 12); no hyphen-minus year ranges or 'five-year'
 M  'not measured' disclosure in report, fact sheets and media items; status labels; no 'published' claims
 T  Tampa absent from headlines, local briefs' comparison language and media headlines; borderline disclosure present
 H  headline values and framing (with vs without primary; age-adjusted present; part-vs-whole absent from headline sections)
 S  statistical disclosures (90% MOE, successive-difference, Holm, 10% familywise, direct standardization, not pre-registered)
 X  DOCX copies: header label present, text free of banned phrases; JSON/JSON-LD parse; HTML img alt text"""
import csv, re, sys, pathlib, json
C_ = pathlib.Path(__file__).resolve().parent; P = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else C_.parent
sys.path.insert(0, str(C_)); from common import *
D = P/'data'; FAIL = []; LOG = []; COUNT = {}
def fail(code, m): FAIL.append(f"[{code}] {m}")
def rel(p): return str(p.relative_to(P))
# ---------- allowed numbers
allowed = set()
def add(v):
    v = v.strip()
    if not v: return
    allowed.add(v.lstrip('+-'))
    try: x = abs(float(v))
    except ValueError: return
    for s in (f"{x:.2f}", f"{x:.1f}", f"{x:.0f}", f"{x:,.0f}", f"{x:.3g}", f"{x:g}", f"{x:,.2f}", f"{x:.6f}", f"{x:.3f}"): allowed.add(s)
    if x == int(x): allowed.add(f"{int(x):,}")
for f in D.glob('*.csv'):
    for r in csv.reader(open(f, newline='')):
        for cell in r:
            for tok in re.split(r'[;| ]', cell): add(tok)
# Non-data numbers: version labels, statistical constants (1.645, 0.10, 0.05), thresholds (50, 30%), ages, years, test-family sizes (24, 28, 9), replicate count (80),
# 249 (values compared in the independent validation, documented in the methodology), chart axis maxima.
WHITELIST = {'249','1.0','1.1','0.10','0.05','0.001','1.645','10','5','90','95','30','50','100','80','24','28','2020','2023','2024','2025','2026','2027','18','65','74','75','84','85'}
NUM = re.compile(r'(?<![\w.\-])(?:n=)?[−+\-]?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+|\d+(?=%)|(?<=±)\d+|(?<=n=)\d+|\d{3,})(?![\w])')
def strip_meta(text):
    text = re.sub(r'https?://\S+', ' ', text)
    text = re.sub(r'\b[0-9a-f]{64}\b', ' ', text)
    text = re.sub(r'`[^`]*`', ' ', text)
    text = text.replace(HOLM_REF, ' ')
    text = re.sub(r'Census server date [A-Z][a-z]+ \d+, 2026|downloaded November 8–9, 2026|November \d+, 2026', ' ', text)
    return text
def numbers(text):
    out = []
    for m in NUM.finditer(strip_meta(text)):
        t = m.group(0).replace('n=', '').lstrip('−+-')
        if re.fullmatch(r'20\d\d', t) or t in WHITELIST: continue
        out.append(t)
    return out
MD = sorted(p for p in P.rglob('*.md') if 'code' not in p.parts and p.parent != P)
ROOTMD = sorted(P.glob('*.md'))
SVGS = sorted((P/'charts'/'reference').glob('*.svg'))
NUMDOCS = [p for p in MD if p.name != 'chart-specs.md']
def vis(svg_text): return ' '.join(re.findall(r'>([^<]+)<', re.sub(r'<text class="tick"[^>]*>[^<]*</text>', '', svg_text)))
n = 0
for d in NUMDOCS + SVGS:
    text = d.read_text()
    if d.suffix == '.svg': text = vis(text)
    for t in numbers(text):
        n += 1
        if t not in allowed: fail('N', f"number not found in data CSVs: {t} in {rel(d)}")
wm = json.load(open(P/'web'/'web-metadata.json'))
for t in numbers(wm['abstract']):
    n += 1
    if t not in allowed: fail('N', f"number not in data: {t} in web-metadata.json abstract")
COUNT['N'] = f"{n} numbers in {len(NUMDOCS)} documents, {len(SVGS)} chart SVGs and the web abstract"
# ---------- charts
src_cache = {}
def src_rows(f):
    key = f.split(' ')[0]
    if key not in src_cache: src_cache[key] = list(csv.DictReader(open(P/key, newline='')))
    return src_cache[key]
nc = 0; EXPECT = [NAME[a] for a in IDS] + [NAME[TOT]]
for s in SVGS:
    t = s.read_text(); v = vis(t).lower(); cid = s.stem
    if 'draft' in v or 'internal' in v or 'content-locked' in v: fail('C', f"draft/internal text in chart {s.name}")
    if '<title' not in t or '<desc' not in t or 'role="img"' not in t: fail('C', f"missing title/desc/role in {s.name}")
    if SOURCE_LINE not in t: fail('C', f"source line missing in {s.name}")
    if not s.with_suffix('.png').exists() or s.with_suffix('.png').stat().st_size < 10000: fail('C', f"PNG missing for {s.name}")
    rows = list(csv.DictReader(open(P/'charts'/'data'/f'{cid}.csv', newline='')))
    labels = re.findall(r'<text class="value"[^>]*>([^<]+)</text>', t)
    if labels != [r['value_label'] for r in rows]: fail('C', f"SVG value labels differ from chart CSV in {cid}")
    for r in rows:
        nc += 1
        sr = src_rows(r['source_file']); key = 'age_group' if 'by_age' in r['source_file'] else 'area_id'
        match = [x for x in sr if x[key] == r['row_id'] and (key == 'area_id' or x['area_id'] == TOT)]
        if len(match) != 1: fail('C', f"{cid}: no unique source row for {r['row_id']}"); continue
        for fld, val in ((r['estimate_field'], r['estimate']), (r['moe90_field'], r['moe90'])):
            if abs(float(match[0][fld]) - float(val)) > 1e-9: fail('C', f"{cid}: {r['row_id']} {fld} {val} != source {match[0][fld]}")
    order = []
    for r in rows:
        if r['row_label'] not in order: order.append(r['row_label'])
    if 'by_age' not in cid and order != [x for x in EXPECT if x in order]: fail('C', f"{cid}: rows not in fixed alphabetical order")
spec = json.load(open(P/'charts'/'specs'/'chart-specs.json'))['charts']; alt = json.load(open(P/'charts'/'alt-text.json'))
if set(spec) != {s.stem for s in SVGS} or set(alt) != {s.name for s in SVGS}: fail('C', 'specs/alt text do not cover every chart')
for cid, sp in spec.items():
    if sp['alt_text'] != alt[cid+'.svg']['alt']: fail('C', f"spec alt text differs from alt-text.json for {cid}")
COUNT['C'] = f"{nc} chart data points verified against source fields; {len(SVGS)} charts"
# ---------- fact sheets vs flagship
rep_p = P/'report'/'senior-transportation-access-report-v1.0.md'; rep = rep_p.read_text()
FS = sorted((P/'fact-sheets').glob('*.md'))
def table_row(table_title, label):
    sec = rep.split(table_title)[1]
    return next(l for l in sec.split('\n') if l.startswith(f'| {label} |'))
nf = 0
for i, a in enumerate(IDS):
    fsp = P/'fact-sheets'/f'{fs_name(i,a)}.md'; t = fsp.read_text()
    r1 = [x.strip() for x in table_row('**Table 1.', NAME[a]).strip('|').split('|')]; r2 = [x.strip() for x in table_row('**Table 2.', NAME[a]).strip('|').split('|')]
    for cell in r1[1:] + r2[1:]:
        nf += 1
        if cell not in t: fail('F', f"{fsp.name}: flagship value '{cell}' not found in fact sheet")
    if NAME[a] not in t.split('\n')[2]: fail('F', f"{fsp.name}: title does not use the display label {NAME[a]}")
COUNT['F'] = f"{nf} flagship table cells found in the matching fact sheets"
# ---------- banned phrasing
BANNED = ['twice as likely','twice','stranded','trapped','isolated','homebound','cannot get to the doctor',"can't get to the doctor",'miss medical appointments','missed appointments',
          'need rides','demand for nemt','unmet need','wheelchair users','disabled seniors','eligible for medicaid','in 2024','today','worst','ranks #1','#1','caused by',
          'because they lost','because of their disability','proves','statistically certain','common for everyone','getting to a doctor is harder','access to care','other seniors']
NEGATED = [NOT_MEASURED, DIV, "not a measure of wheelchair use", "not a clinical diagnosis, and not a measure of wheelchair use", "wheelchair use", "unmet transportation need",
           "not counts of missed appointments or ride requests"]
def scan_text(t):
    t = re.sub(r'## Do not say\n.*?(?=\n## |\Z)', '', t, flags=re.S)
    for x in NEGATED: t = t.replace(x, ' ')
    return t.lower()
def banned_hits(low):
    return [b for b in BANNED if re.search((r'(?<![\w#])' if b[0].isalnum() else '') + re.escape(b) + (r'(?!\w)' if b[-1].isalnum() else ''), low)]
def dont_say_items(md):
    m = re.search(r'## Do not say\n(.*?)(?=\n## |\Z)', md, flags=re.S)
    return [l[2:].strip() for l in m.group(1).split('\n') if l.startswith('- ')] if m else []
SCAN = MD + ROOTMD
for d in SCAN + SVGS:
    if d.name in ('PUNCH_LIST_CHECKLIST.md', 'CHANGELOG-internal-review-v1.0-to-production-v1.0.md'): continue
    low = scan_text(vis(d.read_text()) if d.suffix == '.svg' else d.read_text())
    for b in banned_hits(low): fail('B', f"banned phrase '{b}' in {rel(d)}")
COUNT['B'] = f"{len(BANNED)} phrases across {len(SCAN)+len(SVGS)} files"
# ---------- ranking and 'significant'
RANK = re.compile(r'\b(highest|lowest|largest|smallest|most|least|worst|best|top|rank|ranks|ranked|ranking|outranks?|first place|second place)\b', re.I)
RANK_OK = re.compile(r'not ranked|do not rank|does not rank|never rank|rank numbers|ranking language|not a ranking|or any ordering|implies no ranking|implied ranking|"highest", "lowest"|"highest/lowest"|ranks #1|rank it|top-coded', re.I)
nk = 0
for d in SCAN + SVGS:
    if d.name in ('PUNCH_LIST_CHECKLIST.md', 'CHANGELOG-internal-review-v1.0-to-production-v1.0.md'): continue
    t = re.sub(r'## Do not say\n.*?(?=\n## |\Z)', '', vis(d.read_text()) if d.suffix == '.svg' else d.read_text(), flags=re.S)
    t = re.sub(r'`[^`]*`', ' ', t)
    for sent in re.split(r'(?<=[.!?:])\s+|\n', t):
        if RANK.search(sent) and not RANK_OK.search(sent): nk += 1; fail('K', f"ranking word in {rel(d)}: {sent.strip()[:140]}")
        if re.search(r'\bsignifican', sent, re.I): nk += 1; fail('K', f"'significant' wording in {rel(d)}: {sent.strip()[:140]}")
COUNT['K'] = f"ranking/significance audit over {len(SCAN)+len(SVGS)} files (sentence level)"
# ---------- Boise
BOISE_OK = ['Boise PUMA region', 'Boise is reported as the', 'source `name` value "Boise"', '"Boise", "Boise metro"']
ng = 0
for d in SCAN + SVGS + [P/'web'/'web-metadata.json', P/'web'/'jsonld-dataset.json', P/'web'/'jsonld-scholarlyarticle.json', P/'archive-prep'/'.zenodo.json', P/'data'/'study_areas.csv', P/'charts'/'specs'/'chart-specs.json'] + sorted((P/'charts'/'data').glob('*.csv')):
    if d.name in ('PUNCH_LIST_CHECKLIST.md', 'CHANGELOG-internal-review-v1.0-to-production-v1.0.md'): continue
    t = d.read_text()
    for ok in BOISE_OK: t = t.replace(ok, '')
    if d.name == 'study_areas.csv': t = '\n'.join(','.join(r[:-1]) for r in csv.reader(t.splitlines()))  # last column = unchanged source label (documented)
    for m in re.finditer(r'Boise', t): ng += 1; fail('G', f"bare 'Boise' in {rel(d)}: ...{t[max(0,m.start()-40):m.end()+30]}...")
COUNT['G'] = "Boise label scan over documents, charts, chart data, metadata"
# ---------- license
LIC_REQ = [rep_p] + FS + [P/'methodology'/'methodology-v1.0.md', P/'data'/'DATA_DICTIONARY.md', P/'citation'/'how-to-cite.md', P/'citation'/'attribution.md', P/'web'/'web-metadata.md', P/'README.md', P/'LICENSE.md',
           P/'media'/'research-summary.md', P/'media'/'national-announcement.md', P/'media'/'research-media-fact-sheet.md', P/'disclosures'/'limitations-and-disclosures.md']
for d in LIC_REQ:
    if not d.exists(): fail('L', f"missing file {rel(d)}"); continue
    if CC not in d.read_text(): fail('L', f"'{CC}' missing in {rel(d)}")
for d in SCAN + [P/'web'/'web-metadata.json', P/'citation'/'CITATION.cff', P/'citation'/'citation.bib', P/'archive-prep'/'.zenodo.json']:
    if d.name in ('PUNCH_LIST_CHECKLIST.md', 'CHANGELOG-internal-review-v1.0-to-production-v1.0.md'): continue
    t = d.read_text()
    if re.search(r'CC BY 4\.0|CC BY(?!-SA)\b|CC-BY-4\.0|"cc-by-4\.0"|to be confirmed|\bTBC\b|proposed CC|\[PERMANENT URL TO BE ASSIGNED\]', t): fail('L', f"superseded license or URL placeholder in {rel(d)}")
if 'license: CC-BY-SA-4.0' not in (P/'citation'/'CITATION.cff').read_text(): fail('L', 'CITATION.cff license')
if json.load(open(P/'archive-prep'/'.zenodo.json'))['license'] != 'cc-by-sa-4.0': fail('L', '.zenodo.json license')
for j in ('jsonld-dataset.json', 'jsonld-scholarlyarticle.json'):
    if json.load(open(P/'web'/j))['license'] != CC_URL: fail('L', f'{j} license')
if 'pending ownership and dependency review' not in (P/'code'/'LICENSE').read_text().lower(): fail('L', 'MIT LICENSE not marked pending')
COUNT['L'] = f"{len(LIC_REQ)} files require {CC}; superseded-license scan"
# ---------- study period, version, status labels, not-measured, published claims
PUBL = re.compile(r'has been published|is now published|now available|has published|was published|newly published|is published', re.I)
for d in MD:
    t = d.read_text()
    if re.search(r'2020-2024|five-year|5 year\b', re.sub(r'https?://\S+', ' ', t)): fail('P', f"inconsistent study-period wording in {rel(d)}")
    if d.parent.name in ('report','fact-sheets','methodology','media','local-briefs','disclosures','web') and STUDY not in t: fail('P', f"'{STUDY}' missing in {rel(d)}")
    if d.parent.name != 'reference' and EDITION not in t and d.parent.name not in ('charts',): fail('M', f"'{EDITION}' missing in {rel(d)}")
    if d.parent.name in ('media','local-briefs'):
        if MEDIA_LOCK not in t: fail('M', f"'{MEDIA_LOCK}' missing in {rel(d)}")
    elif d.parent.name not in ('charts',) and LOCK not in t: fail('M', f"content-locked label missing in {rel(d)}")
    if PUBL.search(scan_text(t).replace('that the report "has been published"', '')): fail('M', f"'published' claim in {rel(d)}")
for d in [rep_p] + FS + sorted((P/'media').rglob('*.md')):
    if NOT_MEASURED not in d.read_text(): fail('M', f"not-measured disclosure missing in {rel(d)}")
COUNT['P/M'] = "study period, edition, status label, not-measured disclosure and 'published' scan"
# ---------- Tampa
head = rep.split('## Results by study area')[0]
if 'Tampa' in re.sub(r'Study areas: [^\n]*', '', head): fail('T', 'Tampa appears in report headline sections')
for d in sorted((P/'media').rglob('*.md')):
    t = d.read_text()
    for l in t.split('\n'):
        if l.startswith(('**Proposed headline', '**Proposed subhead', '# ')) and 'Tampa' in l and 'brief' not in d.name: fail('T', f"Tampa in a media headline: {rel(d)}")
    if d.name.startswith('08-tampa') and re.search(r'higher than|other seven|0\.093', t): fail('T', 'Tampa brief uses the borderline comparison')
    if 'brief' in d.name and re.search(r'than the other seven|other seven areas combined \(|Holm', t): fail('T', f"comparison hook in {rel(d)}")
if 'borderline' not in rep.lower() or '0.093' not in rep: fail('T', 'Tampa borderline disclosure missing from report body')
if 'borderline' not in (P/'fact-sheets'/f"{fs_name(IDS.index('tampa'),'tampa')}.md").read_text(): fail('T', 'Tampa fact sheet lacks borderline note')
# ---------- headline framing
H = {r['figure_id']: r['value'] for r in csv.DictReader(open(D/'headline_figures.csv'))}
JT = {r['area_id']: r for r in csv.DictReader(open(D/'joint_estimates.csv'))}[TOT]; WT = {r['area_id']: r for r in csv.DictReader(open(D/'with_without_contrast.csv'))}[TOT]
STT = {r['area_id']: r for r in csv.DictReader(open(D/'with_without_std.csv'))}[TOT]; PVW = {r['area_id']: r for r in csv.DictReader(open(D/'part_vs_whole.csv'))}[TOT]
glance = rep.split('## At a glance')[1].split('## Summary')[0]
for e in [f"{int(JT['older_amb_noveh']):,}", f"±{int(JT['older_amb_noveh_moe90']):,}", f"{round(float(WT['share_with_amb_in_noveh_hh_pct']),1):.1f}%", f"{round(float(WT['share_without_amb_in_noveh_hh_pct']),1):.1f}%",
          f"{float(STT['std_share_with_pct']):.2f}%", f"{float(STT['std_share_without_pct']):.2f}%", f"{float(STT['std_ratio']):.2f}"]:
    if e not in glance: fail('H', f"headline value {e} not in 'At a glance'")
if 'about three times' not in glance or not (2.85 <= float(WT['ratio_with_to_without']) < 3.15): fail('H', "'about three times' does not match the CSV ratio")
if f"about {float(H['std_ratio_rounded_half']):g} times" not in glance: fail('H', 'rounded age-adjusted ratio missing')
for pv_ in (f"{float(PVW['crude_share_older_in_noveh_hh_pct']):.2f}%", f"{float(PVW['crude_ratio']):.2f}", f"{float(PVW['std_ratio']):.2f} "):
    if pv_ in head: fail('H', f"part-vs-whole value {pv_} in headline sections")
for d in sorted((P/'media').rglob('*.md')):
    if f"{float(PVW['crude_share_older_in_noveh_hh_pct']):.2f}%" in d.read_text() or 'twice' in d.read_text().split('## Do not say')[0]: fail('H', f"part-vs-whole figure in media item {rel(d)}")
# ---------- statistical disclosures
meth = (P/'methodology'/'methodology-v1.0.md').read_text()
for need in ('successive-difference replicate', '1.645', '90% confidence', 'Holm step-down', 'familywise error rate 10%', 'Direct standardization', 'not pre-registered', '0.093', 'period averages',
             '45b296ccf1efecf7d76e64960129c67094d910ef1e4d38a5ada9d5c94099751c', 'fc628ae21e2c4e692033b2d817b684a9d1c63255eb5e5ca91b3b81d29aa84ca2', DOI_PH, URL, 'smaller by construction', 'not adjusted for multiple comparisons'):
    if need not in meth: fail('S', f"methodology missing: {need}")
for need in ('successive-difference replicate', '90% margin', 'Holm', '10% familywise', 'direct standardization', 'not pre-registered'):
    if need.lower() not in rep.lower(): fail('S', f"report missing: {need}")
for fsp in FS:
    t = fsp.read_text()
    for need in ('not pre-registered', 'Holm', '10% familywise', 'direct standardization', 'period averages', DOI_PH, URL):
        if need not in t: fail('S', f"{fsp.name} missing: {need}")
# ---------- DOCX, JSON, HTML
try:
    import docx
    nd = 0
    for x in sorted(P.rglob('*.docx')):
        d = docx.Document(str(x)); nd += 1
        txt = '\n'.join(p.text for p in d.paragraphs) + '\n'.join(c.text for t in d.tables for r in t.rows for c in r.cells)
        hdr = d.sections[0].header.paragraphs[0].text
        if not (LOCK in hdr or MEDIA_LOCK in hdr) or EDITION not in hdr: fail('X', f"DOCX header label missing in {rel(x)}")
        mdt = x.with_suffix('.md').read_text() if x.with_suffix('.md').exists() else ''
        for item in dont_say_items(mdt): txt = txt.replace(re.sub(r'[*`]', '', item), ' ')
        for b in banned_hits(scan_text(txt)): fail('X', f"banned phrase '{b}' in {rel(x)}")
        if mdt:
            md_nums = sorted(numbers('\n'.join(l for l in mdt.split('\n') if not l.startswith('![')))); dx_nums = sorted(numbers(txt))
            if md_nums != dx_nums: fail('X', f"DOCX numbers differ from Markdown source in {rel(x)}")
    COUNT['X'] = f"{nd} DOCX files: header label, banned phrases, numbers identical to Markdown source"
except ImportError: fail('X', 'python-docx not available')
for j in list(P.rglob('*.json')) + [P/'archive-prep'/'.zenodo.json']: json.load(open(j))
for h in P.rglob('*.html'):
    for img in re.findall(r'<img[^>]*>', h.read_text()):
        if not re.search(r'alt="[^"]{20,}"', img): fail('X', f"img without alt text in {rel(h)}")
LOG += [f"{k}: {v}" for k, v in COUNT.items()]
LOG.append('RESULT: ' + ('PASS' if not FAIL else f'FAIL ({len(FAIL)} issues)'))
out = '\n'.join(LOG + FAIL) + '\n'
if (P/'logs').exists(): (P/'logs'/'consistency-report.txt').write_text(out)
print(out); sys.exit(1 if FAIL else 0)
