import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== their note (they say 58,014 B / 75bbc6bc... @22:49:50) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  match:', hashlib.sha256(r).hexdigest()=='75bbc6bcdf0ff78ace3ce83c71dd59be58b6dfc1d58d659da63d982460bd4dd0')
print()
print('=== is the forward-looking wrong-set sentence GONE? ===')
print('  "is to become" occurrences: %d'%t.count('is to become'))
for i,l in enumerate(t.split('\n')):
    if 'is to become' in l: print('   L%-5d %s'%(i+1,l.strip()[:170]))
print()
print('=== their claimed counts ===')
print('  "{48,60,61,76,83}" = %d (they say 5)'%t.count('{48,60,61,76,83}'))
print('  slip/correction marker occurrences:', t.count('own slip')+t.count('my own slip'))
print()
print('=== consistency check: which set-value form is used where ===')
for pat in ['[48,60,61,76]','{48,60,61,76,83}','[48,60,61,76,83]','closedRelayNumbers']:
    print('  %-22s %d'%(pat,t.count(pat)))