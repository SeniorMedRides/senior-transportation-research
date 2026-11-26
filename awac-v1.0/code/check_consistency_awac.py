#!/usr/bin/env python3
"""Aging Without a Car run v1: extension of the Version 1.0 consistency checker (code/v1_0_publication/check_consistency.py, unchanged copy).
The Version 1.0 checker is tied to the Version 1.0 package layout, so its rules are applied here to this run's documents:
 B  the Version 1.0 "do not say" list (30 phrases, read from the v1.0 checker source, not retyped) with its negated-disclosure handling
 A  phrases added by SAP s.9: lonely, stuck at home, can't drive, cannot drive, and wording that turns independent living difficulty into missed appointments
 W  "without a car" only in the title "Aging Without a Car"
 K  v1.0 ranking and 'significant' audit (sentence level)
 G  'Boise' only as 'Boise PUMA region'
 P  study period wording 'ACS 2020–2024 5-year'; no hyphen-minus year range or 'five-year'
 N  every statistic-like number in the summary and web items exists in this run's output CSVs or the Version 1.0 data CSVs (v1.0 number rules)
 M  not-measured statement and independent-living line appear with the lead finding; internal status label present
 R  tiers (s.7) recomputed independently from n and CV in every output CSV; display columns follow the tier
 F  F1/F2: Holm at 10% recomputed independently; borderline iff remains and adjusted p > 0.05; wording follows s.6; thin-area rule applied
 L  lead finding matches the s.9 template and rules (CV <= 10%, k rounded to nearest half, F2 not borderline, no area names)
 U  web items: URLs and slugs per s.10; meta descriptions <= 160 characters; no banned phrasing
 H  (run v1.2) David's fragility rule: fragile iff the result remains and is borderline under S1 or S2, fails under S2, or has S1 Holm-adjusted p in 0.04-0.05;
    fragile results kept out of headlines and local summaries; only the eight-area lead is headline-eligible; F1 fragile set must equal the four David named;
    local summaries for every non-fragile remaining F1 area; that set must equal Sacramento, Tampa (4:40 PM) and Phoenix (confirmed 5:38 PM);
    S2 note stated beside each tested result (outputs) and beside each F1 row in the summary; excluded comparisons absent from lead and web items
 C  (run v1.1) difference/ratio n and CV columns present in T5, T8, F1, F2 and equal to the smaller component n / larger component CV
Usage: python3 check_consistency_awac.py   (exit 0 only if every check passes; writes logs/consistency-report-awac.txt)"""
import ast, csv, re, json, math, pathlib, glob
C = pathlib.Path(__file__).resolve().parent; RUN = C.parent; O = RUN/'outputs'; V10 = RUN/'v1_0_1_data'   # bundled Version 1.0.1 data (run v1.1; was an absolute path in run v1)
FAIL = []; LOG = []
def fail(code, m): FAIL.append(f'[{code}] {m}')
src = (C/'v1_0_publication'/'check_consistency.py').read_text(); tree = ast.parse(src)
def literal(name):
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and any(getattr(t,'id',None)==name for t in n.targets): return ast.literal_eval(n.value)
BANNED = literal('BANNED'); WHITELIST_V10 = literal('WHITELIST')
assert len(BANNED) == 30, len(BANNED)
RANK = re.compile(r'\b(highest|lowest|largest|smallest|most|least|worst|best|top|rank|ranks|ranked|ranking|outranks?|first place|second place)\b', re.I)
RANK_OK = re.compile(r'not ranked|do not rank|does not rank|never rank|ranking language|not a ranking|implies no ranking|implied ranking', re.I)
ADDED = ['lonely', 'stuck at home', "can't drive", 'cannot drive', 'miss appointments', 'missing appointments', 'missed doctor', 'miss doctor', 'skip appointments', 'skipped appointments']
NOT_MEASURED = 'These estimates do not directly measure missed medical appointments, transportation demand, wheelchair use, or unmet transportation needs.'
RES = json.load(open(O/'run_results.json')); LEAD = RES['lead']; ILD = LEAD['independent_living_line']
NEGATED = [NOT_MEASURED, ILD]
SUMMARY = RUN/'docs'/'technical-summary-methods-results-run-v1.2.md'
WEBJ = [RUN/'web-data'/'area-pages.json', RUN/'web-data'/'report-page.json']
def web_texts():
    out = []
    for j in WEBJ:
        d = json.load(open(j)); d = d if isinstance(d, list) else [d]
        for x in d:
            for k in ('page_title','meta_description','city_page_local_research_line','city_page_qualifier_line','title'):
                if k in x: out.append((f'{j.name}:{x.get("area_id","report")}:{k}', x[k]))
    return out
