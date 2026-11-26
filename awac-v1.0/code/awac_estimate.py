#!/usr/bin/env python3
"""Aging Without a Car — estimation run under the locked Statistical Analysis Plan (Gate 1, approved 13 Nov 2026).
Code version: awac-run-1.2.0 (run v1.1: validator-note fixes; run v1.2: David's fragility reporting rule; no change to any estimate, MOE, test result or tier). INTERNAL; not for publication.

Reuses, unchanged, the Version 1.0 estimation code (byte-identical copies in code/v1_0_analysis/):
  estimate_joint.py   -> STATES, AREAS (v1.0 order), geography, open_csv_in_zip, se()  [SDR SE = sqrt(4/80*sum((Xr-X)^2))]
  age_sensitivity.py  -> GROUPS (65_74, 75_84, 85_plus), age_group(), vadd/vsub/vdiv, pval() (two-sided normal), holm() (alpha 0.10)
Universe (SAP s.2): AGEP>=65, person SERIALNO links to a housing record with TYPEHUGQ=='1' in a study-area 2020 PUMA.
Weights: PWGTP + PWGTP1..80 for every estimate. MOE90 = 1.645*SE. Shares/differences/ratios are formed inside each replicate.
Recodes (SAP s.3): SEX 1/2; VEH=='0' no vehicle (1-6 any); NP=='1' living alone; DPHY 1/2; DOUT 1/2; POVPIP 0-99 / 100-149 / 150-501;
  TEN 1-2 owner vs 3-4 renter or occupied without payment of rent.
Run order (SAP s.11): check 1 Version 1.0 reproduction -> check 2 internal sums -> check 3 NP/HHT recode; the script stops at the first failure
and writes no new-study tables. Tiers (s.7) are assigned from n and CV only. Thin-area eligibility for F1/F2 (s.6, s.7) is fixed from
unweighted counts and written to logs before any test statistic is computed.
Usage: python3 awac_estimate.py --inputs DIR [--v10-data DIR]
  --inputs    folder holding pums/csv_[hp]??.zip and tract_puma.txt (verified against code/v1_0_analysis/SHA256SUMS-inputs.txt); or env AWAC_INPUTS
  --v10-data  Version 1.0.1 data folder (default: the bundled ../v1_0_1_data, verified against its SHA256SUMS-v1.0.1-data.txt)"""
import sys, os, csv, json, math, pathlib, collections, datetime, argparse, hashlib
VERSION = 'awac-run-1.2.0'
HERE = pathlib.Path(__file__).resolve().parent; RUN = HERE.parent
sys.path.insert(0, str(HERE/'v1_0_analysis')); sys.path.insert(0, str(HERE/'v1_0_analysis'/'sensitivity'))
import estimate_joint as ej, age_sensitivity as asens
_ap = argparse.ArgumentParser(); _ap.add_argument('--inputs', default=os.environ.get('AWAC_INPUTS')); _ap.add_argument('--v10-data', default=str(RUN/'v1_0_1_data'))
_args = _ap.parse_args()
if not _args.inputs: raise SystemExit('give --inputs DIR (or set AWAC_INPUTS): folder with pums/ and tract_puma.txt')
INPUTS = pathlib.Path(_args.inputs).resolve(); V10 = pathlib.Path(_args.v10_data).resolve()
def _verify(folder, sums):
    bad = [l.split()[1] for l in open(sums) if l.strip() and hashlib.sha256((folder/l.split()[1]).read_bytes()).hexdigest() != l.split()[0]] if sums.exists() else ['(no checksum file)']
    if bad: raise SystemExit(f'checksum mismatch in {folder}: {bad}')
_verify(V10, V10/'SHA256SUMS-v1.0.1-data.txt')
OUT = RUN/'outputs'; LOGD = RUN/'logs'; OUT.mkdir(exist_ok=True); LOGD.mkdir(exist_ok=True)
NR = ej.NREP; R = range(NR+1); G = [g for g,_,_ in asens.GROUPS]
V10_ORDER = [a for a,*_ in ej.AREAS]                      # summation order used by Version 1.0 for eight-area totals
NAME = {r['area_id']: r['display_label'] for r in csv.DictReader(open(V10/'study_areas.csv'))}
ORDER = sorted(V10_ORDER, key=lambda a: NAME[a])               # alphabetical display order (SAP s.2)
TOT = 'eight_area_total'; NAME[TOT] = 'Eight areas combined'
S1_PUBLISHED = {'65_74':0.591331,'75_84':0.305893,'85_plus':0.102776}; S2_PUBLISHED = {'65_74':0.409652,'75_84':0.354223,'85_plus':0.236126}
LOG = []
def log(*a):
    s = ' '.join(str(x) for x in a); LOG.append(s); print(s)
def stop(check, msg):
    log(f'STOP at {check}: {msg}'); (LOGD/'awac-run.log').write_text('\n'.join(LOG)+'\n'); sys.exit(2)
K = collections.namedtuple('K', 'ag sex alone noveh dphy dout pov ten')

# ---------------- geography: Version 1.0 study_areas.csv, cross-checked with the v1.0 geography function
def geography():
    tp = ej.load_tract_puma(INPUTS/'tract_puma.txt'); geo = {}
    sa = {r['area_id']: r for r in csv.DictReader(open(V10/'study_areas.csv'))}
    for aid,_,st,cs in ej.AREAS:
        p = ej.area_geography(tp, st, cs)[0]
        if p != sa[aid]['pumas_2020'].split(';') or st != sa[aid]['state_fips']: stop('geography', f'{aid} PUMAs differ from study_areas.csv')
        geo[aid] = (st, set(p))
    return geo

def povband(v):
    if v == '': return 'NA'
    x = int(v); return 'lt100' if x < 100 else ('100_149' if x < 150 else 'ge150')

def accumulate(st, area_pumas, recode, misc, direct):
    puma_area = {p:a for a,ps in area_pumas.items() for p in ps}
    hu = {a:{} for a in area_pumas}
    z,f = ej.open_csv_in_zip(INPUTS/'pums'/f'csv_h{ej.STATES[st]}.zip', 'psam_h')
    with z,f:
        r = csv.reader(f); h = next(r); ix = {c:h.index(c) for c in ['SERIALNO','PUMA','TYPEHUGQ','VEH','NP','HHT','TEN']}
        for row in r:
            a = puma_area.get(row[ix['PUMA']])
            if a and row[ix['TYPEHUGQ']] == '1': hu[a][row[ix['SERIALNO']]] = (row[ix['VEH']], row[ix['NP']], row[ix['HHT']], row[ix['TEN']])
    cells = {a:collections.defaultdict(lambda: [0.0]*(NR+1)) for a in area_pumas}; n = {a:collections.Counter() for a in area_pumas}
    z,f = ej.open_csv_in_zip(INPUTS/'pums'/f'csv_p{ej.STATES[st]}.zip', 'psam_p')
    with z,f:
        r = csv.reader(f); h = next(r)
        ix = {c:h.index(c) for c in ['SERIALNO','PUMA','AGEP','SEX','DPHY','DOUT','POVPIP','RELSHIPP','PWGTP']}; iw = [h.index(f'PWGTP{i}') for i in range(1,NR+1)]
        for row in r:
            a = puma_area.get(row[ix['PUMA']])
            if not a: continue
            hrec = hu[a].get(row[ix['SERIALNO']])
            if hrec is None or int(row[ix['AGEP']]) < 65: continue      # same universe rule as ej.flags()
            veh, np_, hht, ten = hrec
            if veh not in '0123456' or len(veh) != 1: misc['veh_unexpected'] += 1
            alone = np_ == '1'
            _ag = asens.age_group(int(row[ix['AGEP']]))
            if row[ix['RELSHIPP']] == '20':
                recode['householders'] += 1
                if alone != (hht in ('4','6')): recode['disagree'] += 1; recode['examples'].append((a, row[ix['SERIALNO']], np_, hht))
            elif alone: recode['nonhouseholder_np1'] += 1
            k = K(asens.age_group(int(row[ix['AGEP']])), row[ix['SEX']], alone, veh == '0',
                  row[ix['DPHY']] if row[ix['DPHY']] in ('1','2') else 'NA', row[ix['DOUT']] if row[ix['DOUT']] in ('1','2') else 'NA',
                  povband(row[ix['POVPIP']].strip()), ten if ten in ('1','2','3','4') else 'NA')
            w = [float(row[ix['PWGTP']])]+[float(row[i]) for i in iw]; c = cells[a][k]
            for i in R: c[i] += w[i]
            n[a][k] += 1
            # independent direct accumulators (run v1.1, note N4): keyed on the raw NP and VEH codes, not on the cell key
            for dk in ((_ag, 'np1' if np_ == '1' else 'np2plus'), (_ag, 'veh0' if veh == '0' else 'veh1to6')):
                dv = direct[a][dk]
                for i in R: dv[i] += w[i]
    return cells, n

