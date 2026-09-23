import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig')
print('=== their note (they say 53,537 B / b6ac2ea3... @22:35:37) ===')
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print()
print('=== THE ONE OPEN ITEM: is the wrong set [48,61,76] still there? ===')
for pat in ['[48,61,76]','[48, 61, 76]','[48,60,61,76]','[48, 60, 61, 76]','[48,60,61,76,83]']:
    print('  %-22s %d'%(pat,t.count(pat)))
print()
print('=== context for any surviving [48,61,76] ===')
for i,l in enumerate(t.split('\n')):
    if '[48,61,76]' in l or '[48, 61, 76]' in l:
        print('  L%-5d %s'%(i+1,l.strip()[:170]))
print()
print('=== and confirm their two reported fixes are present ===')
for pat in ['four functions close the leg explicitly','one executable line each','the re-run has since been done','sandbox copy at']:
    print('  %-38s %d'%(pat,t.count(pat)))