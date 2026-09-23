import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
if e<0: e=len(cur)
patched=cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else '')
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(patched)
r=open(sbx,'rb').read(); print('sandbox: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print()
print('=== TM640 token count recheck (captain said 2 each; I measured 4) ===')
L2=cur.split('\n')
o=next(i for i,l in enumerate(L2) if l.startswith('DUT_API int TM640_BOOST_HS_OCP('))
depth=0; started=False
for i in range(o,len(L2)):
    t=re.sub(r'//.*$','',L2[i]); depth+=t.count('{')-t.count('}')
    if '{' in t: started=True
    if started and depth==0: end=i; break
blk=[re.sub(r'//.*$','',x) for x in L2[o:end+1]]
print('  TM640 L%d-%d : K48 substring=%d  K76 substring=%d  (alias-inclusive pattern K48(?![0-9])=%d / K76(?![0-9])=%d)'%(
  o+1,end+1,sum(x.count('K48') for x in blk),sum(x.count('K76') for x in blk),
  len(re.findall(r'K48(?![0-9])',' '.join(blk))),len(re.findall(r'K76(?![0-9])',' '.join(blk)))))