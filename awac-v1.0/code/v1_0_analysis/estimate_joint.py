#!/usr/bin/env python3
"""SeniorMedRides first-phase production script (INTERNAL, UNREVIEWED until independent validation).

Joint estimate from ACS 2020-2024 5-year PUMS: people age 65+ in housing units who have ambulatory
difficulty (DPHY=1) AND live in a household with no vehicle (VEH=0), for eight study areas,
reading the frozen official zip files directly (no manual unzip step).

Definitions
  universe        : person records with AGEP>=65 whose SERIALNO matches a housing record with TYPEHUGQ=='1'
                    (housing unit; group quarters excluded) in a selected 2020 PUMA
  older_hh        : all persons in universe
  older_amb       : universe & DPHY=='1'
  older_amb_noveh : universe & DPHY=='1' & VEH=='0'
  older_noveh     : universe & VEH=='0'
Variance: 80 successive-difference replicate weights PWGTP1..PWGTP80
  SE = sqrt(4/80 * sum_r (X_r - X_0)^2), MOE90 = 1.645*SE. Ratios use the same formula on replicate ratios.
Rounding (as feasibility script): counts and count MOEs round(); shares in percent round(...,2).
Stdlib only. Usage: python3 estimate_joint.py [--inputs inputs] [--out outputs]
"""
import csv, io, json, math, sys, zipfile, collections, pathlib, argparse

STATES = {'04':'az','06':'ca','12':'fl','16':'id','32':'nv','49':'ut'}
AREAS = [  # (area_id, label if exact nesting, state FIPS, county FIPS set)
 ('phoenix','Phoenix (Maricopa County, AZ)','04',{'04013'}),
 ('tampa','Tampa (Hillsborough, Pinellas, Pasco counties, FL)','12',{'12057','12103','12101'}),
 ('orlando','Orlando (Orange, Seminole, Osceola counties, FL)','12',{'12095','12117','12097'}),
 ('boise','Boise (Ada, Canyon counties, ID)','16',{'16001','16027'}),
 ('sacramento','Sacramento (Sacramento, Placer counties, CA)','06',{'06067','06061'}),
 ('stockton','Stockton (San Joaquin County, CA)','06',{'06077'}),
 ('salt_lake_city','Salt Lake City (Salt Lake, Davis counties, UT)','49',{'49035','49011'}),
 ('las_vegas','Las Vegas (Clark County, NV)','32',{'32003'}),
]
COUNTY_NAMES = {'16045':'Gem','16075':'Payette','16087':'Washington','16073':'Owyhee'}
KEYS = ['older_hh','older_amb','older_amb_noveh','older_noveh']
NREP = 80
SMALL_N = 50          # analyst flag: unweighted n below this is "small n"
CV_FLAG = 0.30        # analyst flag: CV above 30% is "high uncertainty"

def se(v):
    """Successive-difference replicate SE. v[0]=full-sample estimate, v[1..80]=replicates."""
    return math.sqrt(4/NREP*sum((v[i]-v[0])**2 for i in range(1,NREP+1)))

def load_tract_puma(path):
    tp = collections.defaultdict(set)
    with open(path, encoding='utf-8-sig') as f:
        for x in csv.DictReader(f):
            tp[(x['STATEFP'],x['PUMA5CE'])].add(x['STATEFP']+x['COUNTYFP'])
    return tp

def area_geography(tp, st, counties):
    pumas = sorted(p for (s,p),cs in tp.items() if s==st and cs & counties)
    covered = set().union(*(tp[(st,p)] for p in pumas)) if pumas else set()
    extra = sorted(covered - counties)
    missing = sorted(c for c in counties if c not in covered)
    return pumas, len(extra)==0 and not missing, extra, missing

def flags(person, hu_veh):
    """Return membership flags for one person record (dict-like) or None if outside universe."""
    if person['SERIALNO'] not in hu_veh: return None          # GQ, other PUMA, or unmatched
    if int(person['AGEP']) < 65: return None
    amb = person['DPHY'] == '1'; nov = hu_veh[person['SERIALNO']] == '0'
    return {'older_hh':True,'older_amb':amb,'older_amb_noveh':amb and nov,'older_noveh':nov}