DOCS = [(SUMMARY.name, SUMMARY.read_text())] + web_texts()
def scan(t):
    for x in NEGATED: t = t.replace(x, ' ')
    return t.lower()
def hits(low, words): return [b for b in words if re.search((r'(?<![\w#])' if b[0].isalnum() else '') + re.escape(b) + (r'(?!\w)' if b[-1].isalnum() else ''), low)]
# B, A, W, K, G, P
for name, t in DOCS:
    low = scan(t)
    for b in hits(low, BANNED): fail('B', f"v1.0 banned phrase '{b}' in {name}")
    for b in hits(low, ADDED): fail('A', f"added banned phrase '{b}' in {name}")
    if 'without a car' in re.sub(r'aging without a car', ' ', low): fail('W', f"'without a car' outside the title in {name}")
    body = re.sub(r'`[^`]*`', ' ', t)
    for sent in re.split(r'(?<=[.!?:])\s+|\n', body):
        if RANK.search(sent) and not RANK_OK.search(sent): fail('K', f'ranking word in {name}: {sent.strip()[:120]}')
        if re.search(r'\bsignifican', sent, re.I): fail('K', f"'significant' in {name}: {sent.strip()[:120]}")
    for m in re.finditer(r'Boise', t.replace('Boise PUMA region','')): fail('G', f"bare 'Boise' in {name}")
    if re.search(r'2020-2024|five-year|5 year\b', re.sub(r'https?://\S+', ' ', t)): fail('P', f'study-period wording in {name}')
if 'ACS 2020–2024 5-year' not in SUMMARY.read_text(): fail('P', 'study period missing in summary')
LOG.append(f'B/A/W/K/G/P: {len(BANNED)} v1.0 phrases + {len(ADDED)} added phrases over {len(DOCS)} texts')
# N numbers
allowed = set()
def add(v):
    v = v.strip()
    if not v: return
    allowed.add(v.lstrip('+-'))
    try: x = abs(float(v))
    except ValueError: return
    for s in (f'{x:.2f}', f'{x:.1f}', f'{x:.0f}', f'{x:,.0f}', f'{x:.3g}', f'{x:g}', f'{x:,.2f}', f'{x:.4f}'): allowed.add(s)
    if x == int(x): allowed.add(f'{int(x):,}')
for f in list(O.glob('*.csv')) + list(V10.glob('*.csv')):
    for r in csv.reader(open(f, newline='')):
        for cell in r:
            for tok in re.split(r'[;| ]', cell): add(tok)
for v in json.dumps(RES).replace('"',' ').replace(',',' ').split(): add(v.strip('{}[]:'))
WL = set(WHITELIST_V10) | {'16','17','2015','2019','0.10','0.005','150','149','99','501','0.0','12','13','14','6','4','0.27','0.29'}
NUM = re.compile(r'(?<![\w.\-])(?:n=)?[−+\-]?(?:\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+\.\d+(?:e-\d+)?|\d+(?=%)|(?<=±)\d+|\d{3,})(?![\w])')
nn = 0
for name, t in DOCS:
    t2 = re.sub(r'https?://\S+', ' ', t); t2 = re.sub(r'`[^`]*`', ' ', t2); t2 = re.sub(r'\b20\d\d-\d\d-\d\d\b|\d+ November 2026', ' ', t2)
    for m in NUM.finditer(t2):
        tok = m.group(0).lstrip('−+-')
        if re.fullmatch(r'20\d\d', tok) or tok in WL: continue
        nn += 1
        if tok not in allowed: fail('N', f'number not in output data: {tok} in {name}')
