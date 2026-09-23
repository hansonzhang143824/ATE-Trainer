# -*- coding: utf-8 -*-
import json, sys, os
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
d = json.load(open(os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'overview-dft.json'), encoding='utf-8'))
rows = d['overview']['rows']
for r in rows:
    print('=' * 90)
    print(r.get('_scopeBase'), r.get('Item'), 'excelRow=', r.get('_excelRow'))
    for k, v in r.items():
        if k.startswith('_') or v is None:
            continue
        print('  %-14s %s' % (k, repr(v)))
print()
print('#### DFT.csv records ####')
for r in d['dftCsv']['records']:
    print('=' * 90)
    print('line', r['line'], r['base'])
    print(r['raw'])
