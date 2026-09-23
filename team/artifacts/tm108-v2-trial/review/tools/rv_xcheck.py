import os, hashlib

BASE = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial'
BEFORE = os.path.join(BASE, 'implementation', 'backup', 'tm108-v2-impl__test.cpp.before')
BLOCK = os.path.join(BASE, 'captain-precheck', 'tm108-block-before.txt')

bb = open(BEFORE, 'rb').read()
tb = bb.decode('utf-8-sig')
Lb = tb.split('\n')
Lb = [x[:-1] if x.endswith('\r') else x for x in Lb]
if Lb and Lb[-1] == '':
    Lb = Lb[:-1]

cb = open(BLOCK, 'rb').read()
tc = cb.decode('utf-8-sig')
Lc = tc.split('\n')
Lc = [x[:-1] if x.endswith('\r') else x for x in Lc]
if Lc and Lc[-1] == '':
    Lc = Lc[:-1]

print('backup lines', len(Lb), 'captain block lines', len(Lc))
print('captain block sha256', hashlib.sha256(cb).hexdigest())

# try to locate Lc as a contiguous slice of Lb
target = Lc
found = None
for start in range(0, len(Lb) - len(target) + 1):
    if Lb[start:start + len(target)] == target:
        found = start
        break
if found is None:
    print('NOT a contiguous slice of the backup -- searching loosest match')
    # compare ignoring trailing whitespace
    norm = [x.rstrip() for x in target]
    for start in range(0, len(Lb) - len(target) + 1):
        if [x.rstrip() for x in Lb[start:start + len(target)]] == norm:
            found = start
            print('  (matched after rstrip) start index', start)
            break
if found is not None:
    print('MATCH: captain block == backup lines %d..%d (1-based)' % (found + 1, found + len(target)))
else:
    print('MISMATCH - first differing line vs assumed offset 2146:')
    for i in range(min(len(Lc), 81)):
        a = Lb[2146 + i] if 2146 + i < len(Lb) else '<none>'
        b = Lc[i]
        if a != b:
            print('  line %d:\n    backup: %r\n    block : %r' % (2147 + i, a, b))
            break
    print('  block[0:3]:', Lc[:3])
    print('  backup[2146:2149]:', Lb[2146:2149])