LOG.append(f'N: {nn} numbers checked against {len(list(O.glob("*.csv")))} output CSVs and the Version 1.0 data CSVs')
# M
s = SUMMARY.read_text(); lead_sec = s.split('## 3. Lead finding')[1].split('## 4.')[0]
for need in (NOT_MEASURED, ILD, LEAD['sentence1']): 
    if need not in lead_sec: fail('M', f'lead section missing: {need[:60]}')
if 'INTERNAL TECHNICAL SUMMARY — not a public report draft' not in s: fail('M', 'status label missing')
# R tiers
def tier(n, cv):
    if n == 0 or n < 30 or cv is None or cv > 0.50: return 'Suppressed'
    if n < 50 or cv > 0.30: return 'Indicative'
    return 'Reported'
nt = 0
for f in sorted(O.glob('*.csv')):
    for r in csv.DictReader(open(f)):
        for k, v in r.items():
            if not k.endswith('_tier') or v == '': continue
            pre = k[:-5]
            if pre+'_unweighted_n' in r and pre+'_cv' in r:
                cvv = float(r[pre+'_cv']) if r[pre+'_cv'] not in ('', 'None') else None
                # recompute with 4-decimal CV (thresholds are at 2 decimals so rounding cannot move a tier unless CV sits exactly at a boundary)
                if tier(int(r[pre+'_unweighted_n']), cvv) != v: fail('R', f'{f.name} {r.get("area_id")} {k}: {v} vs recomputed')
                nt += 1
            for dk in [x for x in r if x.endswith('_display') and (x[:-8] in (pre, pre+'_pct'))]:
                d = r[dk]
                if v == 'Suppressed' and d != '— (sample too small)': fail('R', f'{f.name} {dk} suppressed but shown')
                if v == 'Indicative' and 'indicative only; do not quote on its own' not in d: fail('R', f'{f.name} {dk} indicative label missing')
                if v not in ('Reported','Indicative','Suppressed'): fail('R', f'unknown tier {v}')
LOG.append(f'R: {nt} tier assignments recomputed from n and CV')
# Suppressed values must not be quoted in the summary
for r in csv.DictReader(open(O/'t3_profile_no_vehicle_vs_with_vehicle.csv')):
    if r['share_tier'] == 'Suppressed' and re.search(rf'(?<![\d.]){re.escape(f"{float(r["share_pct"]):.2f}")}%', s): fail('R', f'suppressed value {r["share_pct"]} quoted in summary')
# F tests
def holm(ps, alpha):
    m = len(ps); order = sorted(range(m), key=lambda i: ps[i]); res = [False]*m; adj = [0]*m; prev = 0; stop = False
    for rank, i in enumerate(order):
        a = min(1.0, max(prev, (m-rank)*ps[i])); prev = a; adj[i] = a
        if not stop and ps[i] <= alpha/(m-rank): res[i] = True
        else: stop = True
    return res, adj
elig = json.load(open(RUN/'logs'/'eligibility-fixed-before-tests.json'))
for fam, f, n_expected in (('F1','f1_tests_area_vs_other_seven.csv',8), ('F2','f2_tests_living_alone_vs_not.csv',9)):
    rows = list(csv.DictReader(open(O/f)))
    if len(rows) != n_expected: fail('F', f'{fam}: {len(rows)} rows, expected {n_expected}')
    tested = [r for r in rows if r.get('p')]
    if {r['area_id'] for r in tested} != {a for a,v in elig[fam].items() if v}: fail('F', f'{fam}: tested set differs from counts-only eligibility')
    z = [float(r['z']) for r in tested]
    ps = [float(r['p']) for r in tested]
    res, adj = holm(ps, 0.10)
    for r, ok, a in zip(tested, res, adj):
        if (r['remains_after_holm_10pct'] == 'True') != ok: fail('F', f'{fam} {r["area_id"]}: Holm result differs on recomputation')
        bl = ok and float(r['holm_adjusted_p']) > 0.05
        if (r['borderline'] == 'True') != bl: fail('F', f'{fam} {r["area_id"]}: borderline flag')
        est = float(r['estimate_pp'])
        if fam == 'F1':
            want = (('higher' if est > 0 else 'lower') + ' than the other seven combined') if ok else 'not distinguishable from the other seven combined'
        else:
            want = ('no-vehicle share higher' if est > 0 else 'no-vehicle share lower') if ok else 'not distinguishable'
        if not r['wording'].startswith(want): fail('F', f'{fam} {r["area_id"]}: wording "{r["wording"]}"')
        if bl and 'borderline' not in r['wording']: fail('F', f'{fam} {r["area_id"]}: borderline label missing')
    for r in rows:
        if not r.get('p') and r['wording'] != 'not tested: sample too small': fail('F', f'{fam} {r["area_id"]}: untested wording')
