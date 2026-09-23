# Captain-side pre-change baseline for t7 (independent of the implementer's own manifest).
# Purpose: after t7 reports DONE, the manifest's beforeSha256 / scope claims can be checked against
# this record instead of being taken on trust.
# Reader: python byte mode (DLP plaintext). Never pwsh/.NET for these files.
import hashlib, io, json, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET = r'D:\PROJECT6-DALI\ForCodexDebug\source'
OUT = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\captain-precheck\t7-pre-change-baseline.json'
SYMBOL = 'DUT_API int TM108_HSKP_VAC1_PRST'

rec = {'runId': 'tm108-v2-impl', 'task': 't7', 'recordedBy': 'captain',
       'reader': 'python byte mode (DLP plaintext)', 'files': {}}

for name in ('test.cpp', 'sub.cpp', 'StdAfx.h'):
    p = os.path.join(TARGET, name)
    if not os.path.exists(p):
        continue
    raw = open(p, 'rb').read()
    txt = raw.decode('utf-8-sig', errors='replace')
    lines = txt.split('\n')
    ent = {
        'path': p,
        'bytes': len(raw),
        'sha256_plaintext': hashlib.sha256(raw).hexdigest(),
        'utf8_bom': raw[:3] == b'\xef\xbb\xbf',
        'crlf_count': txt.count('\r\n'),
        'line_count': len(lines),
        'dut_api_count': len(re.findall(r'DUT_API\s+int', txt)),
    }
    if name == 'test.cpp':
        start = next((i for i, l in enumerate(lines) if SYMBOL in l), None)
        end = None
        if start is not None:
            for j in range(start + 1, len(lines)):
                if lines[j].rstrip('\r') == '}':
                    end = j
                    break
        ent['tm108'] = {
            'symbol': SYMBOL,
            'start_line': (start + 1) if start is not None else None,
            'end_line': (end + 1) if end is not None else None,
            'comment_line': next((i + 1 for i, l in enumerate(lines) if l.lstrip().startswith('// TM108:')), None),
            'occurrence_lines': [i + 1 for i, l in enumerate(lines) if 'TM108' in l],
        }
        if start is not None and end is not None:
            block = ''.join(lines[start:end + 1])
            ent['tm108']['block_sha256_plaintext'] = hashlib.sha256(block.encode('utf-8')).hexdigest()
            ent['tm108']['block_line_count'] = end - start + 1
    rec['files'][name] = ent
    print(name, ent['sha256_plaintext'], ent['bytes'], 'bytes', ent.get('tm108', {}).get('start_line'),
          ent.get('tm108', {}).get('end_line'))

os.makedirs(os.path.dirname(OUT), exist_ok=True)
with open(OUT, 'w', encoding='utf-8') as f:
    json.dump(rec, f, indent=2)
print('WROTE', OUT)
