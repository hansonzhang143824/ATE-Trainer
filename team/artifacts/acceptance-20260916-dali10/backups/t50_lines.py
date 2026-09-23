import sys,io,os,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(p,'rb').read(); t=r.decode('utf-8-sig')
print('current note: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  t4 says: 18,250 B / 3c48d3449a6619dbebd23dd555506ab43378c0fa625657d2674291586a0fc190 @20:45:44')
print()
print('=== FILE + LINE for every "t40 + t42" style gate statement ===')
for i,l in enumerate(t.split('\n')):
    if re.search(r't40.{0,6}t42|t42.{0,6}t40',l) or ('BLOCKED' in l):
        print('  L%-5d %s'%(i+1,l.strip()[:150]))
print()
print('=== and every t43 mention ===')
hits=[i+1 for i,l in enumerate(t.split('\n')) if 't43' in l]
print('  t43 lines:',hits if hits else 'NONE')
print()
print('=== the t35 precondition line, exactly ===')
for i,l in enumerate(t.split('\n')):
    if 't35' in l: print('  L%-5d %s'%(i+1,l.strip()[:160]))