LOG.append('F: Holm (10%), borderline and wording recomputed for F1 and F2')
# L lead
t4 = {(r['area_id'], r['age_group']): r for r in csv.DictReader(open(O/'t4_living_alone_no_vehicle.csv'))}[('eight_area_total','65_plus')]
if float(t4['lives_alone_no_vehicle_cv']) > 0.10: fail('L', 'T4 CV > 10% but T4 used')
exp1 = f"An estimated {int(t4['lives_alone_no_vehicle']):,} people 65 and older in eight U.S. study areas live alone in a household with no vehicle. Among older adults without a vehicle, {round(float(t4['share_of_no_vehicle_65plus_living_alone_pct']),1):.1f}% live alone."
if LEAD['sentence1'] != exp1: fail('L', 'sentence 1 does not match template')
f2t = [r for r in csv.DictReader(open(O/'f2_tests_living_alone_vs_not.csv')) if r['area_id']=='eight_area_total'][0]
t5 = [r for r in csv.DictReader(open(O/'t5_no_vehicle_living_alone_vs_not.csv')) if r['area_id']=='eight_area_total'][0]
if f2t['remains_after_holm_10pct'] == 'True' and f2t['borderline'] != 'True':
    k1 = math.floor(float(t5['crude_ratio'])*2+0.5)/2; k2 = math.floor(float(t5['std_ratio'])*2+0.5)/2
    if f'about {k1:g} times as likely to have no household vehicle as those who live with others, about {k2:g} times after adjusting for age.' not in LEAD['sentence2']: fail('L', 'sentence 2 k values')
else:
    if 'times as likely' in LEAD['sentence2']: fail('L', 'ratio sentence used although F2 does not qualify')
AREAS = ['Boise','Las Vegas','Orlando','Phoenix','Sacramento','Salt Lake','Stockton','Tampa']
if any(a in LEAD['sentence1'] + LEAD['sentence2'] for a in AREAS): fail('L', 'area named in lead')
LOG.append('L: lead finding rule and template verified')
# U web
SLUG = {'boise':'boise-puma-region','las_vegas':'las-vegas','orlando':'orlando','phoenix':'phoenix','sacramento':'sacramento','salt_lake_city':'salt-lake-city','stockton':'stockton','tampa':'tampa'}
CITY = {'boise':'boise-id','las_vegas':'las-vegas-nv','orlando':'orlando-fl','phoenix':'phoenix-az','sacramento':'sacramento-ca','salt_lake_city':'salt-lake-city-ut','stockton':'stockton-ca','tampa':'tampa-fl'}
items = json.load(open(WEBJ[0])); rep = json.load(open(WEBJ[1]))
if rep['report_url'] != 'https://seniormedrides.com/research/aging-without-a-car/' or len(rep['meta_description']) > 160: fail('U', 'report page item')
for x in items:
    a = x['area_id']
    if x['area_page_url'] != f'https://seniormedrides.com/research/aging-without-a-car/{SLUG[a]}/' or x['city_page_url'] != f'https://seniormedrides.com/{CITY[a]}/' or x['canonical_url'] != x['area_page_url']: fail('U', f'{a}: URL')
    if len(x['meta_description']) > 160: fail('U', f'{a}: meta description {len(x["meta_description"])} chars')
    if x['up_link_report'] != rep['report_url']: fail('U', f'{a}: up link')
