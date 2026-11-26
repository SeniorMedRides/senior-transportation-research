#!/usr/bin/env python3
"""SeniorMedRides first-phase SENSITIVITY + COMPARISONS (INTERNAL, UNREVIEWED, pending independent validation).

Reuses estimate_joint.py (same frozen inputs, same definitions: AGEP>=65, TYPEHUGQ=='1', DPHY=='1', VEH=='0',
PWGTP + PWGTP1..80, SDR SE = sqrt(4/80*sum((Xr-X)^2)), MOE90 = 1.645*SE). Adds an age-group dimension:
65-74, 75-84, 85+ (AGEP is top-coded in PUMS; top-coding does not affect the 85+ group).

A. Age-specific counts and shares by area and age group.
B. Direct age standardization. Standard population (fixed constants, documented in output):
   PRIMARY  S1 = age distribution of ALL persons 65+ in the universe, eight areas combined (full-sample weights).
            Applied to BOTH shares, so the ratio compares like with like.
   ALT      S2 = age distribution of persons 65+ WITH ambulatory difficulty, eight areas combined; applied to the
            share-of-ambulatory-group measure only (sensitivity check).
   std_share = sum_g S_g * share_g, computed in every replicate; SE from the 80 replicate values.
C. Pre-specified comparisons (plan fixed in this file before the tests were run; see PLAN below).
Stdlib only. Usage (from this folder): python3 age_sensitivity.py
"""
import sys, csv, json, math, pathlib, collections
BASE = pathlib.Path(__file__).resolve().parent; ROOT = BASE.parent
sys.path.insert(0, str(ROOT)); import estimate_joint as ej

GROUPS = [('65_74',65,74),('75_84',75,84),('85_plus',85,999)]
NR = ej.NREP; R = range(NR+1)
ALPHA = 0.10   # familywise error rate for Holm (matches 90% intervals used throughout)
PLAN = {
 'family_1_primary': 'Each area vs the other seven areas pooled (no overlap), for three age-standardized (S1) measures: '
   '(a) share of 65+ with ambulatory difficulty in a no-vehicle household, (b) share of all 65+ in a no-vehicle household, '
   '(c) ratio a/b. 8 areas x 3 measures = 24 two-sided z-tests (difference / replicate SE of difference). Holm step-down, familywise alpha=0.10.',
 'family_2_secondary': 'All 28 pairwise area differences in measure (a), age-standardized (S1). Holm, familywise alpha=0.10.',
 'family_3_within_area_gap': 'Within each area and the eight-area total: age-standardized (a) minus (b) (9 tests). Holm, familywise alpha=0.10.',
 'notes': 'Plan written before running the tests but after crude estimates had been seen (disclosed). Boise is the Boise PUMA region throughout. '
          'Normal approximation; p two-sided. Differences/ratios computed replicate by replicate.'}

def age_group(a):
    for g,lo,hi in GROUPS:
        if lo <= a <= hi: return g
    return None

def accumulate_by_age(inputs, st, area_pumas):
    puma_area = {p:a for a,ps in area_pumas.items() for p in ps}
    hu = {a:{} for a in area_pumas}
    z,f = ej.open_csv_in_zip(inputs/'pums'/f'csv_h{ej.STATES[st]}.zip','psam_h')
    with z,f:
        r = csv.reader(f); h = next(r); i_s,i_p,i_t,i_v = (h.index(c) for c in ['SERIALNO','PUMA','TYPEHUGQ','VEH'])
        for row in r:
            a = puma_area.get(row[i_p])
            if a and row[i_t]=='1': hu[a][row[i_s]] = row[i_v]
    est = {a:{g:{k:[0.0]*(NR+1) for k in ej.KEYS} for g,_,_ in GROUPS} for a in area_pumas}
    n = {a:{g:collections.Counter() for g,_,_ in GROUPS} for a in area_pumas}
    z,f = ej.open_csv_in_zip(inputs/'pums'/f'csv_p{ej.STATES[st]}.zip','psam_p')
    with z,f:
        r = csv.reader(f); h = next(r)
        ix = {c:h.index(c) for c in ['SERIALNO','PUMA','AGEP','DPHY','PWGTP']}; iw=[h.index(f'PWGTP{i}') for i in range(1,NR+1)]
        for row in r:
            a = puma_area.get(row[ix['PUMA']])
            if not a: continue
            fl = ej.flags({'SERIALNO':row[ix['SERIALNO']],'AGEP':row[ix['AGEP']],'DPHY':row[ix['DPHY']]}, hu[a])
            if not fl: continue
            g = age_group(int(row[ix['AGEP']])); w=[float(row[ix['PWGTP']])]+[float(row[i]) for i in iw]
            for k,v in fl.items():
                if v:
                    n[a][g][k]+=1; e=est[a][g][k]
                    for i in R: e[i]+=w[i]
    return est, n

