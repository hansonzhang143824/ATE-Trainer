import hashlib, os, json

SRC = r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp'
DST = r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\tm108-v2-trial\review\copy\test.cpp'

with open(SRC, 'rb') as f:
    b = f.read()
os.makedirs(os.path.dirname(DST), exist_ok=True)
with open(DST, 'wb') as f:
    f.write(b)
with open(DST, 'rb') as f:
    c = f.read()
print('src sha256', hashlib.sha256(b).hexdigest())
print('cpy sha256', hashlib.sha256(c).hexdigest())
print('byte-identical:', b == c, 'len', len(b), len(c))

# decode as utf-8-sig, keep CRLF structure
txt = b.decode('utf-8-sig')
lines = txt.split('\r\n')
print('lines(CRLF-split):', len(lines))
