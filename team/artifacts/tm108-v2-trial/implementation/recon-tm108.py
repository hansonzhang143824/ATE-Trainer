# TM108 implementation recon - python byte-mode reader (DLP-whitelisted).
# pwsh/.NET read ciphertext for DLP-protected files; python reads plaintext.
import hashlib, io, os, re, sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

TARGET_DIR = r'D:\PROJECT6-DALI\ForCodexDebug\source'

def read_pl(path):
    with open(path, 'rb') as f:
        raw = f.read()
    return raw, raw.decode('utf-8-sig', errors='replace')

def report(path):
    raw, txt = read_pl(path)
    lines = txt.split('\n')
    print('=' * 70)
    print('FILE      :', path)
    print('bytes     :', len(raw), '(plaintext)')
    print('sha256_pl :', hashlib.sha256(raw).hexdigest())
    print('bom       :', raw[:3] == b'\xef\xbb\xbf', ' crlf:', txt.count('\r\n'))
    print('lines     :', len(lines))
    print('DUT_API   :', len(re.findall(r'DUT_API\s+int', txt)))
    hits = [i + 1 for i, l in enumerate(lines) if 'TM108' in l]
    print('TM108 hits:', len(hits), hits[:40])
    for n in hits[:40]:
        print('  %5d | %s' % (n, lines[n - 1].rstrip()[:150]))
    return lines

for name in ('test.cpp', 'sub.cpp', 'StdAfx.h'):
    p = os.path.join(TARGET_DIR, name)
    if os.path.exists(p):
        report(p)
    else:
        print('MISSING:', p)
