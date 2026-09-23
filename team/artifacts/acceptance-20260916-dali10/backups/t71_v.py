import sys,io,os,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== current note ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  t4 says: 53,537 B / b6ac2ea3828adde9f8632599efffd1d6f8c3b1faf48ec3d1647b2aa3458b864f @22:35:37')
print('  => is this the SAME bytes they are describing?', hashlib.sha256(r).hexdigest()=='b6ac2ea3828adde9f8632599efffd1d6f8c3b1faf48ec3d1647b2aa3458b864f')
print()
print('=== the disputed forward-looking line, verbatim from THESE bytes ===')
for i,l in enumerate(t.split('\n')):
    if 'is to become' in l or 'rev 25' in l and '48' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:190]))
print()
print('=== full count of [48,61,76] and where ===')
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l: print('  L%-5d %s'%(i+1,l.strip()[:150]))