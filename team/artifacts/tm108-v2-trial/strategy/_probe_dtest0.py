# read-only probe: DTEST0 token search across the schematic three-artifact set and connect map (t4)
import io
import os
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

TARGETS = ['DTEST0', 'DTEST', 'dtest']
FILES = [
    'project/DALI/SCH-Connect-Map.txt',
    'project/DALI/Component-Statistic.txt',
    'project/DALI/schematic-ir.json',
    'project/DALI/input/PINLIST.txt',
]
for f in FILES:
    try:
        txt = io.open(f, encoding='utf-8', errors='replace').read()
    except Exception as e:  # noqa
        print('%s READ-FAIL %s' % (f, e))
        continue
    lines = txt.splitlines()
    print('--- %s : bytes=%d lines=%d' % (f, os.path.getsize(f), len(lines)))
    for t in TARGETS:
        hits = [(i, l.strip()[:120]) for i, l in enumerate(lines, 1) if t in l]
        print('    token %-8s hits=%d %s' % (t, len(hits), hits[:4]))
