#!/usr/bin/env python3
"""v1.1 (validator note 3, sensitivity): age-specific and directly age-standardized contrast between people 65+
WITH and WITHOUT ambulatory difficulty in the no-vehicle-household share. INTERNAL; not yet independently validated.
Reuses age_sensitivity.py (accumulate_by_age, same frozen inputs/definitions). Standard = S1, the eight-area
age distribution of ALL persons 65+ in the universe (same constant as age_sensitivity.py), applied to BOTH shares.
  share_with_g    = older_amb_noveh_g / older_amb_g
  share_without_g = (older_noveh_g - older_amb_noveh_g) / (older_hh_g - older_amb_g)
  std = sum_g S1_g * share_g in every replicate; SDR SE; MOE90 = 1.645*SE. Writes to outputs/ (new files only).
Usage (from sensitivity/): python3 with_without_std.py"""
import csv, json, pathlib
import age_sensitivity as a
ej = a.ej; R = a.R; G = [g for g,_,_ in a.GROUPS]
B = pathlib.Path(__file__).resolve().parent
def main():
    inputs = a.ROOT/'inputs'; tp = ej.load_tract_puma(inputs/'tract_puma.txt'); ids=[x for x,*_ in ej.AREAS]
    geo={aid:(st,set(ej.area_geography(tp,st,cs)[0])) for aid,_,st,cs in ej.AREAS}
    est={}; n={}
    for st in sorted({g[0] for g in geo.values()}):
        e,c=a.accumulate_by_age(inputs, st, {x:geo[x][1] for x in ids if geo[x][0]==st}); est.update(e); n.update(c)
    est['eight_area_total']={g:{k:a.vadd(*[est[x][g][k] for x in ids]) for k in ej.KEYS} for g in G}
    n['eight_area_total']={g:sum((n[x][g] for x in ids), a.collections.Counter()) for g in G}
    T=est['eight_area_total']; S1={g:T[g]['older_hh'][0] for g in G}; s=sum(S1.values()); S1={g:v/s for g,v in S1.items()}
    m=a.moe; NAME={aid:('Boise PUMA region' if aid=='boise' else lab) for aid,lab,_,_ in ej.AREAS}; NAME['eight_area_total']='Eight study areas combined (incl. Boise PUMA region)'
    by_age=[]; std_rows=[]
    for aid in ids+['eight_area_total']:
        e=est[aid]
        sw={g:a.vdiv(e[g]['older_amb_noveh'],e[g]['older_amb']) for g in G}
        so={g:a.vdiv(a.vsub(e[g]['older_noveh'],e[g]['older_amb_noveh']),a.vsub(e[g]['older_hh'],e[g]['older_amb'])) for g in G}
        for g in G:
            d=[100*(sw[g][i]-so[g][i]) for i in R]; r=a.vdiv(sw[g],so[g])
            by_age.append(dict(area_id=aid, area=NAME[aid], age_group=g,
                share_with_amb_in_noveh_hh_pct=round(100*sw[g][0],2), share_with_amb_in_noveh_hh_moe90_pp=round(100*m(sw[g]),2),
                share_without_amb_in_noveh_hh_pct=round(100*so[g][0],2), share_without_amb_in_noveh_hh_moe90_pp=round(100*m(so[g]),2),
                diff_with_minus_without_pp=round(d[0],2), diff_with_minus_without_moe90_pp=round(m(d),2),
                ratio_with_to_without=round(r[0],2), ratio_with_to_without_moe90=round(m(r),2),
                with_amb_noveh_unweighted_n=n[aid][g]['older_amb_noveh'],
                small_n_flag='small unweighted n (<50)' if n[aid][g]['older_amb_noveh']<50 else 'none'))
        tot=lambda k:a.vadd(*[e[g][k] for g in G])
        cw=a.vdiv(tot('older_amb_noveh'),tot('older_amb')); co=a.vdiv(a.vsub(tot('older_noveh'),tot('older_amb_noveh')),a.vsub(tot('older_hh'),tot('older_amb')))
        stw=[sum(S1[g]*sw[g][i] for g in G) for i in R]; sto=[sum(S1[g]*so[g][i] for g in G) for i in R]
        row=dict(area_id=aid, area=NAME[aid])
        for k,v in [('crude_share_with',cw),('std_share_with',stw),('crude_share_without',co),('std_share_without',sto)]:
            row[k+'_pct']=round(100*v[0],2); row[k+'_moe90_pp']=round(100*m(v),2)
        for k,(x,y) in [('crude',(cw,co)),('std',(stw,sto))]:
            d=[100*(x[i]-y[i]) for i in R]; r=a.vdiv(x,y)
            row[k+'_diff_pp']=round(d[0],2); row[k+'_diff_moe90_pp']=round(m(d),2); row[k+'_diff_exceeds_moe90']=abs(d[0])>m(d)
            row[k+'_ratio']=round(r[0],2); row[k+'_ratio_moe90']=round(m(r),2)
        std_rows.append(row)
    for f,rows in [('with_without_std.csv',std_rows),('with_without_by_age.csv',by_age)]:
        with open(B/'outputs'/f,'w',newline='') as fh:
            w=csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows)
    json.dump(dict(status='INTERNAL; v1.1; not yet independently validated', standard_population_S1={g:round(v,6) for g,v in S1.items()},
                   definitions=__doc__.split('Usage')[0].strip(), age_standardized=std_rows, by_age=by_age), open(B/'outputs'/'with_without_std.json','w'), indent=2)
    for r in std_rows: print(r['area_id'], r['crude_share_with_pct'], r['crude_share_without_pct'], r['crude_diff_pp'],'±',r['crude_diff_moe90_pp'], r['crude_ratio'],'±',r['crude_ratio_moe90'],'| std', r['std_share_with_pct'],'±',r['std_share_with_moe90_pp'], r['std_share_without_pct'],'±',r['std_share_without_moe90_pp'], r['std_diff_pp'],'±',r['std_diff_moe90_pp'], r['std_ratio'],'±',r['std_ratio_moe90'], r['std_diff_exceeds_moe90'])
    for r in by_age:
        if r['area_id']=='eight_area_total': print(r)
if __name__=='__main__': main()
