import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json')
r=open(p,'rb').read(); h=hashlib.sha256(r).hexdigest()
print('=== plan, independently verified (they claim 185,689 B / 707ce845... @21:54:50, v25, 25 history entries) ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
print('  size+hash match:', h=='707ce845c5459b41b528059eab7f26b1a8e597e34daf8df40929346942a8ee69')
J=json.loads(r.decode('utf-8-sig'))
print('  revision:',J.get('revision'))
rh=J.get('revisionHistory')
print('  revisionHistory entries:',len(rh) if isinstance(rh,list) else 'n/a')
if isinstance(rh,list) and rh:
    last=rh[-1]
    print('  last entry revision:', last.get('revision') if isinstance(last,dict) else str(last)[:60])
    print('  last entry keys:', list(last.keys())[:8] if isinstance(last,dict) else '-')
print()
print('=== and my own delivery, final check for this turn ===')
q=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); qr=open(q,'rb').read()
print('  %d B / %s @%s'%(len(qr),hashlib.sha256(qr).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(q).st_mtime))))