# ---------------- estimation helpers
CELLS = {}; NCNT = {}
def tot(areas, pred):
    """Weighted count vector and unweighted n over cells matching pred; areas summed in the order given (replicate by replicate)."""
    out = [0.0]*(NR+1); nn = 0
    for a in areas:
        av = [0.0]*(NR+1)
        for k,v in CELLS[a].items():
            if pred(k):
                for i in R: av[i] += v[i]
                nn += NCNT[a][k]
        for i in R: out[i] += av[i]
    return out, nn
def AREAS_OF(aid): return V10_ORDER if aid == TOT else [aid]
def se(v): return ej.se(v)
def moe(v): return 1.645*ej.se(v)
def cv(v):  return (ej.se(v)/abs(v[0])) if v[0] else None

def tier(nn, c):
    """SAP s.7, assigned from n and CV only."""
    if nn == 0 or nn < 30 or c is None or c > 0.50: return 'Suppressed'
    if nn < 50 or c > 0.30: return 'Indicative'
    return 'Reported'
WORST = {'Reported':0,'Indicative':1,'Suppressed':2}
def worst(*ts): return max(ts, key=lambda t: WORST[t])
TIER_NOTE = {'Reported':'', 'Indicative':'indicative only; do not quote on its own', 'Suppressed':'sample too small'}

def count_fields(p, v, nn):
    c = cv(v); t = tier(nn, c)
    return {p: round(v[0]), p+'_moe90': round(moe(v)), p+'_unweighted_n': nn, p+'_cv': (round(c,4) if c is not None else ''), p+'_tier': t}
def share_fields(p, num, den, nn):
    s = asens.vdiv(num, den); c = cv(s); t = tier(nn, c)
    return {p+'_pct': round(100*s[0],2), p+'_moe90_pp': round(100*moe(s),2), p+'_unweighted_n': nn, p+'_cv': (round(c,4) if c is not None else ''), p+'_tier': t}, s, t
def std(shares, S): return [sum(S[g]*shares[g][i] for g in G) for i in R]

SPECIAL_TIER = {'crude_diff_ratio_tier':['crude_diff_pp','crude_ratio'], 'std_diff_ratio_tier':['std_diff_pp','std_ratio'], 'diff_tier':['diff_no_vehicle_minus_with_vehicle_pp']}
def add_display(r):
    """SAP s.7 display rule: Reported as is; Indicative shown with the caution; Suppressed shown as an em dash with 'sample too small'.
    Raw values stay in the CSV for validation only; display columns are what any publication would use."""
    for k in list(r):
        if not k.endswith('_tier'): continue
        pre = k[:-5]; fields = SPECIAL_TIER.get(k) or [f for f in (pre, pre+'_pct') if f in r]
        for f in fields:
            t = r[k]; v = r[f]
            r[f+'_display'] = (f'{v}' if t=='Reported' else (f'{v} (indicative only; do not quote on its own)' if t=='Indicative' else '— (sample too small)'))
    return r
def write_csv(name, rows):
    rows = [add_display(dict(r)) for r in rows]
    keys = list(dict.fromkeys(k for r in rows for k in r))
    with open(OUT/name, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=keys, lineterminator='\n'); w.writeheader(); w.writerows(rows)
    log(f'wrote outputs/{name} ({len(rows)} rows)')