if len(items) != 8: fail('U', 'expected 8 area items')
LOG.append(f'U: {len(items)} area items + report item')
# H headline/local-summary rule (run v1.2: David P. Faustina's fragility rule, 14 Nov 2026, 4:40 PM; replaces the v1.1 Orlando-only list)
NEAR_CUT_LOW, CUT = 0.04, 0.05
DAVID_FRAGILE_NAMED = {'boise','las_vegas','orlando','stockton'}; DAVID_LOCAL_NAMED = {'phoenix','sacramento','tampa'}
sens = {(r['family'], r['area_id']): r for r in csv.DictReader(open(O/'sens2_f1_f2_standard_S2.csv'))}
excluded_f1 = set(); fragile = {'F1': set(), 'F2': set()}; local_ok = {'F1': set(), 'F2': set()}
for fam, f in (('F1','f1_tests_area_vs_other_seven.csv'), ('F2','f2_tests_living_alone_vs_not.csv')):
    for r in csv.DictReader(open(O/f)):
        if not r.get('p'): continue
        sv = sens[(fam, r['area_id'])]; remains = r['remains_after_holm_10pct']=='True'; p_adj = float(r['holm_adjusted_p'])
        want = remains and (r['borderline']=='True' or sv['primary_conclusion_changes']=='True' or 'borderline' in sv['S2_result'] or NEAR_CUT_LOW <= p_adj <= CUT)
        if (r.get('fragile') == 'True') != want: fail('H', f'{fam} {r["area_id"]}: fragility flag')
        if want and not r.get('fragility_reason'): fail('H', f'{fam} {r["area_id"]}: fragility reason missing')
        if (r.get('headline_local_summary_eligible') == 'False') != want: fail('H', f'{fam} {r["area_id"]}: headline/local-summary eligibility')
        if 'pending' in (r.get('headline_local_summary_exclusion_reason','') + r.get('local_summary_claim','')).lower(): fail('H', f'{fam} {r["area_id"]}: stale pending-David marker')
        hl_want = fam == 'F2' and r['area_id'] == 'eight_area_total' and remains and not want
        if (r.get('headline_eligible') == 'True') != hl_want: fail('H', f'{fam} {r["area_id"]}: headline eligibility (only the pre-specified eight-area lead)')
        ls_want = remains and not want and r['area_id'] != 'eight_area_total'
        if (r.get('local_summary_eligible') == 'True') != ls_want: fail('H', f'{fam} {r["area_id"]}: local-summary eligibility')
        if not ls_want and not r.get('local_summary_claim','').startswith(('none', 'not applicable')): fail('H', f'{fam} {r["area_id"]}: local-summary claim made')
        note = r.get('s2_sensitivity_note', '')
        if sv['primary_conclusion_changes']=='True' and 'changes' not in note: fail('H', f'{fam} {r["area_id"]}: S2 change not stated beside result')
        if sv['primary_conclusion_changes']!='True' and sv['borderline_status_changes']=='True' and 'borderline' not in note: fail('H', f'{fam} {r["area_id"]}: S2 borderline not stated')
        if not note: fail('H', f'{fam} {r["area_id"]}: S2 note missing')
        if want: fragile[fam].add(r['area_id'])
        if ls_want: local_ok[fam].add(r['area_id'])
        if ls_want and r.get('local_summary_claim') != r['wording']: fail('H', f'{fam} {r["area_id"]}: local-summary claim differs from the result wording')
        if fam=='F1' and want: excluded_f1.add(r['area_id'])
if fragile['F1'] != DAVID_FRAGILE_NAMED: fail('H', f'fragile F1 set {sorted(fragile["F1"])} differs from the four areas David named')
if local_ok['F1'] != DAVID_LOCAL_NAMED: fail('H', f'local-summary F1 set {sorted(local_ok["F1"])} differs from Phoenix, Sacramento and Tampa')
NAMES = {r['area_id']: r['area'] for r in csv.DictReader(open(O/'t6_std_living_alone_no_vehicle_share.csv'))}
f1sec = s.split('**T6 and F1.')[1].split('**F2.')[0]
for a, nm in NAMES.items():
    if a == 'eight_area_total': continue
    row = next((l for l in f1sec.split('\n') if l.startswith(f'| {nm} |')), '')
    if 'S2' not in row: fail('H', f'summary F1 row for {nm} lacks the S2 result beside it')
    if a in excluded_f1 and 'not for headlines or local summaries' not in row: fail('H', f'summary F1 row for {nm} lacks the headline/local-summary exclusion')
    if a not in excluded_f1 and 'not for headlines or local summaries' in row: fail('H', f'summary F1 row for {nm} wrongly excluded')
