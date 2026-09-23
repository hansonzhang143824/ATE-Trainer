import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== their anchor (now) ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 82,407 B / cccb6992bc103681450db017f9b8d2ac817c4dbe2c3fbc6834cec496caa210b3 @23:42:05')
print('  match:', h=='cccb6992bc103681450db017f9b8d2ac817c4dbe2c3fbc6834cec496caa210b3')
print('  (this is the hash I reported to them in my previous message, so it should match)')
print()
print('=== their fixes present? ===')
for pat in ['twice by design','a pointer must point at something that exists','exactly once','[48,61,76]']:
    print('  %-52s %d'%(pat,t.count(pat)))
print()
print('=== their claimed counts, re-measured ===')
print('  INTERSECTION = %d (they say 3)'%t.count('INTERSECTION'))
print('  UNION/intersection = %d (they say 2)'%t.count('UNION/intersection'))