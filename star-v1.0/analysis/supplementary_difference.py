#!/usr/bin/env python3
"""Supplementary (part vs whole): per-area difference and ratio between share_amb_in_noveh_hh and
share_older_in_noveh_hh, with SDR replicate MOEs (computed replicate by replicate). Reuses estimate_joint.py.
v1.1 (validator note 2): --out option; default writes to rerun/ and the bundled outputs/ folder is never
overwritten unless --overwrite-bundled is given (release builds only).
Usage: python3 supplementary_difference.py [--out DIR] [--overwrite-bundled]"""
import json, pathlib, argparse
import estimate_joint as ej
B = pathlib.Path(__file__).resolve().parent

def out_dir(arg, overwrite):
    o = pathlib.Path(arg); o = o if o.is_absolute() else B/o
    if o.resolve() == (B/'outputs').resolve() and not overwrite:
        raise SystemExit('Refusing to overwrite bundled outputs/; pass --out DIR (default rerun/) or --overwrite-bundled')
    o.mkdir(parents=True, exist_ok=True); return o

def area_replicates():
    tp = ej.load_tract_puma(B/'inputs'/'tract_puma.txt')
    geo = {aid: ej.area_geography(tp, st, cs)[0] for aid,_,st,cs in ej.AREAS}
    allest = {}
    for st in sorted({a[2] for a in ej.AREAS}):
        est, _ = ej.accumulate_state(B/'inputs', st, {aid:set(geo[aid]) for aid,_,s,_ in ej.AREAS if s==st})
        allest.update(est)
    allest['eight_area_total'] = {k:[sum(allest[a][k][i] for a,*_ in ej.AREAS) for i in range(ej.NREP+1)] for k in ej.KEYS}
    return allest

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='rerun'); ap.add_argument('--overwrite-bundled', action='store_true')
    a = ap.parse_args(argv); o = out_dir(a.out, a.overwrite_bundled)
    allest = area_replicates(); out = []
    for aid in [a for a,*_ in ej.AREAS]+['eight_area_total']:
        e = allest[aid]
        s1 = [e['older_amb_noveh'][i]/e['older_amb'][i] for i in range(ej.NREP+1)]
        s2 = [e['older_noveh'][i]/e['older_hh'][i] for i in range(ej.NREP+1)]
        d = [100*(x-y) for x,y in zip(s1,s2)]; r = [x/y for x,y in zip(s1,s2)]
        out.append(dict(area_id=aid, diff_pp=round(d[0],2), diff_moe90_pp=round(1.645*ej.se(d),2),
                        ratio=round(r[0],2), ratio_moe90=round(1.645*ej.se(r),2),
                        diff_excludes_zero_at_90pct=abs(d[0]) > 1.645*ej.se(d)))
    (o/'supplementary_difference.json').write_text(json.dumps(out, indent=2)+'\n')
    for x in out: print(x)
if __name__=='__main__': main()
