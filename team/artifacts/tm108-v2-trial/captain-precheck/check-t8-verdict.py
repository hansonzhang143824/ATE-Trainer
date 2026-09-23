# Independently verify the load-bearing claims of the t8 verdict (RF-01, RF-02, RF-03, RF-04).
import hashlib, json, os, re

A = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
TGT = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
MP = os.path.join(A, 'implementation', 'implementation-manifest.json')
FJ = os.path.join(A, 'review', 't8-review-findings.json')


def h(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


print('live test.cpp sha256_pl :', h(TGT))
print('manifest sha256         :', h(MP))
print('findings.json sha256    :', h(FJ))
print()

L = open(TGT, 'rb').read().decode('utf-8-sig', errors='replace').split('\n')
s = next(i for i, l in enumerate(L) if 'DUT_API int TM108_HSKP_VAC1_PRST' in l)
e = next(j for j in range(s + 1, len(L)) if L[j].rstrip('\r') == '}')
body = L[s:e + 1]
print('TM108 body lines        :', s + 1, '-', e + 1)
print('SetTestResult in body   :', sum(1 for l in body if 'SetTestResult' in l))
print('Step headings in TM108  :', [re.search(r'Step \d', l).group(0) for l in body if re.search(r'Step \d', l)])

for nm in ('TM107', 'TM109'):
    i = next(k for k, l in enumerate(L) if nm in l and l.startswith('DUT_API int '))
    j = next(k for k in range(i + 1, len(L)) if L[k].rstrip('\r') == '}')
    print('%s step headings      : %s' % (nm, [re.search(r'Step \d', l).group(0) for l in L[i:j + 1] if re.search(r'Step \d', l)]))

print()
print('--- RF-02 sentences (framework-release asserted as fact) ---')
for k in list(range(2177, 2181)) + list(range(2285, 2292)):
    print('  %4d| %s' % (k + 1, L[k].rstrip()[:155]))

print()
R3 = open(os.path.join(A, 'method', 'tm108-test-method-contract.md'), 'rb').read().decode('utf-8-sig', errors='replace')
parts = R3.split('\n## 6.')
print('R3 split on "## 6." parts:', len(parts))
if len(parts) > 1:
    rows = [l for l in parts[1].split('\n') if l.strip().startswith('|') and '---' not in l]
    print('R3 section-6 table rows :', len(rows))
    for r in rows[:14]:
        print('   ', r.strip()[:130])
