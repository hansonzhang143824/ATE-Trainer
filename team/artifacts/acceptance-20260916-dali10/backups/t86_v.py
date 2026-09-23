import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); L=t.split('\n'); h=hashlib.sha256(r).hexdigest()
print('=== their anchor ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 81,800 B / c82bd1a4e11d6dc8082ac043ab73d999ce51711ee82bda713f68ad05654e5b5 @23:39:28')
print('  match:', h=='c82bd1a4e11d6dc8082ac043ab73d999ce51711ee82bda713f68ad05654e5b5')
print()
print('=== DEFECT 1: is "exactly once" replaced by "twice by design"? ===')
print('  "exactly once" count:', t.count('exactly once'))
print('  "twice by design" count:', t.count('twice by design'))
print('  ACTUAL "is to become" occurrences:', t.count('is to become'))
print()
print('=== DEFECT 2: does the pointer now point DOWN at an existing operative sentence? ===')
ri=[i for i,l in enumerate(L) if 'READING NOTE' in l]
for x in ri:
    print('  READING NOTE at L%d:'%(x+1))
    for k in range(max(0,x-3),x+1):
        print('    L%-5d %s'%(k+1, (L[k].strip()[:135] if L[k].strip() else '(BLANK)')))
    print('    -> immediately above is %s'%('BLANK' if not L[x-1].strip() else 'non-blank'))
print()
print('=== and their new count claims ===')
print('  "INTERSECTION" actual count: %d (they say 3)'%t.count('INTERSECTION'))
print('  "UNION/intersection" actual count: %d (they say 2)'%t.count('UNION/intersection'))