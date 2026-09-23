import sys,io,os,hashlib,re,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'review-handoff-note-plan-side.md')
print('exists:',os.path.exists(p))
if os.path.exists(p):
    r=open(p,'rb').read(); t=r.decode('utf-8-sig')
    print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
    print()
    print('  gate mentions in that note:')
    for pat in ['t40','t42','t43','t39','t44']:
        print('    %-5s %d'%(pat,t.count(pat)))
    for m in re.finditer(r'[^\n]*(t40|t42|t43)[^\n]*',t):
        print('    | %s'%m.group(0).strip()[:130])