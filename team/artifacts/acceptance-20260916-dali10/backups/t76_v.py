import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
b=os.path.join(d,'backups')
print('=== their claims about my restore ===')
print('  superseded-scratch/ exists:', os.path.exists(os.path.join(b,'superseded-scratch')))
subs=[x for x in os.listdir(b) if os.path.isdir(os.path.join(b,x))]
print('  subdirs now:',subs,'(they say t53-20260916-211719, t55-target-20260916-213542)')
pys=[f for f in os.listdir(b) if f.endswith('.py') and os.path.isfile(os.path.join(b,f))]
print('  top-level *.py count: %d (they say 367)'%len(pys))
rp=os.path.join(b,'README-READ-BEFORE-RUNNING.md')
if os.path.exists(rp):
    r=open(rp,'rb').read()
    print('  README: %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(rp).st_mtime))))
    print('  they say: 1,711 B / 934ccf843e88f9cc… @22:35:04')
    print('  size match:',len(r)==1711,'| hash match:',hashlib.sha256(r).hexdigest().startswith('934ccf843e88f9cc'))
    print('  loneLF:',r.count(b'\n')-r.count(b'\r\n'),'| CRLF:',r.count(b'\r\n'))
print()
print('=== and their new note (they say 64,670 B / 42ac6d36... @22:59:10) ===')
n=os.path.join(d,'review-handoff-note-plan-side.md')
if os.path.exists(n):
    nr=open(n,'rb').read()
    print('  %d B / %s @%s'%(len(nr),hashlib.sha256(nr).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))