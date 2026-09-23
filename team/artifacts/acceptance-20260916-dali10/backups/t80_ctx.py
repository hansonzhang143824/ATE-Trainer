import sys,io,os
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
t=open(os.path.join(d,'review-handoff-note-plan-side.md'),'rb').read().decode('utf-8-sig').split('\n')
print('=== the TWO occurrences of "is to become" (they report 1) ===')
for i,l in enumerate(t):
    if 'is to become' in l: print('  L%-5d %s'%(i+1,l.strip()[:185]))
print()
print('=== the TWO of "with rev 25" ===')
for i,l in enumerate(t):
    if 'with rev 25' in l: print('  L%-5d %s'%(i+1,l.strip()[:185]))
print()
print('=== the TWO of INTERSECTION / UNION/intersection ===')
for i,l in enumerate(t):
    if 'INTERSECTION' in l: print('  L%-5d %s'%(i+1,l.strip()[:185]))
print()
print('=== and what is immediately ABOVE the READING NOTE (the claimed operative sentence) ===')
idx=[i for i,l in enumerate(t) if 'READING NOTE' in l][0]
for i in range(max(0,idx-6),idx+2):
    print('  L%-5d %s'%(i+1,t[i].strip()[:175]))