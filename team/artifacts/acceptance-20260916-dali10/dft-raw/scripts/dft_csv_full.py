# -*- coding: utf-8 -*-
"""DFT.csv full record extraction (proper RFC4180 parse; cells contain embedded newlines)."""
import os, json, re, hashlib, csv, io, sys
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
OUTDIR = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1 << 20), b''):
            h.update(chunk)
    return h.hexdigest()

def decode(raw):
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc), enc
        except Exception: pass
    return raw.decode('utf-8', errors='replace'), 'replace'

for name in ('DFT.csv', 'DFT_restored.csv'):
    path = os.path.join(ROOT, 'project', 'DALI', 'input', name)
    raw = open(path, 'rb').read()
    txt, enc = decode(raw)
    rdr = csv.reader(io.StringIO(txt))
    rows = list(rdr)
    print('=' * 100)
    print(name, 'sha256', sha256_file(path), 'encoding', enc, 'records', len(rows) - 1)
    header = rows[0]
    print('header:', header)
    items = []
    for i, r in enumerate(rows[1:], start=2):
        if not r or all(c.strip() == '' for c in r):
            continue
        item = r[0].strip()
        items.append(item)
        if re.match(r'^TM(000|001|102|103|108|109|135|600|601|1205)\b', item):
            rec = {'csvRecord': i, 'item': item}
            for k, v in zip(header, r):
                rec[k] = v
            print('-' * 100)
            print(json.dumps(rec, ensure_ascii=False, indent=1))
    out = os.path.join(OUTDIR, name.replace('.csv', '') + '-full.json')
    with open(out, 'w', encoding='utf-8') as f:
        json.dump({'file': 'project/DALI/input/' + name, 'sha256': sha256_file(path),
                   'encoding': enc, 'header': header,
                   'rows': [dict(zip(header, r)) | {'_record': i} for i, r in enumerate(rows[1:], start=2)]},
                  f, ensure_ascii=False, indent=2)
    print('wrote', out)
    print('all items:', items[:60])
