# -*- coding: utf-8 -*-
"""t32 core verification: independent recomputation of the deployed result and the new-capability proof."""
import os, sys, json, re, hashlib, subprocess, datetime
sys.stdout.reconfigure(encoding='utf-8')

ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
RD = os.path.join(ROOT, 'team', 'artifacts', RUN)
TARGET = r"D:/PROJECT6-DALI/ForCodexDebug"
DEVEL = r"D:/PROJECT6-DALI/devel"

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''): h.update(c)
    return h.hexdigest()

def rt(p):
    raw = open(p, 'rb').read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try: return raw.decode(enc)
        except Exception: pass
    return raw.decode('utf-8', errors='replace')

def strip_comments(src):
    """Remove // line comments and /* */ block comments; keep string literals intact textually."""
    out = []
    i, n = 0, len(src)
    in_line = in_block = in_str = None
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ''
        if in_line:
            if c == '\n':
                in_line = False; out.append(c)
            i += 1; continue
        if in_block:
            if c == '*' and nxt == '/':
                in_block = False; i += 2; continue
            if c == '\n': out.append(c)
            i += 1; continue
        if in_str:
            out.append(c)
            if c == '\\': out.append(nxt); i += 2; continue
            if c == in_str: in_str = None
            i += 1; continue
        if c == '/' and nxt == '/': in_line = True; i += 2; continue
        if c == '/' and nxt == '*': in_block = True; i += 2; continue
        if c in ('"', "'"): in_str = c; out.append(c); i += 1; continue
        out.append(c); i += 1
    return ''.join(out)

def func_block(text, name):
    m = re.search(r'DUT_API\s+int\s+' + re.escape(name) + r'\s*\(', text)
    if not m: return None, None, None
    brace = text.find('{', m.end())
    depth = 0
    for pos in range(brace, len(text)):
        if text[pos] == '{': depth += 1
        elif text[pos] == '}':
            depth -= 1
            if depth == 0:
                start_line = text.count('\n', 0, m.start()) + 1
                end_line = text.count('\n', 0, pos) + 1
                return text[m.start():pos + 1], start_line, end_line
    return text[m.start():], text.count('\n', 0, m.start()) + 1, None

report = {'extractedAt': datetime.datetime.now().astimezone().isoformat(timespec='seconds')}

# ---------------------------------------------------------------- deployed
tgt_test = os.path.join(TARGET, 'source', 'test.cpp')
deployed = rt(tgt_test)
deployed_sha = sha(tgt_test)
dstrip = strip_comments(deployed)
print('=== deployed test.cpp ===')
print('  size', os.path.getsize(tgt_test), 'sha256', deployed_sha)
print('  lines', deployed.count('\n') + 1, '| BOM', deployed.startswith('\ufeff'))
report['deployed'] = {'path': 'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp', 'sizeBytes': os.path.getsize(tgt_test),
                      'sha256': deployed_sha, 'lines': deployed.count('\n') + 1, 'bom': deployed.startswith('\ufeff')}

counts = {}
for tok in ('TM600_HS_RDSON', 'TM601_LS_RDSON', 'TM600', 'TM601', 'RDSON'):
    counts[tok] = {'raw': deployed.count(tok), 'commentsStripped': dstrip.count(tok)}
print('  token counts (raw / comments-stripped):', json.dumps(counts))
report['tokenCounts'] = counts

INVARIANTS = [
    ('delay_ms(1)', r'delay_ms\(1\)'),
    ('delay_ms(2)', r'delay_ms\(2\)'),
    ('SetClamp(50,50)', r'SetClamp\(\s*50\s*,\s*50\s*\)'),
    ('MeasureVI(200,5,FPVIe_MV_X10)', r'MeasureVI\(\s*200\s*,\s*5\s*,\s*FPVIe_MV_X10\s*\)'),
    ('bare 126', r'(?<![0-9A-Za-z_])126(?![0-9A-Za-z_])'),
    ('K126_V1P5_CAP', r'K126_V1P5_CAP'),
    ('ERROR_RES', r'ERROR_RES'),
    ('K5_VBUS_Cap', r'K5_VBUS_Cap'),
    ('K44_Cap_SW2_BST2', r'K44_Cap_SW2_BST2'),
    ('K45_Cap_SW1_BST1', r'K45_Cap_SW1_BST1'),
    ('K57_CAP_BST_SW', r'K57_CAP_BST_SW'),
    ('K109_BUSL1_PB0', r'K109_BUSL1_PB0'),
    ('K110_ACM18_BST', r'K110_ACM18_BST'),
    ('rampi_capv-or-rampv_capv', r'rampi_capv\s*\(|rampv_capv\s*\('),
    ('K_FPVIH_TO_BST_B', r'K_FPVIH_TO_BST_B'),
    ('K83_BUSH0_PMID', r'K83_BUSH0_PMID'),
]
inv = {}
print('  invariants (comments-stripped):')
for label, pat in INVARIANTS:
    c = len(re.findall(pat, dstrip))
    inv[label] = c
    print('    %-32s %d' % (label, c))
