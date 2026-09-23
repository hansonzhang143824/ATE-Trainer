# -*- coding: utf-8 -*-
"""DFT extraction (t1 evidence source): dump OVERVIEW rows for the 10 in-scope TMs,
plus DFT.csv records, to a JSON intermediate under team/artifacts/<run-id>/dft-raw/.

Reads via python byte mode (DLP-authorized plaintext).
"""
import os, json, re, hashlib, sys

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
OUTDIR = os.path.join(ROOT, "team", "artifacts", RUN, "dft-raw")
os.makedirs(OUTDIR, exist_ok=True)

def p(*a): return os.path.join(ROOT, *a)

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

def clean(v):
    if v is None: return None
    if isinstance(v, str):
        s = v.replace('\r\n', '\n').rstrip()
        return s if s != '' else None
    return v

SCOPE = ["TM000", "TM001", "TM102", "TM103", "TM108", "TM109", "TM135", "TM600", "TM601", "TM1205"]

def base_of(item):
    m = re.match(r'^(TM\d+)', str(item))
    return m.group(1) if m else None

result = {"runId": RUN, "generatedBy": "scripts/_dft_extract.py"}

# ---------- OVERVIEW ----------
import openpyxl
xlsx = p('project', 'DALI', 'Dali_testmode.xlsx')
wb = openpyxl.load_workbook(xlsx, read_only=True, data_only=True)
ws = wb['OVERVIEW']
rows = list(ws.iter_rows(values_only=True))
wb.close()
header = [clean(h) for h in rows[0]]
overview = []
for ridx, r in enumerate(rows[1:], start=2):
    if r is None or all(c is None for c in r): continue
    rec = {}
    for i, h in enumerate(header):
        key = h if h else ("col%d" % i)
        rec[key] = clean(r[i]) if i < len(r) else None
    rec["_excelRow"] = ridx
    b = base_of(rec.get("Item"))
    if b in SCOPE:
        into = "base" if rec.get("Item") == b else "variant"
        rec["_scopeBase"] = b
        rec["_scopeKind"] = into
        overview.append(rec)

result["overview"] = {"file": "project/DALI/Dali_testmode.xlsx", "sheet": "OVERVIEW",
                      "sha256": sha256_file(xlsx), "header": header, "sourceRowCount": len(rows) - 1,
                      "rows": overview}

# ---------- DFT.csv ----------
csvp = p('project', 'DALI', 'input', 'DFT.csv')
raw = open(csvp, 'rb').read()
txt, enc = decode(raw)
lines = txt.split('\n')
csv_recs = []
for i, line in enumerate(lines, start=1):
    b = base_of(line)
    if b in SCOPE:
        csv_recs.append({"line": i, "base": b, "raw": line.replace('\r', '')})
result["dftCsv"] = {"file": "project/DALI/input/DFT.csv", "sha256": sha256_file(csvp),
                    "encoding": enc, "lineCount": len(lines), "records": csv_recs}

# ---------- DFT_restored.csv (secondary) ----------
rp = p('project', 'DALI', 'input', 'DFT_restored.csv')
if os.path.exists(rp):
    raw2 = open(rp, 'rb').read()
    t2, e2 = decode(raw2)
    recs2 = []
    for i, line in enumerate(t2.split('\n'), start=1):
        b = base_of(line)
        if b in SCOPE:
            recs2.append({"line": i, "base": b, "raw": line.replace('\r', '')})
    result["dftRestoredCsv"] = {"file": "project/DALI/input/DFT_restored.csv", "sha256": sha256_file(rp),
                                "encoding": e2, "lineCount": len(t2.split('\n')), "records": recs2}

out = os.path.join(OUTDIR, "overview-dft.json")
with open(out, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)
print("wrote", out)
print("overview rows for scope:", len(overview))
for r in overview:
    print("  ", r.get("Item"), "|", r.get("Level"), "|", r.get("Name"), "|", r.get("Test"), "|", r.get("Special"))
print("dft.csv scope recs:", len(csv_recs))
print("dft_restored scope recs:", len(result.get("dftRestoredCsv", {}).get("records", [])))
