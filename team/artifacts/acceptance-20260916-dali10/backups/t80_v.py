import sys,io,os,re,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
n=os.path.join(d,'review-handoff-note-plan-side.md')
r=open(n,'rb').read(); t=r.decode('utf-8-sig'); h=hashlib.sha256(r).hexdigest()
print('=== CURRENT note ===')
print('  %d B / %s @%s'%(len(r),h,time.strftime('%H:%M:%S',time.localtime(os.stat(n).st_mtime))))
print('  they cite: 67,206 B / 63dc3ba0bd121e93a8982d0008c7d4bc0b6250edfca3026a7afb2ae6305a155d @23:07:57')
print('  match:', h=='63dc3ba0bd121e93a8982d0008c7d4bc0b6250edfca3026a7afb2ae6305a155d')
print()
print('=== their counts ===')
for pat in ['INTERSECTION','UNION/intersection','is to become','with rev 25','READING NOTE','[48,61,76]','{48,60,61,76,83}']:
    print('  %-22s %d'%(pat,t.count(pat)))
print()
print('=== AUDIT THE ONE PHRASE: is the operative sentence now correct? ===')
i=t.find('READING NOTE')
if i>0:
    ln=t[:i].count('\n')+1
    print('  READING NOTE found by content at line %d:'%ln)
    print('   ',' '.join(t[i:i+330].split())[:330])
print()
print('=== and the sentence immediately ABOVE the note (the operative one) ===')
j=t.rfind('\n',0,i)
k=t.rfind('\n',0,j-1)
k2=t.rfind('\n',0,k-1)
print('  ',' '.join(t[k2:i].split())[-330:])