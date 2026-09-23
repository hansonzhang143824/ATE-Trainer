import sys,io,os,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
cur=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else ''))
r=open(sbx,'rb').read(); print('sandbox: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
for n in ['t50-payload-k76-evidence.md','implementation-payload-TM600-TM601.cpp']:
    q=os.path.join(d,n); rr=open(q,'rb').read()
    print('  %-42s %6d B / %s @%s'%(n,len(rr),hashlib.sha256(rr).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(q).st_mtime))))