def vadd(*vs): return [sum(v[i] for v in vs) for i in R]
def vsub(a,b): return [a[i]-b[i] for i in R]
def vdiv(a,b): return [a[i]/b[i] for i in R]
def moe(v): return 1.645*ej.se(v)
def pval(v):
    s = ej.se(v); z = v[0]/s if s else float('inf')
    return z, math.erfc(abs(z)/math.sqrt(2))
def holm(tests, alpha=ALPHA):
    m = len(tests); order = sorted(range(m), key=lambda i: tests[i]['p']); stop=False; adj_prev=0
    for rank,i in enumerate(order):
        thr = alpha/(m-rank); adj = min(1.0, max(adj_prev, (m-rank)*tests[i]['p'])); adj_prev = adj
        if not stop and tests[i]['p'] <= thr: tests[i]['holm_significant']=True
        else: stop=True; tests[i]['holm_significant']=False
        tests[i]['holm_threshold']=thr; tests[i]['holm_adjusted_p']=adj
    return tests

def main():
    inputs = ROOT/'inputs'; tp = ej.load_tract_puma(inputs/'tract_puma.txt')
    ids = [a for a,*_ in ej.AREAS]; names = {}
    geo = {}
    for aid,label,st,cs in ej.AREAS:
        p,exact,extra,_ = ej.area_geography(tp,st,cs); geo[aid]=(st,set(p))
        names[aid] = label if exact else 'Boise PUMA region'
    est={}; n={}
    for st in sorted({g[0] for g in geo.values()}):
        e,c = accumulate_by_age(inputs, st, {a:geo[a][1] for a in ids if geo[a][0]==st}); est.update(e); n.update(c)
    G=[g for g,_,_ in GROUPS]
    est['eight_area_total'] = {g:{k:vadd(*[est[a][g][k] for a in ids]) for k in ej.KEYS} for g in G}
    n['eight_area_total'] = {g:sum((n[a][g] for a in ids), collections.Counter()) for g in G}
    T = est['eight_area_total']
    S1 = {g:T[g]['older_hh'][0] for g in G}; s=sum(S1.values()); S1={g:v/s for g,v in S1.items()}
    S2 = {g:T[g]['older_amb'][0] for g in G}; s=sum(S2.values()); S2={g:v/s for g,v in S2.items()}
    areas = ids+['eight_area_total']
    def shares(e):
        a = {g:vdiv(e[g]['older_amb_noveh'],e[g]['older_amb']) for g in G}
        b = {g:vdiv(e[g]['older_noveh'],e[g]['older_hh']) for g in G}
        return a,b
    def std(sh,S): return [sum(S[g]*sh[g][i] for g in G) for i in R]
    def crude(e,num,den): return vdiv(vadd(*[e[g][num] for g in G]), vadd(*[e[g][den] for g in G]))
    M={}  # replicate vectors per area for comparisons
    age_rows=[]; std_rows=[]
    for aid in areas:
        e=est[aid]; a,b=shares(e)
        for g in G:
            c=n[aid][g]
            age_rows.append(dict(area_id=aid, area=names.get(aid,'Eight study areas combined (incl. Boise PUMA region)'), age_group=g,
              older_hh=round(e[g]['older_hh'][0]), older_hh_moe90=round(moe(e[g]['older_hh'])), older_hh_unweighted_n=c['older_hh'],
              older_amb=round(e[g]['older_amb'][0]), older_amb_moe90=round(moe(e[g]['older_amb'])), older_amb_unweighted_n=c['older_amb'],
              older_amb_noveh=round(e[g]['older_amb_noveh'][0]), older_amb_noveh_moe90=round(moe(e[g]['older_amb_noveh'])), older_amb_noveh_unweighted_n=c['older_amb_noveh'],
              older_noveh=round(e[g]['older_noveh'][0]), older_noveh_moe90=round(moe(e[g]['older_noveh'])), older_noveh_unweighted_n=c['older_noveh'],
              amb_prevalence_pct=round(100*e[g]['older_amb'][0]/e[g]['older_hh'][0],2), amb_prevalence_moe90_pp=round(100*moe(vdiv(e[g]['older_amb'],e[g]['older_hh'])),2),
              share_amb_in_noveh_hh_pct=round(100*a[g][0],2), share_amb_in_noveh_hh_moe90_pp=round(100*moe(a[g]),2),
              share_older_in_noveh_hh_pct=round(100*b[g][0],2), share_older_in_noveh_hh_moe90_pp=round(100*moe(b[g]),2),
              ratio=round(a[g][0]/b[g][0],2), ratio_moe90=round(moe(vdiv(a[g],b[g])),2),
              small_n_flag='small unweighted n (<50)' if c['older_amb_noveh']<50 else 'none'))
        ca=crude(e,'older_amb_noveh','older_amb'); cb=crude(e,'older_noveh','older_hh')
        sa=std(a,S1); sb=std(b,S1); sa2=std(a,S2)
        M[aid]=dict(a=sa,b=sb,r=vdiv(sa,sb))
        row=dict(area_id=aid, area=names.get(aid,'Eight study areas combined (incl. Boise PUMA region)'))
        for key,v in [('crude_share_amb_in_noveh_hh',ca),('std_share_amb_in_noveh_hh',sa),('std_alt_share_amb_in_noveh_hh',sa2),
                      ('crude_share_older_in_noveh_hh',cb),('std_share_older_in_noveh_hh',sb)]:
            row[key+'_pct']=round(100*v[0],2); row[key+'_moe90_pp']=round(100*moe(v),2)
        for key,v in [('crude_ratio',vdiv(ca,cb)),('std_ratio',vdiv(sa,sb))]:
            row[key]=round(v[0],2); row[key+'_moe90']=round(moe(v),2)
        d=vsub(sa,sb); row['std_gap_pp']=round(100*d[0],2); row['std_gap_moe90_pp']=round(100*moe(d),2)
        # share of universe that is 85+ (age-mix descriptor)
        row['pct_of_65plus_aged_85plus']=round(100*e['85_plus']['older_hh'][0]/sum(e[g]['older_hh'][0] for g in G),2)
        row['pct_of_65plus_aged_85plus_moe90_pp']=round(100*moe(vdiv(e['85_plus']['older_hh'],vadd(*[e[g]['older_hh'] for g in G]))),2)
        std_rows.append(row); M[aid]['_gap']=d
    # comparisons
    def test(label, family, measure, v, scale):
        z,p=pval(v); return dict(family=family, measure=measure, comparison=label, estimate=round(scale*v[0],2), moe90=round(scale*moe(v),2), z=round(z,2), p=p)
    # rest-of-seven pooled standardized measures
    f1=[]
    for aid in ids:
        rest={g:{k:vadd(*[est[o][g][k] for o in ids if o!=aid]) for k in ej.KEYS} for g in G}
        ra,rb=shares(rest); rsa=std(ra,S1); rsb=std(rb,S1)
        f1.append(test(f'{aid} minus other seven','1','std share of 65+ w/ ambulatory difficulty in no-vehicle HH (pp)',vsub(M[aid]['a'],rsa),100))
        f1.append(test(f'{aid} minus other seven','1','std share of all 65+ in no-vehicle HH (pp)',vsub(M[aid]['b'],rsb),100))
        f1.append(test(f'{aid} minus other seven','1','std ratio (difference in ratio)',vsub(M[aid]['r'],vdiv(rsa,rsb)),1))
    f2=[test(f'{a} minus {b}','2','std share of 65+ w/ ambulatory difficulty in no-vehicle HH (pp)',vsub(M[a]['a'],M[b]['a']),100)
        for i,a in enumerate(ids) for b in ids[i+1:]]
    f3=[test(f'{aid}: std share (amb) minus std share (all 65+)','3','within-area gap (pp)',M[aid]['_gap'],100) for aid in areas]
    tests=holm(f1)+holm(f2)+holm(f3)
    for t in tests: t['p']=float(f"{t['p']:.3g}"); t['holm_adjusted_p']=float(f"{t['holm_adjusted_p']:.3g}"); t['holm_threshold']=float(f"{t['holm_threshold']:.4g}")
    out=BASE/'outputs'; out.mkdir(exist_ok=True)
    def wcsv(name, rows):
        with open(out/name,'w',newline='') as f:
            w=csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    wcsv('age_specific.csv',age_rows); wcsv('age_standardized.csv',std_rows); wcsv('comparisons.csv',tests)
    json.dump(dict(status='INTERNAL, UNREVIEWED, pending independent validation; not for publication or outreach',
        standard_population_S1={g:round(v,6) for g,v in S1.items()}, standard_population_S2={g:round(v,6) for g,v in S2.items()},
        standard_note='S1 = eight-area combined weighted persons 65+ in housing units by age group; S2 = same, restricted to DPHY=1. Treated as fixed constants (standard not re-estimated in replicates).',
        plan=PLAN, alpha=ALPHA, age_specific=age_rows, age_standardized=std_rows, comparisons=tests), open(out/'sensitivity.json','w'), indent=2)
    print('S1',S1,'\nS2',S2)
    for r in std_rows: print(r)
    for t in tests: print(t['family'],t['measure'][:30],t['comparison'],t['estimate'],'±',t['moe90'],'p=',t['p'],'sig' if t['holm_significant'] else '')
if __name__=='__main__': main()
