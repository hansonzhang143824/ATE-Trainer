import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig').split('\n')
print('=== the ONE surviving INTERSECTION / UNION/intersection occurrence (they report 0) ===')
for i,l in enumerate(t):
    if 'INTERSECTION' in l or 'UNION/intersection' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:210]))
print()
print('=== and the forward-looking [48,61,76] line, with its two neighbours ===')
for i in range(420,426):
    if i<len(t): print('  L%-5d %s'%(i+1,t[i].strip()[:200]))