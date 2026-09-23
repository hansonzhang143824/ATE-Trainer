import sys,io,os,hashlib,time,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== 1) verify their note figures ===')
p=os.path.join(d,'review-handoff-note-plan-side.md')
if os.path.exists(p):
    q=open(p,'rb').read(); t=q.decode('utf-8-sig')
    print('  %d B / %s @%s'%(len(q),hashlib.sha256(q).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
    print('  they say: 30,884 B / b5ad5f8dd5f3d31e1a92cd73396ea3276ef627bc51a6c27d1a9e62c6c6d8e321 @21:37:48')
    print('  t43 count = %d (they say 22)'%t.count('t43'))
    print('  "t40 + t42" count = %d (they say 1 = the history note)'%t.count('t40 + t42'))
    print('  "t39+t40" count = %d (they say 0)'%t.count('t39+t40'))
    print('  "GATE CLOSED" present:', 'GATE CLOSED' in t)
    for m in re.finditer(r'[^\n]*(t43 HAS RETURNED|GATE CLOSED)[^\n]*',t):
        print('    | %s'%m.group(0).strip()[:130])
print()
print('=== 2) payload state, measured now (the item they flag for the 4th time) ===')
p2=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p2,'rb').read()
print('  %d B / %s @%s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p2).st_mtime))))
print('  they say: 43,806 B / 66abc088... @21:09:24  -> MATCH:',hashlib.sha256(r).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')