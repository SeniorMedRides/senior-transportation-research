#!/usr/bin/env python3
"""v1.1 supplementary contrast (validator note 3): people 65+ WITH vs WITHOUT ambulatory difficulty.
INTERNAL. Same frozen inputs and definitions as estimate_joint.py (AGEP>=65, TYPEHUGQ=='1', DPHY, VEH=='0', PWGTP + 80 SDR replicates).
  with    : share_with    = older_amb_noveh / older_amb
  without : share_without = (older_noveh - older_amb_noveh) / (older_hh - older_amb)   [DPHY=='2' in the universe]
  difference (pp) = 100*(share_with - share_without); ratio = share_with / share_without
All computed replicate by replicate; SE = sqrt(4/80*sum((Xr-X)^2)); MOE90 = 1.645*SE.
Usage: python3 with_without_contrast.py [--out DIR] [--overwrite-bundled]  (default out: rerun/)"""
import json, csv, argparse
import estimate_joint as ej
from supplementary_difference import area_replicates, out_dir
R = range(ej.NREP+1)
NAME = {aid:('Boise PUMA region' if aid=='boise' else lab) for aid,lab,_,_ in ej.AREAS}; NAME['eight_area_total']='Eight study areas combined (incl. Boise PUMA region)'

def contrast(e):
    wo_n = [e['older_noveh'][i]-e['older_amb_noveh'][i] for i in R]; wo_d = [e['older_hh'][i]-e['older_amb'][i] for i in R]
    sw = [e['older_amb_noveh'][i]/e['older_amb'][i] for i in R]; so = [wo_n[i]/wo_d[i] for i in R]
    d = [100*(sw[i]-so[i]) for i in R]; r = [sw[i]/so[i] for i in R]
    m = lambda v: 1.645*ej.se(v)
    return dict(older_without_amb=round(wo_d[0]), older_without_amb_moe90=round(m(wo_d)),
                older_without_amb_noveh=round(wo_n[0]), older_without_amb_noveh_moe90=round(m(wo_n)),
                share_with_amb_in_noveh_hh_pct=round(100*sw[0],2), share_with_amb_in_noveh_hh_moe90_pp=round(100*m(sw),2),
                share_without_amb_in_noveh_hh_pct=round(100*so[0],2), share_without_amb_in_noveh_hh_moe90_pp=round(100*m(so),2),
                diff_with_minus_without_pp=round(d[0],2), diff_with_minus_without_moe90_pp=round(m(d),2),
                ratio_with_to_without=round(r[0],2), ratio_with_to_without_moe90=round(m(r),2),
                diff_exceeds_moe90=abs(d[0]) > m(d)), (wo_n, wo_d, sw, so)

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument('--out', default='rerun'); ap.add_argument('--overwrite-bundled', action='store_true')
    a = ap.parse_args(argv); o = out_dir(a.out, a.overwrite_bundled)
    allest = area_replicates(); rows = []
    for aid in [x for x,*_ in ej.AREAS]+['eight_area_total']:
        c,_ = contrast(allest[aid]); rows.append(dict(area_id=aid, area=NAME[aid], **c))
    (o/'with_without_contrast.json').write_text(json.dumps({'status':'INTERNAL; v1.1 supplementary contrast; not yet independently validated by the author pipeline (validator reported matching figures)','definitions':__doc__.split('Usage')[0].strip(),'results':rows}, indent=2)+'\n')
    with open(o/'with_without_contrast.csv','w',newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    for r in rows: print(r['area_id'], r['share_with_amb_in_noveh_hh_pct'], r['share_without_amb_in_noveh_hh_pct'], '±', r['share_without_amb_in_noveh_hh_moe90_pp'], r['diff_with_minus_without_pp'], '±', r['diff_with_minus_without_moe90_pp'], r['ratio_with_to_without'], '±', r['ratio_with_to_without_moe90'], r['diff_exceeds_moe90'])
if __name__=='__main__': main()
