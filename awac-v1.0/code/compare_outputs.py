#!/usr/bin/env python3
"""Run v1.2 proof that no estimate changed: every output CSV, run_results.json and web item of an earlier run (v1 and v1.1) is compared value by value
with this run. Estimate, MOE, n, CV, tier, test and wording columns must be identical; columns may be added. The only values allowed to differ are the
reporting-status fields that David's 14 Nov 2026 4:40 PM rule changes (listed in REPORTING_FIELDS); every such change is listed in the report.
Usage: python3 compare_outputs.py [RUN_V1_DIR RUN_V1_1_DIR]  (defaults ../../run-v1 ../../run-v1.1). Writes logs/v1.2-vs-v1-and-v1.1-output-diff-report.md"""
import csv, json, sys, pathlib
RUN = pathlib.Path(__file__).resolve().parent.parent
BASES = [pathlib.Path(p).resolve() for p in sys.argv[1:3]] if len(sys.argv) > 2 else [RUN.parent/'run-v1', RUN.parent/'run-v1.1']
REPORTING_FIELDS = {'headline_local_summary_eligible', 'headline_local_summary_exclusion_reason', 'f1_comparison_headline_local_summary', 'f1_exclusion_reason',
                    'headline_exclusions_f1', 'headline_local_summary_exclusions', 'version'}
L = ['# Run v1.2 vs run v1 and run v1.1: output comparison', '',
     'Rule: every earlier estimate, MOE, n, CV, tier, test-result and wording cell identical; new columns additive. Only the reporting-status fields changed by David P. Faustina\'s 14 Nov 2026 4:40 PM rule may differ, and each such change is listed.', '']
bad = []
def walk(x, y, path, out):
    if isinstance(x, dict):
        for k in x:
            if k not in y: out.append((path+'.'+k, 'removed', None))
            elif k in REPORTING_FIELDS:
                if x[k] != y[k]: out.append((path+'.'+k, x[k], y[k]))
            else: walk(x[k], y[k], f'{path}.{k}', out)
    elif isinstance(x, list) and isinstance(y, list) and len(x) == len(y):
        for i, (xi, yi) in enumerate(zip(x, y)): walk(xi, yi, f'{path}[{i}]', out)
    elif x != y: out.append((path, x, y))
for base in BASES:
    L += [f'## vs {base.name}', '', '| File | Rows earlier / v1.2 | Cells compared | Estimate/test differences | Reporting-status changes | Columns added in v1.2 |', '| --- | --- | --- | --- | --- | --- |']
    tot = d_tot = 0; rep_changes = []
    for f in sorted((base/'outputs').glob('*.csv')):
        a = list(csv.DictReader(open(f))); b = list(csv.DictReader(open(RUN/'outputs'/f.name)))
        if len(a) != len(b): bad.append(f'{base.name} {f.name}: row count')
        n = d = rc = 0
        for ra, rb in zip(a, b):
            for c in ra:
                n += 1
                if c not in rb: bad.append(f'{base.name} {f.name}: column {c} removed'); continue
                if ra[c] != rb[c]:
                    if c in REPORTING_FIELDS: rc += 1; rep_changes.append(f'{f.name} {ra.get("area_id","")} {c}: {ra[c]!r} → {rb[c]!r}')
                    else: d += 1; bad.append(f'{base.name} {f.name} {ra.get("area_id","")} {c}: {ra[c]!r} -> {rb[c]!r}')
        tot += n; d_tot += d
        L.append(f'| {f.name} | {len(a)} / {len(b)} | {n} | {d} | {rc} | {", ".join(c for c in b[0] if c not in a[0]) or "none"} |')
    ja = json.load(open(base/'outputs'/'run_results.json')); jb = json.load(open(RUN/'outputs'/'run_results.json')); jr = []
    walk(ja, jb, 'run_results', jr)
    wr = []
    for name in ('area-pages.json', 'report-page.json'):
        walk({'items': json.load(open(base/'web-data'/name))}, {'items': json.load(open(RUN/'web-data'/name))}, name, wr)
    for path, x, y in jr + wr:
        if path.split('.')[-1].split('[')[0] in REPORTING_FIELDS: rep_changes.append(f'{path}: {x!r} → {y!r}')
        else: bad.append(f'{base.name} {path}: {x!r} -> {y!r}')
    L += ['', f'**{base.name}: {tot} CSV cells compared; estimate/test differences: {d_tot}.** run_results.json and web items compared field by field; non-reporting differences: {sum(1 for p,_,_ in jr+wr if p.split(".")[-1].split("[")[0] not in REPORTING_FIELDS)}. Keys added to run_results.json: {", ".join(k for k in jb if k not in ja) or "none"}.', '',
          f'Reporting-status changes vs {base.name} ({len(rep_changes)}):', ''] + [f'- {c}' for c in rep_changes] + ['']
L.append('RESULT: ' + ('NO ESTIMATE, MOE, n, CV, TIER OR TEST RESULT CHANGED' if not bad else f'DIFFERENCES FOUND ({len(bad)})'))
L += [f'- {p}' for p in bad[:200]]
out = '\n'.join(L) + '\n'; (RUN/'logs'/'v1.2-vs-v1-and-v1.1-output-diff-report.md').write_text(out); print(out[-1500:])
raise SystemExit(1 if bad else 0)
