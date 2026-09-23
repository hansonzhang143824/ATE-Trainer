import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); L=t.split('\n')
h=hashlib.sha256(r).hexdigest()
print('=== file identity ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 67,206 B / 63dc3ba0... @23:07:57 -> match:', h=='63dc3ba0bd121e93a8982d0008c7d4bc0b6250edfca3026a7afb2ae6305a155d')
print()
print('=== their claims, re-measured ON THESE BYTES ===')
claims=[('"is to become" occurrences','1',t.count('is to become')),
        ('"with rev 25" occurrences','2 (L519-520? and L535)',t.count('with rev 25')),
        ('"[48,61,76]" occurrences','12',t.count('[48,61,76]')),
        ('"exactly once, here" present','yes',t.count('exactly once, here'))]
for name,theirs,mine in claims:
    print('  %-30s they say %-22s I measure %d'%(name,theirs,mine))
print()
print('=== LOCATION of every occurrence ===')
for pat in ['is to become','with rev 25']:
    print('  "%s":'%pat)
    for i,l in enumerate(L):
        if pat in l: print('     L%-5d %s'%(i+1,l.strip()[:150]))
print()
print('=== the READING NOTE and what is IMMEDIATELY ABOVE it ===')
ri=[i for i,l in enumerate(L) if 'READING NOTE' in l][0]
print('  READING NOTE at L%d'%(ri+1))
for k in range(ri-2,ri+1):
    print('    L%-5d %s'%(k+1,L[k].strip()[:130] if L[k].strip() else '(BLANK)'))
print()
print('=== and where is the correct-set operative sentence? ===')
for i,l in enumerate(L):
    if 'holds for every contract revision from 29 onward' in l:
        print('    L%-5d %s'%(i+1,l.strip()[:150]))