def open_csv_in_zip(zpath, member_prefix):
    z = zipfile.ZipFile(zpath)
    name = [n for n in z.namelist() if n.startswith(member_prefix) and n.endswith('.csv')]
    assert len(name)==1, (zpath, name)
    return z, io.TextIOWrapper(z.open(name[0]), encoding='utf-8', newline='')

def accumulate_state(inputs, st, area_pumas):
    """One pass over a state's housing then person file. area_pumas: {area_id: set(pumas)}."""
    ab = STATES[st]; puma_area = {}
    for a, ps in area_pumas.items():
        for p in ps:
            assert p not in puma_area, f'PUMA {p} assigned to two areas'
            puma_area[p] = a
    hu = {a:{} for a in area_pumas}
    z, f = open_csv_in_zip(inputs/'pums'/f'csv_h{ab}.zip', 'psam_h')
    with z, f:
        r = csv.reader(f); h = next(r); i_s, i_p, i_t, i_v = (h.index(c) for c in ['SERIALNO','PUMA','TYPEHUGQ','VEH'])
        for row in r:
            a = puma_area.get(row[i_p])
            if a and row[i_t]=='1': hu[a][row[i_s]] = row[i_v]
    est = {a:{k:[0.0]*(NREP+1) for k in KEYS} for a in area_pumas}
    n = {a:collections.Counter() for a in area_pumas}
    z, f = open_csv_in_zip(inputs/'pums'/f'csv_p{ab}.zip', 'psam_p')
    with z, f:
        r = csv.reader(f); h = next(r)
        ix = {c:h.index(c) for c in ['SERIALNO','PUMA','AGEP','DPHY','PWGTP']}
        iw = [h.index(f'PWGTP{i}') for i in range(1,NREP+1)]
        for row in r:
            a = puma_area.get(row[ix['PUMA']])
            if not a: continue
            fl = flags({'SERIALNO':row[ix['SERIALNO']],'AGEP':row[ix['AGEP']],'DPHY':row[ix['DPHY']]}, hu[a])
            if not fl: continue
            w = [float(row[ix['PWGTP']])]+[float(row[i]) for i in iw]
            for k,v in fl.items():
                if v:
                    n[a][k]+=1; e=est[a][k]
                    for i in range(NREP+1): e[i]+=w[i]
    return est, n