def main():
    log(f'{VERSION} started {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}; Python {sys.version.split()[0]}')
    geo = geography(); DIRECT = {a: collections.defaultdict(lambda: [0.0]*(NR+1)) for a in V10_ORDER}; V10AGE = {}
    recode = collections.Counter(householders=0, disagree=0, nonhouseholder_np1=0); recode['examples'] = []; misc = collections.Counter()
    for st in sorted({g[0] for g in geo.values()}):
        c, nn = accumulate(st, {a:geo[a][1] for a in V10_ORDER if geo[a][0]==st}, recode, misc, DIRECT); CELLS.update(c); NCNT.update(nn)
        e10, _ = asens.accumulate_by_age(INPUTS, st, {a:geo[a][1] for a in V10_ORDER if geo[a][0]==st}); V10AGE.update(e10)   # separate pass, Version 1.0 code
        log(f'state {st}: accumulated (cells, direct accumulators, and a separate Version 1.0 code pass)')
    ALL = lambda k: True
    # ================= CHECK 1: Version 1.0 reproduction (T1, T2, walking-difficulty contrast), exact, MOEs included
    mism = []; ncmp = 0
    def cmp(file, aid, key, field, val):
        nonlocal ncmp; ncmp += 1
        ref = V10ROWS[file][(aid,key)][field]
        if str(val) != ref: mism.append(f'{file} {aid} {key} {field}: v1.0={ref} rerun={val}')
    V10ROWS = {}
    for f,kf in [('joint_estimates.csv',None),('age_specific.csv','age_group'),('with_without_contrast.csv',None),('with_without_std.csv',None),('with_without_by_age.csv','age_group')]:
        V10ROWS[f] = {(r['area_id'], r[kf] if kf else ''): r for r in csv.DictReader(open(V10/f))}
    Q = {'older_hh': ALL, 'older_amb': lambda k: k.dphy=='1', 'older_amb_noveh': lambda k: k.dphy=='1' and k.noveh, 'older_noveh': lambda k: k.noveh}
    E = {}; EN = {}
    for aid in V10_ORDER + [TOT]:
        for g in G + ['all']:
            for q,p in Q.items():
                E[(aid,g,q)], EN[(aid,g,q)] = tot(AREAS_OF(aid), (lambda k,p=p,g=g: p(k) and (g=='all' or k.ag==g)))
    T1 = []
    for aid in V10_ORDER + [TOT]:
        row = {}
        for q in Q:
            v = E[(aid,'all',q)]; s = se(v)
            row.update({q: round(v[0]), q+'_moe90': round(1.645*s), q+'_unweighted_n': EN[(aid,'all',q)], q+'_cv': round(s/v[0],4) if v[0] else None})
        for name,num,den in [('share_amb_in_noveh_hh','older_amb_noveh','older_amb'),('share_older_in_noveh_hh','older_noveh','older_hh')]:
            r_ = asens.vdiv(E[(aid,'all',num)], E[(aid,'all',den)]); row[name+'_pct'] = round(100*r_[0],2); row[name+'_moe90_pp'] = round(100*1.645*se(r_),2)
        for fld,val in row.items(): cmp('joint_estimates.csv', aid, '', fld, val)
        vn = E[(aid,'all','older_noveh')]; vh = E[(aid,'all','older_hh')]
        r1 = {'area_id':aid,'area':NAME[aid]}; r1.update(count_fields('older_65plus', vh, EN[(aid,'all','older_hh')]))
        r1.update(count_fields('no_vehicle_65plus', vn, EN[(aid,'all','older_noveh')]))
        r1.update(share_fields('no_vehicle_share_of_65plus', vn, vh, EN[(aid,'all','older_noveh')])[0]); r1['source'] = 'Version 1.0 joint_estimates.csv (reused; reproduced exactly)'
        T1.append(r1)
    T2 = []
    for aid in V10_ORDER + [TOT]:
        for g in G:
            e = {q:E[(aid,g,q)] for q in Q}; a_ = asens.vdiv(e['older_amb_noveh'],e['older_amb']); b_ = asens.vdiv(e['older_noveh'],e['older_hh'])
            row = {}
            for q in Q: row.update({q: round(e[q][0]), q+'_moe90': round(moe(e[q])), q+'_unweighted_n': EN[(aid,g,q)]})
            row.update(amb_prevalence_pct=round(100*e['older_amb'][0]/e['older_hh'][0],2), amb_prevalence_moe90_pp=round(100*moe(asens.vdiv(e['older_amb'],e['older_hh'])),2),
                       share_amb_in_noveh_hh_pct=round(100*a_[0],2), share_amb_in_noveh_hh_moe90_pp=round(100*moe(a_),2),
                       share_older_in_noveh_hh_pct=round(100*b_[0],2), share_older_in_noveh_hh_moe90_pp=round(100*moe(b_),2),
                       ratio=round(a_[0]/b_[0],2), ratio_moe90=round(moe(asens.vdiv(a_,b_)),2))
            for fld,val in row.items(): cmp('age_specific.csv', aid, g, fld, val)
            r2 = {'area_id':aid,'area':NAME[aid],'age_group':g}
            r2.update(share_fields('no_vehicle_share', e['older_noveh'], e['older_hh'], EN[(aid,g,'older_noveh')])[0])
            r2['source'] = 'Version 1.0 age_specific.csv (reused; reproduced exactly)'; T2.append(r2)
    # contrast (with_without_contrast.csv) and age-standardized contrast (with_without_std.csv, with_without_by_age.csv)
    Ttot = {g:E[(TOT,g,'older_hh')][0] for g in G}; s_ = sum(Ttot.values()); S1 = {g:Ttot[g]/s_ for g in G}
    Ta = {g:E[(TOT,g,'older_amb')][0] for g in G}; s_ = sum(Ta.values()); S2 = {g:Ta[g]/s_ for g in G}
    if {g:round(v,6) for g,v in S1.items()} != S1_PUBLISHED: mism.append(f'S1 {S1} != published {S1_PUBLISHED}')
    if {g:round(v,6) for g,v in S2.items()} != S2_PUBLISHED: mism.append(f'S2 {S2} != published {S2_PUBLISHED}')
    for aid in V10_ORDER + [TOT]:
        e = {q:E[(aid,'all',q)] for q in Q}
        wo_n = asens.vsub(e['older_noveh'], e['older_amb_noveh']); wo_d = asens.vsub(e['older_hh'], e['older_amb'])
        sw = asens.vdiv(e['older_amb_noveh'], e['older_amb']); so = asens.vdiv(wo_n, wo_d); d = [100*(sw[i]-so[i]) for i in R]; r_ = asens.vdiv(sw, so)
        row = dict(older_without_amb=round(wo_d[0]), older_without_amb_moe90=round(moe(wo_d)), older_without_amb_noveh=round(wo_n[0]), older_without_amb_noveh_moe90=round(moe(wo_n)),
                   share_with_amb_in_noveh_hh_pct=round(100*sw[0],2), share_with_amb_in_noveh_hh_moe90_pp=round(100*moe(sw),2),
                   share_without_amb_in_noveh_hh_pct=round(100*so[0],2), share_without_amb_in_noveh_hh_moe90_pp=round(100*moe(so),2),
                   diff_with_minus_without_pp=round(d[0],2), diff_with_minus_without_moe90_pp=round(moe(d),2),
                   ratio_with_to_without=round(r_[0],2), ratio_with_to_without_moe90=round(moe(r_),2), diff_exceeds_moe90=abs(d[0]) > moe(d))
        for fld,val in row.items(): cmp('with_without_contrast.csv', aid, '', fld, val)
        eg = {g:{q:E[(aid,g,q)] for q in Q} for g in G}
        swg = {g:asens.vdiv(eg[g]['older_amb_noveh'], eg[g]['older_amb']) for g in G}
        sog = {g:asens.vdiv(asens.vsub(eg[g]['older_noveh'],eg[g]['older_amb_noveh']), asens.vsub(eg[g]['older_hh'],eg[g]['older_amb'])) for g in G}
        for g in G:
            dg = [100*(swg[g][i]-sog[g][i]) for i in R]; rg = asens.vdiv(swg[g], sog[g])
            rb = dict(share_with_amb_in_noveh_hh_pct=round(100*swg[g][0],2), share_with_amb_in_noveh_hh_moe90_pp=round(100*moe(swg[g]),2),
                      share_without_amb_in_noveh_hh_pct=round(100*sog[g][0],2), share_without_amb_in_noveh_hh_moe90_pp=round(100*moe(sog[g]),2),
                      diff_with_minus_without_pp=round(dg[0],2), diff_with_minus_without_moe90_pp=round(moe(dg),2),
                      ratio_with_to_without=round(rg[0],2), ratio_with_to_without_moe90=round(moe(rg),2), with_amb_noveh_unweighted_n=EN[(aid,g,'older_amb_noveh')])
            for fld,val in rb.items(): cmp('with_without_by_age.csv', aid, g, fld, val)
        stw = std(swg, S1); sto = std(sog, S1); row = {}
        for k_,v in [('crude_share_with',sw),('std_share_with',stw),('crude_share_without',so),('std_share_without',sto)]:
            row[k_+'_pct'] = round(100*v[0],2); row[k_+'_moe90_pp'] = round(100*moe(v),2)
        for k_,(x,y) in [('crude',(sw,so)),('std',(stw,sto))]:
            dd = [100*(x[i]-y[i]) for i in R]; rr = asens.vdiv(x,y)
            row[k_+'_diff_pp'] = round(dd[0],2); row[k_+'_diff_moe90_pp'] = round(moe(dd),2); row[k_+'_diff_exceeds_moe90'] = abs(dd[0]) > moe(dd)
            row[k_+'_ratio'] = round(rr[0],2); row[k_+'_ratio_moe90'] = round(moe(rr),2)
        for fld,val in row.items(): cmp('with_without_std.csv', aid, '', fld, val)
    log(f'CHECK 1 (Version 1.0 reproduction): {ncmp} values compared across joint_estimates, age_specific, with_without_contrast, with_without_std, with_without_by_age; mismatches: {len(mism)}')
    for m in mism[:50]: log('  MISMATCH', m)
    if mism: stop('check 1', 'Version 1.0 values not reproduced exactly')
    log(f'  S1 (unrounded, derived as in v1.0) = {S1}; rounds to the SAP constants. S2 = {S2}; rounds to the v1.0 methodology constants.')
    # ================= CHECK 2: internal sums, replicate by replicate
    bad = []; nsum = 0
    def same(x, y, what):
        nonlocal nsum; nsum += 1
        if any(abs(x[i]-y[i]) > 1e-6*max(1.0, abs(y[i])) for i in R): bad.append(what)
    PREDS = {'all':ALL, 'noveh':lambda k:k.noveh, 'alone':lambda k:k.alone, 'notalone':lambda k:not k.alone, 'alone_noveh':lambda k:k.alone and k.noveh,
             'notalone_noveh':lambda k:(not k.alone) and k.noveh, 'alone_noveh_dphy':lambda k:k.alone and k.noveh and k.dphy=='1'}
    for p_,pr in PREDS.items():
        areas_sum = [0.0]*(NR+1)
        for aid in V10_ORDER:
            whole = tot([aid], pr)[0]; parts = asens.vadd(*[tot([aid], lambda k,g=g: pr(k) and k.ag==g)[0] for g in G])
            same(parts, whole, f'{aid} {p_}: age groups vs total'); areas_sum = asens.vadd(areas_sum, whole)
        same(areas_sum, tot(V10_ORDER, pr)[0], f'{p_}: areas vs eight-area total')
    n_age_area = nsum
    # Run v1.1 (validator note N4): the 72 complement identities of run v1 summed complementary predicates over the same cells and could not
    # fail. They are replaced by identities against sources computed independently of the cell table:
    #   V  = Version 1.0 code (age_sensitivity.accumulate_by_age), a separate read of the PUMS files: older_hh and older_noveh by area and age
    #   D  = direct accumulators in this run's pass, keyed on the raw NP and VEH codes rather than the cell key
    # Per area (8) and eight-area total, per age group (3) and 65+ (4 rows): (a) D[NP=1] + D[NP>=2] = V older_hh; (b) D[VEH=0] + D[VEH 1-6] = V older_hh;
    # (c) cell-table living-alone total = D[NP=1]; (d) cell-table no-vehicle total = V older_noveh.  4 x 36 = 144 identities.
    def vsum(aid, g, key):
        out = [0.0]*(NR+1)
        for a in AREAS_OF(aid):
            for gg in (G if g=='all' else [g]):
                v = V10AGE[a][gg][key] if key in ('older_hh','older_noveh') else DIRECT[a][(gg, key)]
                out = asens.vadd(out, v)
        return out
    for aid in V10_ORDER + [TOT]:
        for g in G + ['all']:
            f_ = (lambda k,g=g: g=='all' or k.ag==g)
            same(asens.vadd(vsum(aid,g,'np1'), vsum(aid,g,'np2plus')), vsum(aid,g,'older_hh'), f'{aid} {g}: direct NP=1 + NP>=2 vs Version 1.0 code older_hh')
            same(asens.vadd(vsum(aid,g,'veh0'), vsum(aid,g,'veh1to6')), vsum(aid,g,'older_hh'), f'{aid} {g}: direct VEH=0 + VEH 1-6 vs Version 1.0 code older_hh')
            same(tot(AREAS_OF(aid), lambda k: f_(k) and k.alone)[0], vsum(aid,g,'np1'), f'{aid} {g}: cell-table living alone vs direct NP=1')
            same(tot(AREAS_OF(aid), lambda k: f_(k) and k.noveh)[0], vsum(aid,g,'older_noveh'), f'{aid} {g}: cell-table no vehicle vs Version 1.0 code older_noveh')
    log(f'CHECK 2a (internal sums, replicate by replicate): {n_age_area} age-group and area identities + {nsum-n_age_area} identities against independently computed totals = {nsum}; failures: {len(bad)}')
    if bad: stop('check 2', '; '.join(bad[:10]))
    # ================= CHECK 3: NP = 1 vs HHT 4/6 among householders in the universe
    log(f"CHECK 3 (recode): householders 65+ in universe: {recode['householders']}; NP/HHT disagreements: {recode['disagree']}; non-householders with NP=1: {recode['nonhouseholder_np1']}; unexpected VEH codes: {misc['veh_unexpected']}")
    if recode['disagree'] or recode['nonhouseholder_np1']: stop('check 3', f"examples {recode['examples'][:5]}")
    # ================= missing values (SAP s.3)
    miss = {}
    for var in ('dphy','dout','pov','ten'):
        miss[var] = tot(V10_ORDER, lambda k,v=var: getattr(k,v)=='NA')[1]
    log(f'Missing values among people 65+ in universe (unweighted records): {miss}')
    write_csv('t1_no_vehicle_reused_v1.0.csv', [r for a in ORDER+[TOT] for r in T1 if r['area_id']==a])
    write_csv('t2_no_vehicle_by_age_reused_v1.0.csv', [r for a in ORDER+[TOT] for g in G for r in T2 if r['area_id']==a and r['age_group']==g])
    RES = {'check2a':{'age_area_identities':n_age_area,'independent_identities':nsum-n_age_area,'failures':len(bad)}, 'version':VERSION, 'S1':S1, 'S2':S2, 'missing_records':miss, 'recode':{k:v for k,v in recode.items() if k!='examples'}}
    # ================= T3 profile (and sensitivity 1)
    tenure_detail_n = tot(V10_ORDER, lambda k: k.noveh and k.ten=='4')[1]
    show_ten4 = tenure_detail_n >= 50
    log(f'T3 tenure detail rule: records with TEN=4 among no-vehicle older adults, eight areas: {tenure_detail_n} -> shown separately: {show_ten4}')
    def profile_vars(poverty_cut):
        V = [('sex','male',lambda k:k.sex=='1',lambda k:True), ('sex','female',lambda k:k.sex=='2',lambda k:True),
             ('living_alone','lives_alone',lambda k:k.alone,lambda k:True), ('living_alone','does_not_live_alone',lambda k:not k.alone,lambda k:True)]
        okp = lambda k: k.pov!='NA'
        if poverty_cut == 100:
            V += [('poverty','below_100',lambda k:k.pov=='lt100',okp), ('poverty','100_to_149',lambda k:k.pov=='100_149',okp), ('poverty','150_or_more',lambda k:k.pov=='ge150',okp)]
        else:
            V += [('poverty','below_150',lambda k:k.pov in ('lt100','100_149'),okp), ('poverty','150_or_more',lambda k:k.pov=='ge150',okp)]
        okt = lambda k: k.ten!='NA'
        V += [('tenure','owner',lambda k:k.ten in ('1','2'),okt), ('tenure','renter_or_occupied_without_rent',lambda k:k.ten in ('3','4'),okt)]
        if show_ten4: V += [('tenure_detail','of_which_rented',lambda k:k.ten=='3',okt), ('tenure_detail','of_which_occupied_without_payment_of_rent',lambda k:k.ten=='4',okt)]
        okd = lambda k: k.dphy!='NA'; oko = lambda k: k.dout!='NA'
        V += [('walking_difficulty','with',lambda k:k.dphy=='1',okd), ('walking_difficulty','without',lambda k:k.dphy=='2',okd),
              ('independent_living_difficulty','with',lambda k:k.dout=='1',oko), ('independent_living_difficulty','without',lambda k:k.dout=='2',oko)]
        return V
    def profile(poverty_cut):
        rows = []; sumbad = []
        for aid in ORDER + [TOT]:
            for grp,gp in [('no_vehicle',lambda k:k.noveh),('with_vehicle',lambda k:not k.noveh)]:
                acc = collections.defaultdict(float)
                for var,cat,pr,ok in profile_vars(poverty_cut):
                    num,nn = tot(AREAS_OF(aid), lambda k: gp(k) and ok(k) and pr(k)); den,_ = tot(AREAS_OF(aid), lambda k: gp(k) and ok(k))
                    f_,_,_ = share_fields('share', num, den, nn)
                    rows.append({'area_id':aid,'area':NAME[aid],'group':grp,'variable':var,'category':cat, **f_, 'group_denominator':round(den[0]), 'tier_note':TIER_NOTE[f_['share_tier']]})
                    if var != 'tenure_detail': acc[var] += f_['share_pct']
                    else: acc['tenure_detail'] += f_['share_pct']
                for var,sm in acc.items():
                    if var == 'tenure_detail': continue
                    k_ = len([1 for v,*_ in profile_vars(poverty_cut) if v==var])
                    if abs(sm-100) > 0.005*k_+1e-9: sumbad.append(f'{aid} {grp} {var} sums to {sm:.2f}')
        return rows, sumbad
    T3, sb = profile(100)
    log(f'CHECK 2b (T3 shares sum to 100% within rounding): failures: {len(sb)}')
    if sb: stop('check 2b', '; '.join(sb[:10]))
    write_csv('t3_profile_no_vehicle_vs_with_vehicle.csv', T3)
    T3s, sb2 = profile(150)
    if sb2: stop('check 2b (sensitivity)', '; '.join(sb2[:10]))
    write_csv('sens1_t3_profile_poverty_cut_150.csv', T3s)
    # ================= T4 lead table
    LA = lambda k: k.alone and k.noveh
    T4 = []; detail = {}
    for aid in ORDER + [TOT]:
        ns = {g: tot(AREAS_OF(aid), lambda k,g=g: LA(k) and k.ag==g)[1] for g in G}
        if all(ns[g] >= 50 for g in G): lvl, groups = 'three_groups', [('65_74',('65_74',)),('75_84',('75_84',)),('85_plus',('85_plus',))]
        elif ns['65_74'] >= 50 and ns['75_84']+ns['85_plus'] >= 50: lvl, groups = '75_plus_combined', [('65_74',('65_74',)),('75_plus',('75_84','85_plus'))]
        else: lvl, groups = '65_plus_only', []
        detail[aid] = (lvl, ns)
        for lab,gs in groups + [('65_plus', tuple(G))]:
            inn = lambda k,gs=gs: k.ag in gs
            c,nn = tot(AREAS_OF(aid), lambda k: LA(k) and inn(k)); allv,_ = tot(AREAS_OF(aid), inn); nv,_ = tot(AREAS_OF(aid), lambda k: k.noveh and inn(k))
            row = {'area_id':aid,'area':NAME[aid],'age_group':lab,'age_detail_rule':lvl}
            row.update(count_fields('lives_alone_no_vehicle', c, nn))
            row.update(share_fields('share_of_all_65plus', c, allv, nn)[0]); row.update(share_fields('share_of_no_vehicle_65plus_living_alone', c, nv, nn)[0])
            T4.append(row)
    log('T4 age-detail decisions (n of living-alone no-vehicle records by age): ' + '; '.join(f'{a}: {detail[a][0]} {dict(detail[a][1])}' for a in ORDER+[TOT]))
    write_csv('t4_living_alone_no_vehicle.csv', T4)
    # ================= eligibility for F1 and F2 (counts only, before any test)
    elig1 = {}; elig2 = {}
    for aid in ORDER + [TOT]:
        c1 = {g:(tot(AREAS_OF(aid), lambda k,g=g: k.ag==g)[1], tot(AREAS_OF(aid), lambda k,g=g: k.ag==g and LA(k))[1]) for g in G}
        c2 = {g:(tot(AREAS_OF(aid), lambda k,g=g: k.ag==g and k.alone)[1], tot(AREAS_OF(aid), lambda k,g=g: k.ag==g and LA(k))[1],
                 tot(AREAS_OF(aid), lambda k,g=g: k.ag==g and not k.alone)[1], tot(AREAS_OF(aid), lambda k,g=g: k.ag==g and (not k.alone) and k.noveh)[1]) for g in G}
        if aid != TOT: elig1[aid] = (all(d>=30 and m>=10 for d,m in c1.values()), c1)
        elig2[aid] = (all(c[0]>=30 and c[1]>=10 and c[2]>=30 and c[3]>=10 for c in c2.values()), c2)
    erows = [{'family':'F1','area_id':a,'eligible':elig1[a][0], **{f'{g}_den_n':elig1[a][1][g][0] for g in G}, **{f'{g}_num_n':elig1[a][1][g][1] for g in G}} for a in ORDER] + \
            [{'family':'F2','area_id':a,'eligible':elig2[a][0], **{f'{g}_alone_den_n':elig2[a][1][g][0] for g in G}, **{f'{g}_alone_num_n':elig2[a][1][g][1] for g in G},
              **{f'{g}_notalone_den_n':elig2[a][1][g][2] for g in G}, **{f'{g}_notalone_num_n':elig2[a][1][g][3] for g in G}} for a in ORDER+[TOT]]
    write_csv('test_eligibility_counts_only.csv', erows)
    log(f'Eligibility fixed before tests. F1 tested: {[a for a in ORDER if elig1[a][0]]} not tested: {[a for a in ORDER if not elig1[a][0]]}. '
        f'F2 tested: {[a for a in ORDER+[TOT] if elig2[a][0]]} not tested: {[a for a in ORDER+[TOT] if not elig2[a][0]]}')
    (LOGD/'eligibility-fixed-before-tests.json').write_text(json.dumps({'F1':{a:v[0] for a,v in elig1.items()}, 'F2':{a:v[0] for a,v in elig2.items()},
        'family_size_F1':sum(v[0] for v in elig1.values()), 'family_size_F2':sum(v[0] for v in elig2.values())}, indent=2)+'\n')
    # ================= age-specific components
    def la_shares(areas):  # F1 measure: share of all 65+ living alone with no vehicle, by age
        return {g: asens.vdiv(tot(areas, lambda k,g=g: k.ag==g and LA(k))[0], tot(areas, lambda k,g=g: k.ag==g)[0]) for g in G}
    def f2_shares(areas):
        a_ = {g: asens.vdiv(tot(areas, lambda k,g=g: k.ag==g and LA(k))[0], tot(areas, lambda k,g=g: k.ag==g and k.alone)[0]) for g in G}
        b_ = {g: asens.vdiv(tot(areas, lambda k,g=g: k.ag==g and (not k.alone) and k.noveh)[0], tot(areas, lambda k,g=g: k.ag==g and not k.alone)[0]) for g in G}
        return a_, b_
    # ================= T5 (F2 measure) and T6 (F1 measure)
    T5 = []; COMP = []
    F2V = {}
    for aid in ORDER + [TOT]:
        A = AREAS_OF(aid)
        nA,nAn = tot(A, LA); dA,dAn = tot(A, lambda k:k.alone); nB,nBn = tot(A, lambda k:(not k.alone) and k.noveh); dB,_ = tot(A, lambda k: not k.alone)
        fa, ca_, ta = share_fields('crude_share_no_vehicle_living_alone', nA, dA, nAn); fb, cb_, tb = share_fields('crude_share_no_vehicle_not_living_alone', nB, dB, nBn)
        sa, sb_ = f2_shares(A)
        ssa = std(sa, S1); ssb = std(sb_, S1); F2V[aid] = (sa, sb_)
        cva, cvb = cv(ssa), cv(ssb); tsa, tsb = tier(nAn, cva), tier(nBn, cvb)
        row = {'area_id':aid,'area':NAME[aid], **fa, **fb}
        dd = [100*(ca_[i]-cb_[i]) for i in R]; rr = asens.vdiv(ca_, cb_)
        row.update(crude_diff_pp=round(dd[0],2), crude_diff_moe90_pp=round(moe(dd),2), crude_ratio=round(rr[0],2), crude_ratio_moe90=round(moe(rr),2), crude_diff_ratio_tier=worst(ta,tb))
        CARRY_T5 = dict(crude_diff_ratio_unweighted_n=min(fa['crude_share_no_vehicle_living_alone_unweighted_n'], fb['crude_share_no_vehicle_not_living_alone_unweighted_n']),
                        crude_diff_ratio_cv=max(fa['crude_share_no_vehicle_living_alone_cv'], fb['crude_share_no_vehicle_not_living_alone_cv']))
        row.update(std_share_no_vehicle_living_alone_pct=round(100*ssa[0],2), std_share_no_vehicle_living_alone_moe90_pp=round(100*moe(ssa),2), std_share_no_vehicle_living_alone_unweighted_n=nAn,
                   std_share_no_vehicle_living_alone_cv=round(cva,4), std_share_no_vehicle_living_alone_tier=tsa,
                   std_share_no_vehicle_not_living_alone_pct=round(100*ssb[0],2), std_share_no_vehicle_not_living_alone_moe90_pp=round(100*moe(ssb),2), std_share_no_vehicle_not_living_alone_unweighted_n=nBn,
                   std_share_no_vehicle_not_living_alone_cv=round(cvb,4), std_share_no_vehicle_not_living_alone_tier=tsb)
        dd = [100*(ssa[i]-ssb[i]) for i in R]; rr = asens.vdiv(ssa, ssb)
        row.update(std_diff_pp=round(dd[0],2), std_diff_moe90_pp=round(moe(dd),2), std_ratio=round(rr[0],2), std_ratio_moe90=round(moe(rr),2), std_diff_ratio_tier=worst(tsa,tsb),
                   _crude_ratio_unrounded=asens.vdiv(ca_,cb_)[0], _std_ratio_unrounded=rr[0], _std_ratio_lower90=rr[0]-moe(rr), _crude_ratio_lower90=asens.vdiv(ca_,cb_)[0]-moe(asens.vdiv(ca_,cb_)))
        row['tier_rule_note'] = 'difference/ratio tier = worse of the two component share tiers'
        row.update(CARRY_T5); row.update(std_diff_ratio_unweighted_n=min(nAn, nBn), std_diff_ratio_cv=max(round(cva,4), round(cvb,4)),
                   carried_n_cv_note='run v1.1: difference/ratio n = smaller component n, CV = larger component CV (carried from the component shares; consistent with the weaker-tier rule)')
        T5.append(row)
        for g in G:
            COMP.append({'measure':'F2 (T5) standardization input','area_id':aid,'age_group':g,'share_no_vehicle_living_alone_pct':round(100*sa[g][0],2),'share_no_vehicle_living_alone_moe90_pp':round(100*moe(sa[g]),2),
                         'share_no_vehicle_not_living_alone_pct':round(100*sb_[g][0],2),'share_no_vehicle_not_living_alone_moe90_pp':round(100*moe(sb_[g]),2),'note':'standardization input; not a display table'})
    write_csv('t5_no_vehicle_living_alone_vs_not.csv', [{k:v for k,v in r.items() if not k.startswith('_')} for r in T5])
    T6 = []; F1V = {}
    for aid in ORDER + [TOT]:
        A = AREAS_OF(aid); sh = la_shares(A); s_ = std(sh, S1); F1V[aid] = sh; nn = tot(A, LA)[1]; c_ = cv(s_)
        T6.append({'area_id':aid,'area':NAME[aid],'std_share_65plus_living_alone_no_vehicle_pct':round(100*s_[0],2),'std_share_65plus_living_alone_no_vehicle_moe90_pp':round(100*moe(s_),2),
                   'std_share_65plus_living_alone_no_vehicle_unweighted_n':nn,'std_share_65plus_living_alone_no_vehicle_cv':round(c_,4),'std_share_65plus_living_alone_no_vehicle_tier':tier(nn,c_),'standard':'S1'})
        for g in G:
            COMP.append({'measure':'F1 (T6) standardization input','area_id':aid,'age_group':g,'share_65plus_living_alone_no_vehicle_pct':round(100*sh[g][0],2),'share_65plus_living_alone_no_vehicle_moe90_pp':round(100*moe(sh[g]),2),'note':'standardization input; not a display table'})
    write_csv('t6_std_living_alone_no_vehicle_share.csv', T6)
    write_csv('standardization_inputs_by_age.csv', COMP)
    # ================= tests
    def run_tests(S, label):
        f1 = []
        for aid in ORDER:
            if not elig1[aid][0]: continue
            rest = [a for a in V10_ORDER if a != aid]; sr = la_shares(rest)
            d = [100*(x-y) for x,y in zip(std(F1V[aid],S), std(sr,S))]; z,p = asens.pval(d)
            f1.append({'family':'F1','standard':label,'area_id':aid,'comparison':f'{aid} minus other seven combined','measure':'age-standardized share of all 65+ living alone with no vehicle (pp)',
                       'estimate_pp':round(d[0],2),'moe90_pp':round(moe(d),2),'z':round(z,2),'p':p,
                       '_carry':{'area_std_share_unweighted_n':tot([aid] if aid!=TOT else V10_ORDER, LA)[1], 'area_std_share_cv':round(cv(std(F1V[aid],S)),4),
                                 'other_seven_std_share_unweighted_n':tot(rest, LA)[1], 'other_seven_std_share_cv':round(cv(std(sr,S)),4)}})
        f2 = []
        for aid in ORDER + [TOT]:
            if not elig2[aid][0]: continue
            sa, sb_ = F2V[aid]; d = [100*(x-y) for x,y in zip(std(sa,S), std(sb_,S))]; z,p = asens.pval(d)
            rr = asens.vdiv(std(sa,S), std(sb_,S))
            f2.append({'family':'F2','standard':label,'area_id':aid,'comparison':f'{aid}: living alone minus not living alone','measure':'age-standardized no-vehicle share (pp)',
                       'estimate_pp':round(d[0],2),'moe90_pp':round(moe(d),2),'std_ratio':round(rr[0],2),'std_ratio_moe90':round(moe(rr),2),'z':round(z,2),'p':p,
                       '_carry':{'living_alone_std_share_unweighted_n':tot(AREAS_OF(aid), LA)[1], 'living_alone_std_share_cv':round(cv(std(sa,S)),4),
                                 'not_living_alone_std_share_unweighted_n':tot(AREAS_OF(aid), lambda k:(not k.alone) and k.noveh)[1], 'not_living_alone_std_share_cv':round(cv(std(sb_,S)),4)}})
        for fam in (f1, f2):
            asens.holm(fam, 0.10)
            for t in fam:
                t['remains_after_holm_10pct'] = t.pop('holm_significant'); t['borderline'] = t['remains_after_holm_10pct'] and t['holm_adjusted_p'] > 0.05
                t['holm_adjusted_p'] = float(f"{t['holm_adjusted_p']:.3g}"); t['p'] = float(f"{t['p']:.3g}"); t['holm_threshold'] = round(t['holm_threshold'],6)
                if t['family']=='F1':
                    t['wording'] = (('higher' if t['estimate_pp']>0 else 'lower') + ' than the other seven combined') if t['remains_after_holm_10pct'] else 'not distinguishable from the other seven combined'
                else:
                    t['wording'] = (('no-vehicle share higher among people living alone than among those living with others' if t['estimate_pp']>0 else 'no-vehicle share lower among people living alone than among those living with others')
                                    if t['remains_after_holm_10pct'] else 'not distinguishable between people living alone and those living with others')
                if t['borderline']: t['wording'] += ' (borderline: remains at 10% familywise level only; not for headlines or local summaries)'
        nt1 = [{'family':'F1','standard':label,'area_id':a,'wording':'not tested: sample too small'} for a in ORDER if not elig1[a][0]]
        nt2 = [{'family':'F2','standard':label,'area_id':a,'wording':'not tested: sample too small'} for a in ORDER+[TOT] if not elig2[a][0]]
        return f1+nt1, f2+nt2
    F1, F2 = run_tests(S1, 'S1'); F1s, F2s = run_tests(S2, 'S2')
    chg = []
    for prim, sens in ((F1,F1s),(F2,F2s)):
        sm = {(t['family'],t['area_id']):t for t in sens}
        for t in prim:
            s_ = sm[(t['family'],t['area_id'])]
            row = {'family':t['family'],'area_id':t['area_id'],'S1_result':t['wording'],'S2_result':s_['wording'],
                   'S1_estimate_pp':t.get('estimate_pp',''),'S2_estimate_pp':s_.get('estimate_pp',''),'S1_holm_adjusted_p':t.get('holm_adjusted_p',''),'S2_holm_adjusted_p':s_.get('holm_adjusted_p',''),
                   'primary_conclusion_changes':t.get('remains_after_holm_10pct') != s_.get('remains_after_holm_10pct'),
                   'borderline_status_changes':t.get('borderline') != s_.get('borderline')}
            chg.append(row)
    write_csv('sens2_f1_f2_standard_S2.csv', chg)
    # Run v1.1 (validator notes N1, N2; David's decisions relayed 14 Nov 2026). Additive columns only; estimates, tests and wording unchanged.
    #  - s2_sensitivity_note: SAP s.8 statement beside each result
    #  - headline_local_summary_eligible: results stand under the plan, but these are kept out of headlines and local summaries:
    #      (run v1.2) fragile results, by the rule below
    # Run v1.2: David P. Faustina's reporting rule (14 Nov 2026, 4:40 PM), applied generally, replacing the v1.1 Orlando-only list:
    #   a result is FRAGILE if it remains after Holm at 10% under S1 and (a) its conclusion changes under the alternative standard S2, or
    #   (b) it is borderline under S2, or (c) it is borderline under S1 (s.6), or (d) its S1 Holm-adjusted p sits "within a hair" of the 5% cut.
    #   "Within a hair" is operationalized as NEAR_CUT_LOW <= Holm-adjusted p <= 0.05, i.e. within 0.01 of the 0.05 cut that defines borderline
    #   (Orlando, 0.0486, is the motivating case). Fragile results stand under the plan and stay in tables and the technical report with their
    #   sensitivity note, but are kept out of headlines and local summaries. Headlines use only the pre-specified eight-area lead: no area
    #   result is headline-eligible. Local summaries may state an F1 comparison only if it remains and is not fragile.
    #   David named Sacramento and Tampa for local summaries (4:40 PM) and confirmed Phoenix at 5:38 PM, 14 Nov 2026 ("Yes, Phoenix may appear
    #   in its local summary."), so every non-fragile remaining F1 area result is local-summary eligible.
    NEAR_CUT_LOW, CUT = 0.04, 0.05
    S2MAP = {(t['family'], t['area_id']): t for t in F1s + F2s}
    cm = {(r['family'], r['area_id']): r for r in chg}
    for fam in (F1, F2):
        for t in fam:
            c_ = cm[(t['family'], t['area_id'])]
            carry = t.pop('_carry', {})
            if 'not tested' in t['wording']: t['s2_sensitivity_note'] = 'not tested under either standard'; t['headline_local_summary_eligible'] = False; t['headline_local_summary_exclusion_reason'] = 'not tested'; continue
            if c_['primary_conclusion_changes']: note = f"Under the alternative age standard S2 this result changes: {c_['S2_result']} (S2 estimate {c_['S2_estimate_pp']:+.2f} points; Holm-adjusted p {c_['S2_holm_adjusted_p']})."
            elif c_['borderline_status_changes']: note = f"Under the alternative age standard S2 this result still remains but is borderline (S2 Holm-adjusted p {c_['S2_holm_adjusted_p']})."
            else: note = f"Unchanged under the alternative age standard S2 (S2 Holm-adjusted p {c_['S2_holm_adjusted_p']})."
            reasons = []; s2t = S2MAP[(t['family'], t['area_id'])]; remains = bool(t.get('remains_after_holm_10pct'))
            if remains:
                if t.get('borderline'): reasons.append('borderline under S1 (SAP s.6)')
                if c_['primary_conclusion_changes']: reasons.append(f"fails under the alternative age standard S2 (S2: {c_['S2_result']}; Holm-adjusted p {c_['S2_holm_adjusted_p']})")
                elif s2t.get('borderline'): reasons.append(f"borderline under the alternative age standard S2 (Holm-adjusted p {c_['S2_holm_adjusted_p']})")
                if NEAR_CUT_LOW <= t['holm_adjusted_p'] <= CUT: reasons.append(f"S1 Holm-adjusted p {t['holm_adjusted_p']} is within a hair of the 5% cut (band {NEAR_CUT_LOW}–{CUT})")
            fragile = bool(reasons)
            t['s2_sensitivity_note'] = note
            t['headline_local_summary_eligible'] = not fragile
            t['headline_local_summary_exclusion_reason'] = ('fragile: ' + '; '.join(reasons) + ' (David P. Faustina reporting rule, 14 Nov 2026)') if fragile else ''
            t['fragile'] = fragile; t['fragility_reason'] = '; '.join(reasons)
            t['headline_eligible'] = (t['family'] == 'F2' and t['area_id'] == TOT and remains and not fragile)
            t['headline_rule'] = ('used only through the pre-specified eight-area lead (SAP s.9)' if t['headline_eligible'] else 'no area results in headlines; headlines use only the pre-specified eight-area lead')
            if t['area_id'] == TOT:
                t['local_summary_eligible'] = False; t['local_summary_claim'] = 'not applicable (eight areas combined)'
            elif not remains:
                t['local_summary_eligible'] = False; t['local_summary_claim'] = 'none: ' + t['wording'] + ' (no comparison claim)'
            elif fragile:
                t['local_summary_eligible'] = False; t['local_summary_claim'] = 'none: fragile result, reported only in tables and the technical report with its sensitivity note'
            else:
                t['local_summary_eligible'] = True; t['local_summary_claim'] = t['wording']
            t.update({k: v for k, v in carry.items()})
            ns = [v for k, v in carry.items() if k.endswith('_unweighted_n')]; cs = [v for k, v in carry.items() if k.endswith('_cv')]
            t['difference_unweighted_n'] = min(ns); t['difference_cv'] = max(cs)
            t['carried_n_cv_note'] = 'run v1.1: n and CV carried from the two component age-standardized shares (S1); difference n = smaller, CV = larger'
    write_csv('f1_tests_area_vs_other_seven.csv', F1); write_csv('f2_tests_living_alone_vs_not.csv', F2)
    # ================= T7
    T7 = []; L3 = lambda k: LA(k) and k.dphy=='1'
    for aid in ORDER + [TOT]:
        A = AREAS_OF(aid); c,nn = tot(A, L3)
        if aid != TOT and nn < 50:
            T7.append({'area_id':aid,'area':NAME[aid],'shown':False,'reason':'area n < 50 (SAP s.7: eight areas combined only)'}); continue
        allv,_ = tot(A, ALL); la,_ = tot(A, LA)
        row = {'area_id':aid,'area':NAME[aid],'shown':True,'reason':''}; row.update(count_fields('lives_alone_no_vehicle_walking_difficulty', c, nn))
        row.update(share_fields('share_of_all_65plus', c, allv, nn)[0]); row.update(share_fields('share_of_living_alone_no_vehicle_group', c, la, nn)[0]); T7.append(row)
    write_csv('t7_living_alone_no_vehicle_walking_difficulty.csv', T7)
    # ================= T8
    T8 = []
    for aid in ORDER + [TOT]:
        A = AREAS_OF(aid)
        n1,n1n = tot(A, lambda k:k.noveh and k.dout=='1'); d1,_ = tot(A, lambda k:k.noveh and k.dout!='NA')
        n2,n2n = tot(A, lambda k:(not k.noveh) and k.dout=='1'); d2,_ = tot(A, lambda k:(not k.noveh) and k.dout!='NA')
        fa, sa, ta = share_fields('independent_living_difficulty_no_vehicle', n1, d1, n1n); fb, sb_, tb = share_fields('independent_living_difficulty_with_vehicle', n2, d2, n2n)
        dd = [100*(sa[i]-sb_[i]) for i in R]
        T8.append({'area_id':aid,'area':NAME[aid], **fa, **fb, 'diff_no_vehicle_minus_with_vehicle_pp':round(dd[0],2), 'diff_moe90_pp':round(moe(dd),2), 'diff_tier':worst(ta,tb),
                   'tier_rule_note':'difference tier = worse of the two component share tiers',
                   'diff_unweighted_n':min(n1n, n2n), 'diff_cv':max(fa['independent_living_difficulty_no_vehicle_cv'], fb['independent_living_difficulty_with_vehicle_cv']),
                   'carried_n_cv_note':'run v1.1: difference n = smaller component n, CV = larger component CV (carried from the component shares; consistent with the weaker-tier rule)'})
    write_csv('t8_independent_living_difficulty_by_vehicle.csv', T8)
    # ================= lead finding (SAP s.9), by rule
    t4tot = [r for r in T4 if r['area_id']==TOT and r['age_group']=='65_plus'][0]
    lead = {}
    if t4tot['lives_alone_no_vehicle_cv'] <= 0.10:
        N = t4tot['lives_alone_no_vehicle']; x = round(t4tot['share_of_no_vehicle_65plus_living_alone_pct'],1)
        lead['rule1'] = f'T4 eight-area count used (CV {t4tot["lives_alone_no_vehicle_cv"]} <= 0.10)'
        lead['sentence1'] = f'An estimated {N:,} people 65 and older in eight U.S. study areas live alone in a household with no vehicle. Among older adults without a vehicle, {x:.1f}% live alone.'
    else:
        t1 = [r for r in T1 if r['area_id']==TOT][0]; t3 = [r for r in T3 if r['area_id']==TOT and r['group']=='no_vehicle' and r['category']=='lives_alone'][0]
        lead['rule1'] = 'T4 CV > 0.10; fallback to T1 count with T3 living-alone share'
        lead['sentence1'] = f'FALLBACK (template not specified in SAP for this case): T1 count {t1["no_vehicle_65plus"]:,}; T3 living-alone share {t3["share_pct"]:.1f}%'
    f2tot = [t for t in F2 if t['area_id']==TOT][0]; t5tot = [r for r in T5 if r['area_id']==TOT][0]
    half = lambda v: math.floor(v*2+0.5)/2
    if f2tot.get('remains_after_holm_10pct') and not f2tot.get('borderline'):
        k1 = half(t5tot['_crude_ratio_unrounded']); k2 = half(t5tot['_std_ratio_unrounded'])
        lead['rule2'] = 'eight-area F2 remains after Holm (not borderline): ratio sentence used'
        lead['sentence2'] = f'People 65 and older who live alone are about {k1:g} times as likely to have no household vehicle as those who live with others, about {k2:g} times after adjusting for age.'
        lead['k_inputs'] = {'crude_ratio':t5tot['crude_ratio'],'std_ratio':t5tot['std_ratio'],'k':k1,'k_prime':k2}
    else:
        t7tot = [r for r in T7 if r['area_id']==TOT][0]
        if t7tot['lives_alone_no_vehicle_walking_difficulty_cv'] <= 0.10:
            lead['rule2'] = 'eight-area F2 does not remain (or borderline); T7 count used'
            lead['sentence2'] = f'T7 count: {t7tot["lives_alone_no_vehicle_walking_difficulty"]:,} (sentence wording not specified in SAP)'
        else: lead['rule2'] = 'no second sentence (F2 not remaining and T7 CV > 0.10)'; lead['sentence2'] = ''
    lead['not_measured'] = 'These estimates do not directly measure missed medical appointments, transportation demand, wheelchair use, or unmet transportation needs.'
    lead['independent_living_line'] = 'Independent living difficulty is a self-reported difficulty doing errands alone, such as visiting a doctor\'s office or shopping; it is not a record of missed appointments.'
    log('LEAD 1: ' + lead['sentence1']); log('LEAD 2: ' + lead['sentence2'])
    RES.update(fragility_rule={'near_cut_band':[NEAR_CUT_LOW, CUT], 'fragile_F1':[t['area_id'] for t in F1 if t.get('fragile')], 'local_summary_eligible_F1':[t['area_id'] for t in F1 if t.get('local_summary_eligible')]}, headline_local_summary_exclusions={f"{t['family']} {t['area_id']}": t['headline_local_summary_exclusion_reason'] for t in F1+F2 if not t['headline_local_summary_eligible']}, lead=lead, T4_detail={a:{'rule':detail[a][0],'n':dict(detail[a][1])} for a in detail}, tenure_detail_n=tenure_detail_n, show_ten4=show_ten4,
               eligibility={'F1':{a:v[0] for a,v in elig1.items()},'F2':{a:v[0] for a,v in elig2.items()}}, t5_tot=dict((k,v) for k,v in t5tot.items()))
    (OUT/'run_results.json').write_text(json.dumps(RES, indent=2, default=str)+'\n')
    log(f'{VERSION} finished {datetime.datetime.now().astimezone().isoformat(timespec="seconds")}: all checks passed')
    (LOGD/'awac-run.log').write_text('\n'.join(LOG)+'\n')
if __name__ == '__main__': main()
