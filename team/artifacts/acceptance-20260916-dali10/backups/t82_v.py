import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); L=t.split('\n'); h=hashlib.sha256(r).hexdigest()
print('=== file they now cite ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 68,161 B / 94beadd2... @23:12:16 -> match:', h=='94beadd24e4f941ae3bd763cc4a9f48772096a6fe94fcde25abdc64b6b3f400a')
print()
print('=== DEFECT 1: does the false "exactly once" claim still exist? ===')
print('  "exactly once, here" count:', t.count('exactly once, here'))
for i,l in enumerate(L):
    if 'exactly once' in l or 'occurs in this note' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:180]))
print('  actual "is to become" occurrences:', t.count('is to become'))
for i,l in enumerate(L):
    if 'is to become' in l: print('     L%-5d %s'%(i+1,l.strip()[:120]))
print()
print('=== DEFECT 2: what is immediately ABOVE the READING NOTE? ===')
ri=[i for i,l in enumerate(L) if 'READING NOTE' in l]
for x in ri:
    print('  READING NOTE at L%d'%(x+1))
    for k in range(max(0,x-2),x+1):
        print('    L%-5d %s'%(k+1,L[k].strip()[:130] if L[k].strip() else '(BLANK)'))
print()
print('=== and is the quotation above or below it? ===')
qi=[i for i,l in enumerate(L) if 'is to become' in l]
for x in qi:
    above = x-1
    role = 'while READING NOTE is at L%d'%(ri[0]+1) if ri else ''
    print('    quotation at L%d; immediately above: %s'%(x+1, (L[x-1].strip()[:90] if L[x-1].strip() else '(BLANK)')))