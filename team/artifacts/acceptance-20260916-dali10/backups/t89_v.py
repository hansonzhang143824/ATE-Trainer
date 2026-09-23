import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); L=t.split('\n'); h=hashlib.sha256(r).hexdigest()
print('=== their anchor ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite 89,213 B / bc41bcefaf26c586f4128c1cb9ce527cb5ad035666f5e76271245a74dc5e6a55 @23:57:38')
print('  match:', h=='bc41bcefaf26c586f4128c1cb9ce527cb5ad035666f5e76271245a74dc5e6a55')
print()
print('=== their claims ===')
for pat,claim in [('immediately ABOVE this note','0'),('by its content, not by a position','1'),('twice by design','2'),('exactly once','3')]:
    print('  %-40s = %d (they claim %s)'%(pat,t.count(pat),claim))
print()
print('=== is the READING NOTE at L739 with a blank line above it (as they say)? ===')
ri=[i for i,l in enumerate(L) if 'READING NOTE' in l]
for x in ri:
    print('  READING NOTE at L%d; line above = %s'%(x+1,'(BLANK)' if not L[x-1].strip() else L[x-1].strip()[:100]))
print()
print('=== MY payload, unchanged check ===')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(p,'rb').read()
print('  %d B / %s @%s'%(len(pr),hashlib.sha256(pr).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))