import sys,io,re,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10\implementation-payload-TM600-TM601.cpp'
raw=open(p,'rb').read(); t=raw.decode('utf-8-sig')
lines=t.split('\n')
print('payload',len(raw),'B',hashlib.sha256(raw).hexdigest())
print()
print('=== every FPVI0.Set line with its line number ===')
for i,l in enumerate(lines):
    if re.search(r'FPVI0\.Set\(',l) and not l.strip().startswith('//'):
        print('  %4d: %s'%(i+1,l.strip()[:115]))