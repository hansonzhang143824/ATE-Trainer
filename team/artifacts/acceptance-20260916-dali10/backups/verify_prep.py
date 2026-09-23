import sys,io,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementer-t5-prep.md'
raw=open(p,'rb').read()
print('prep bytes',len(raw),'tsz',raw[:4]==b'TSZ#','sha256',hashlib.sha256(raw).hexdigest())
t=raw.decode('utf-8-sig'); print('lines',t.count('\n')+1)
print('## 9 heading present:','## 9. CURRENT-DISK HASHES' in t)
print('43ad8c84 present:','43ad8c84' in t)
print('ad9859e9 mentioned as unresolved:','ad9859e9' in t)
print('sections:',[m.group(1) for m in re.finditer(r'^#{2,3} (\d+(?:\.\d+)*)',t,re.M)][:34])