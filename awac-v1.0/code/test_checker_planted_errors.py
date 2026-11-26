#!/usr/bin/env python3
"""Planted-error tests: each plant must make check_consistency_awac.py fail with the expected code. Works on a scratch copy in /tmp."""
import shutil, subprocess, pathlib, tempfile, json, csv
RUN = pathlib.Path(__file__).resolve().parent.parent
PLANTS = [('B', 'summary', 'Older adults here are stranded.'), ('A', 'summary', 'Many are lonely.'), ('W', 'summary', 'Seniors without a car need help.'),
          ('K', 'summary', 'Tampa has the highest share.'), ('K', 'summary', 'This is a significant gap.'), ('G', 'summary', 'In Boise the share is lower.'),
          ('P', 'summary', 'Data cover 2020-2024.'), ('N', 'summary', 'An estimated 123,457 people.'), ('L', 'lead', None), ('F', 'f1', None), ('R', 't3', None), ('U', 'web', None),
          ('H', 'orlando', None), ('H', 'lvrow', None), ('C', 't5carry', None),
          ('H', 'boiselocal', None), ('H', 'tampaheadline', None), ('H', 'phoenixlocal', None)]  # run v1.2 additions  # run v1.1 additions
ok = True
for code, where, text in PLANTS:
    d = pathlib.Path(tempfile.mkdtemp())/'run'; shutil.copytree(RUN, d, ignore=shutil.ignore_patterns('repro_v1_0','*.zip','validation-package-dee-c','__pycache__'))
    s = d/'docs'/'technical-summary-methods-results-run-v1.2.md'
    if where == 'summary': s.write_text(s.read_text() + '\n' + text + '\n')
    elif where == 'lead':
        r = json.load(open(d/'outputs'/'run_results.json')); r['lead']['sentence1'] = r['lead']['sentence1'].replace('65.1%', '65.2%'); (d/'outputs'/'run_results.json').write_text(json.dumps(r))
    elif where in ('f1','t3'):
        f = d/'outputs'/('f1_tests_area_vs_other_seven.csv' if where=='f1' else 't3_profile_no_vehicle_vs_with_vehicle.csv'); rows = list(csv.DictReader(open(f)))
        if where == 'f1': rows[0]['remains_after_holm_10pct'] = 'False' if rows[0]['remains_after_holm_10pct']=='True' else 'True'
        else:
            i = next(i for i,r in enumerate(rows) if r['share_tier']=='Suppressed'); rows[i]['share_pct_display'] = rows[i]['share_pct']
        fh = open(f,'w',newline=''); w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows); fh.close()
    elif where == 'orlando':
        f = d/'outputs'/'f1_tests_area_vs_other_seven.csv'; rows = list(csv.DictReader(open(f)))
        for r in rows:
            if r['area_id']=='orlando': r['headline_local_summary_eligible'] = 'True'
        fh = open(f,'w',newline=''); w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows); fh.close()
    elif where == 'lvrow':
        t = s.read_text().split('\n'); t = [l.replace('S2', 'XX') if l.startswith('| Las Vegas |') and 'other seven' in l else l for l in t]; s.write_text('\n'.join(t))
    elif where == 't5carry':
        f = d/'outputs'/'t5_no_vehicle_living_alone_vs_not.csv'; rows = list(csv.DictReader(open(f))); rows[0]['crude_diff_ratio_unweighted_n'] = '999999'
        fh = open(f,'w',newline=''); w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows); fh.close()
    elif where == 'boiselocal':
        f = d/'outputs'/'f1_tests_area_vs_other_seven.csv'; rows = list(csv.DictReader(open(f)))
        for r in rows:
            if r['area_id']=='boise': r['local_summary_eligible'] = 'True'
        fh = open(f,'w',newline=''); w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows); fh.close()
    elif where == 'phoenixlocal':
        f = d/'outputs'/'f1_tests_area_vs_other_seven.csv'; rows = list(csv.DictReader(open(f)))
        for r in rows:
            if r['area_id']=='phoenix': r['local_summary_eligible'] = 'False'; r['local_summary_claim'] = 'none: pending David'
        fh = open(f,'w',newline=''); w = csv.DictWriter(fh, fieldnames=list(rows[0]), lineterminator='\n'); w.writeheader(); w.writerows(rows); fh.close()
    elif where == 'tampaheadline':
        j = d/'web-data'/'area-pages.json'; x = json.load(open(j))
        for it in x:
            if it['area_id']=='tampa': it['f1_headline_eligible'] = True
        j.write_text(json.dumps(x))
    elif where == 'web':
        j = d/'web-data'/'area-pages.json'; x = json.load(open(j)); x[0]['meta_description'] += ' ' + 'x'*80; j.write_text(json.dumps(x))
    p = subprocess.run(['python3', str(d/'code'/'check_consistency_awac.py')], capture_output=True, text=True)
    caught = p.returncode == 1 and f'[{code}]' in p.stdout
    ok &= caught; print(('CAUGHT ' if caught else 'MISSED ') + code + ' ' + (text or where))
    shutil.rmtree(d.parent)
print('RESULT:', 'PASS' if ok else 'FAIL'); raise SystemExit(0 if ok else 1)