if 'Yes, Phoenix may appear in its local summary.' not in s or 'pending David' in s: fail('H', "David's 5:38 PM Phoenix decision not recorded verbatim, or a stale pending-David marker in the summary")
if 'Leave Boise PUMA region and Stockton out of headlines and local summaries too.' not in s: fail('H', "David's rule not stated verbatim in the summary")
for x in json.load(open(WEBJ[0])):
    a = x['area_id']; txt = ' '.join(str(x.get(k,'')) for k in ('meta_description','city_page_local_research_line','city_page_qualifier_line','page_title'))
    if 'other seven' in txt and a in excluded_f1: fail('H', f'web item {a} uses an excluded F1 comparison')
    if (a in excluded_f1) != (x.get('f1_comparison_headline_local_summary') == 'excluded') or x.get('f1_fragile') != (a in fragile['F1']): fail('H', f'web item {a}: F1 exclusion status')
    if x.get('f1_headline_eligible') is not False: fail('H', f'web item {a}: area F1 result marked headline-eligible')
    if x.get('f1_local_summary_eligible') != (a in local_ok['F1']): fail('H', f'web item {a}: local-summary eligibility')
    if 'f1_pending_david' in x or 'pending' in str(x.get('f1_exclusion_reason','')).lower(): fail('H', f'web item {a}: stale pending-David field')
if any(nm.split()[0] in LEAD['sentence1'] + LEAD['sentence2'] for a, nm in NAMES.items() if a != 'eight_area_total') or 'other seven' in LEAD['sentence1'] + LEAD['sentence2']: fail('H', 'area result in headline lead')
LOG.append(f'H: fragility rule recomputed (F1 fragile: {", ".join(sorted(fragile["F1"]))}; F1 local-summary eligible: {", ".join(sorted(local_ok["F1"]))}; F2 fragile: {", ".join(sorted(fragile["F2"])) or "none"}); headlines use only the eight-area lead')
# C carried n/CV (run v1.1)
def chk_carry(f, pairs):
    for r in csv.DictReader(open(O/f)):
        if not r.get(pairs[0][0]) and f.startswith('f'): 
            if not r.get('p'): continue
        for tgt, comps in pairs:
            ns = [int(r[c+'_unweighted_n']) for c in comps]; cs = [float(r[c+'_cv']) for c in comps]
            if r.get(tgt+'_unweighted_n') in (None, '') or int(r[tgt+'_unweighted_n']) != min(ns) or abs(float(r[tgt+'_cv']) - max(cs)) > 1e-12: fail('C', f'{f} {r["area_id"]} {tgt}: carried n/CV')
chk_carry('t5_no_vehicle_living_alone_vs_not.csv', [('crude_diff_ratio', ['crude_share_no_vehicle_living_alone','crude_share_no_vehicle_not_living_alone']),
                                                   ('std_diff_ratio', ['std_share_no_vehicle_living_alone','std_share_no_vehicle_not_living_alone'])])
chk_carry('t8_independent_living_difficulty_by_vehicle.csv', [('diff', ['independent_living_difficulty_no_vehicle','independent_living_difficulty_with_vehicle'])])
chk_carry('f1_tests_area_vs_other_seven.csv', [('difference', ['area_std_share','other_seven_std_share'])])
chk_carry('f2_tests_living_alone_vs_not.csv', [('difference', ['living_alone_std_share','not_living_alone_std_share'])])
LOG.append('C: carried n/CV columns verified in T5, T8, F1, F2')
LOG.append('RESULT: ' + ('PASS' if not FAIL else f'FAIL ({len(FAIL)} issues)'))
out = '\n'.join(LOG + FAIL) + '\n'; (RUN/'logs'/'consistency-report-awac.txt').write_text(out); print(out)
raise SystemExit(1 if FAIL else 0)