def summarize(est, n):
    out = {}
    for k in KEYS:
        s = se(est[k]); x = est[k][0]
        out[k]=round(x); out[k+'_moe90']=round(1.645*s); out[k+'_unweighted_n']=n[k]
        out[k+'_cv']=round(s/x,4) if x else None
        out['_unrounded_'+k]=x; out['_unrounded_'+k+'_se']=s
    for name,num,den in [('share_amb_in_noveh_hh','older_amb_noveh','older_amb'),('share_older_in_noveh_hh','older_noveh','older_hh')]:
        r=[est[num][i]/est[den][i] for i in range(NREP+1)]; s=se(r)
        out[name+'_pct']=round(100*r[0],2); out[name+'_moe90_pp']=round(100*1.645*s,2)
        out['_unrounded_'+name]=r[0]; out['_unrounded_'+name+'_se']=s
    j=out['older_amb_noveh_unweighted_n']; cv=out['older_amb_noveh_cv']
    out['reliability_flag'] = ('small unweighted n (<%d)'%SMALL_N if j<SMALL_N else '') + ('; ' if j<SMALL_N and cv and cv>CV_FLAG else '') + ('CV > 30%' if cv and cv>CV_FLAG else '') or 'none'
    return out

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--inputs', default='inputs'); ap.add_argument('--out', default='outputs')
    ap.add_argument('--states', default=None, help='comma list of state FIPS to run (testing)')
    a = ap.parse_args(argv); base = pathlib.Path(__file__).resolve().parent
    inputs = (base/a.inputs) if not pathlib.Path(a.inputs).is_absolute() else pathlib.Path(a.inputs)
    outdir = (base/a.out) if not pathlib.Path(a.out).is_absolute() else pathlib.Path(a.out); outdir.mkdir(parents=True, exist_ok=True)
    tp = load_tract_puma(inputs/'tract_puma.txt')
    geo = {}
    for aid,label,st,cs in AREAS:
        pumas, exact, extra, missing = area_geography(tp, st, cs)
        lab = label if exact else ('Boise PUMA region (Ada, Canyon PUMAs; also covers parts of ' + ', '.join(COUNTY_NAMES.get(c,c) for c in extra) + ' counties)' if aid=='boise' else label+' PUMA-extended region; extra counties: '+', '.join(extra))
        geo[aid]=dict(area_id=aid,area=lab,state_fips=st,study_counties=sorted(cs),pumas=pumas,pumas_exactly_nest_in_counties=exact,extra_counties_in_pumas=extra,study_counties_missing=missing)
    want = set(a.states.split(',')) if a.states else set(STATES)
    results = {}; totals = {k:[0.0]*(NREP+1) for k in KEYS}; tot_n = collections.Counter()
    for st in sorted({g['state_fips'] for g in geo.values()} & want):
        aps = {aid:set(g['pumas']) for aid,g in geo.items() if g['state_fips']==st}
        est, n = accumulate_state(inputs, st, aps)
        for aid in aps:
            results[aid] = {**geo[aid], **summarize(est[aid], n[aid])}
            for k in KEYS:
                tot_n[k]+=n[aid][k]
                for i in range(NREP+1): totals[k][i]+=est[aid][k][i]
    ordered = [results[aid] for aid,*_ in AREAS if aid in results]
    if len(ordered)==len(AREAS):
        t = summarize(totals, tot_n)
        t.update(area_id='eight_area_total', area='Eight study areas combined (Boise counted as Boise PUMA region, not exact Ada+Canyon)', state_fips='multiple', study_counties=[], pumas=[], pumas_exactly_nest_in_counties=False, extra_counties_in_pumas=geo['boise']['extra_counties_in_pumas'], study_counties_missing=[],
                 total_method='Replicate-by-replicate sum of area estimates across all 81 weights, then the same SDR formula (no RSS independence assumption needed). Areas share no PUMAs.')
        ordered.append(t)
    meta = {'dataset':'ACS 2020-2024 5-year PUMS (csv_p??.zip, csv_h??.zip)','status':'INTERNAL, UNREVIEWED working estimates pending independent validation; not for publication or outreach',
            'definitions':__doc__.split('Definitions')[1].split('Stdlib')[0].strip()}
    (outdir/'joint_estimates.json').write_text(json.dumps({'meta':meta,'results':ordered}, indent=2)+'\n')
    # v1.1 (validator note 1): header is the union of keys across rows so total_method (total row only) is kept
    pub = list(dict.fromkeys(k for r in ordered for k in r if not k.startswith('_')))
    with (outdir/'joint_estimates.csv').open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=pub, extrasaction='ignore', lineterminator='\n'); w.writeheader()
        for r in ordered: w.writerow({k:(';'.join(v) if isinstance(v,list) else v) for k,v in r.items()})
    for r in ordered:
        print(f"{r['area_id']:16s} {r['older_amb_noveh']:>8,} ±{r['older_amb_noveh_moe90']:>6,} n={r['older_amb_noveh_unweighted_n']:>5} | amb share {r['share_amb_in_noveh_hh_pct']:5.2f}±{r['share_amb_in_noveh_hh_moe90_pp']:.2f} | all65 {r['share_older_in_noveh_hh_pct']:5.2f}±{r['share_older_in_noveh_hh_moe90_pp']:.2f} | exact={r['pumas_exactly_nest_in_counties']} flag={r['reliability_flag']}")

if __name__=='__main__': main()