report['invariantsCommentsStripped'] = inv
report['invariantsExpected'] = {'delay_ms(1)': 6, 'delay_ms(2)': 0, 'SetClamp(50,50)': 2,
                                'MeasureVI(200,5,FPVIe_MV_X10)': 2, 'bare 126': 0, 'K126_V1P5_CAP': 2, 'ERROR_RES': 2}

# ---------------------------------------------------------------- functions + SetOn
print()
print('=== TM600 / TM601 function blocks ===')
fns = {}
for name in ('TM600_HS_RDSON', 'TM601_LS_RDSON'):
    blk, s, e = func_block(deployed, name)
    fns[name] = {'found': blk is not None, 'startLine': s, 'endLine': e, 'blockChars': len(blk) if blk else 0}
    print('  %-18s found=%s lines %s-%s' % (name, blk is not None, s, e))
    if blk:
        seton = re.findall(r'cbite\.SetOn\((.*?)\)\s*;', blk, re.DOTALL)
        for i, so in enumerate(seton, 1):
            toks = [t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1']
            print('    SetOn[%d] relays: %s' % (i, toks))
        fns[name]['setOnCalls'] = [[t.strip() for t in so.split(',') if t.strip() and t.strip() != '-1'] for so in seton]
        for tok in ('K109', 'K110', 'K83', 'K60', 'K61', 'K126_V1P5_CAP', 'K57_CAP_BST_SW'):
            fns[name][tok] = blk.count(tok)
    report.setdefault('functions', {})[name] = fns[name]

# ---------------------------------------------------------------- baseline (pre-change)
print()
print('=== baseline proof ===')
bak = os.path.join(RD, 'backups', 'test.cpp.before_TM600_TM601.bak')
btxt = rt(bak)
print('  bak size', os.path.getsize(bak), 'sha256', sha(bak))
for tok in ('TM600', 'TM601', 'RDSON'):
    print('    %-8s hits=%d' % (tok, btxt.count(tok)))
report['baseline'] = {'path': 'team/artifacts/%s/backups/test.cpp.before_TM600_TM601.bak' % RUN,
                      'sizeBytes': os.path.getsize(bak), 'sha256': sha(bak),
                      'hits': {t: btxt.count(t) for t in ('TM600', 'TM601', 'RDSON')}}

# ---------------------------------------------------------------- golden non-copy proof
print()
print('=== golden non-copy proof ===')
gold = os.path.join(ROOT, 'knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp')
gtxt = rt(gold)
gb = open(gold, 'rb').read()
print('  golden size', len(gb), 'sha256', sha(gold))
def norm(s):
    s = s.replace('\ufeff', '').replace('\r\n', '\n').replace('\r', '\n')
    return re.sub(r'\s+', ' ', s).strip()
gflat = norm(gtxt)
# longest common substring between flattened golden and flattened payload regions
pl = [os.path.join(RD, 'implementation-payload-TM600-TM601.cpp'),
      os.path.join(TARGET, 'source', 'test.cpp')]
common = []
for p in pl:
    ptxt = rt(p)
    # search a few distinctive golden lines in the candidate
    probes = [l.strip() for l in gtxt.splitlines() if l.strip().startswith(('FPVI.Set(', 'FPVI.MeasureVI(', 'VBAT_ACM.Set', 'BTST_ACM.Set', 'PMID_FOVI.Set'))]
    hit = [q for q in probes if q in ptxt]
    common.append({'path': p.replace(ROOT, '.').replace('\\', '/'), 'goldenDistinctiveLinesProbed': len(probes), 'hits': hit})
    print('  %s -> probed %d golden lines, hits %d %s' % (common[-1]['path'], len(probes), len(hit), hit[:3]))
report['goldenNonCopy'] = {'golden': {'path': 'knowledge/references/L4-Golden-code/tm600-normal-highcurrent.cpp',
                                      'sizeBytes': len(gb), 'sha256': sha(gold)},
                           'probeResults': common}

# ---------------------------------------------------------------- devel zero-write
print()
print('=== devel vs target (zero-write) ===')
zw = {}
for rel in (('source', 'test.cpp'), ('source', 'StdAfx.h'), ('source', 'sub.cpp'), ('source', 'Pin_Channel_define.h')):
    a = os.path.join(TARGET, *rel); b = os.path.join(DEVEL, *rel)
    zw['/'.join(rel)] = {'target': sha(a), 'devel': sha(b), 'identical': sha(a) == sha(b),
                         'targetSize': os.path.getsize(a), 'develSize': os.path.getsize(b)}
    print('  %-28s identical=%-5s target=%s devel=%s' % ('/'.join(rel), zw['/'.join(rel)]['identical'],
                                                          zw['/'.join(rel)]['target'][:12], zw['/'.join(rel)]['devel'][:12]))
report['develZeroWrite'] = zw

out = os.path.join(RD, 't32-recompute-evidence.json')
with open(out, 'w', encoding='utf-8') as f:
    json.dump(report, f, ensure_ascii=False, indent=1)
print()
print('wrote', out, os.path.getsize(out))
