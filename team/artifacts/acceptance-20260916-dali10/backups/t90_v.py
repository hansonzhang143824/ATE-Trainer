import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== current note ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 89,213 B / bc41bcefaf26c586f4128c1cb9ce527cb5ad035666f5e76271245a74dc5e6a55 @23:57:38')
print('  match:', h=='bc41bcefaf26c586f4128c1cb9ce527cb5ad035666f5e76271245a74dc5e6a55')
print()
print('=== every claim of theirs, re-measured ===')
for pat,claim in [('exactly once, here','0'),('twice by design','2'),('immediately ABOVE this note','0'),('by its content','1'),('is to become','2'),('exactly once','3')]:
    got=t.count(pat)
    print('  %-32s = %d (they claim %s) %s'%(pat,got,claim,'OK' if str(got)==claim else '*** DIFFERS ***'))
print()
print('=== and each "exactly once" context, to confirm none is a live assertion ===')
for i,l in enumerate(t.split('\n')):
    if 'exactly once' in l: print('  L%-5d %s'%(i+1,l.strip()[:150]))