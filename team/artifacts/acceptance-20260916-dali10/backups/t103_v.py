import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== their anchor ===')
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 133,328 B / 2bdd2be5b9e840d04722cc80a77061cac168a395b7aacb72b69980268a9b05f7 @01:39:25')
print('  match:', len(r)==133328 and h=='2bdd2be5b9e840d04722cc80a77061cac168a395b7aacb72b69980268a9b05f7')
print()
print('=== their three corrections, on current disk ===')
fs=os.path.join(d,'gate-logs-t28','setupArchitect-freeze-snapshots.json')
ta=os.path.join(d,'gate-logs-t28','t28-anchors.json')
for f,label in [(fs,'freeze-snapshots'),(ta,'t28-anchors')]:
    if os.path.exists(f):
        b=open(f,'rb').read().decode('utf-8-sig',errors='replace')
        print('  %-18s %d B | 97636 x%d | mirrorSize token x%d'%(label,os.path.getsize(f),b.count('97636'),b.count('mirrorSize')))
print()
print('=== my three artefacts, unchanged and re-measured ===')
for f in ['implementation-payload-TM600-TM601.cpp','implementation-manifest.json','APPLY-TM600-TM601.md']:
    p=os.path.join(d,f); rr=open(p,'rb').read()
    print('  %-40s %7d B / %s'%(f,len(rr),hashlib.sha256(rr).hexdigest()[:20]))