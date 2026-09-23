import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
p=r'D:\Newtest\DSH\ATE-Coding-Plat\knowledge\sources\fpvie.md'
t=open(p,'rb').read().decode('utf-8-sig',errors='replace')
lines=t.split('\n')
for i,l in enumerate(lines):
    if 'MeasureVI' in l and ('##' in l or 'samplePeriod' in l or 'sampleTimes' in l):
        print('anchor %d: %s'%(i+1,l.strip()[:120]))
print('---- 6.4.5 MeasureVI block ----')
start=None
for i,l in enumerate(lines):
    if l.strip().startswith('## 6.4.5'): start=i
if start is not None:
    for i in range(start,min(start+46,len(lines))): print('%d: %s'%(i+1,lines[i].rstrip()[:130]))