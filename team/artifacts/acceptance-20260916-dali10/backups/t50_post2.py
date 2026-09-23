import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); code=re.sub(r'//.*$','',u,flags=re.M)
L=u.split('\r\n')
print('=== POST-CHANGE SELF-CHECK on 66abc088... ===')
print('  %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  content keys:',{k:code.count(k) for k in ['K48_ACM5_AMP_REF','K76_ACM_BST','K109_BUSL1_PB0','K110_ACM18_BST','K46']})
inv={k:code.count(k) for k in ['delay_ms(1)','delay_ms(2)','SetClamp(50, 50)','MeasureVI(200, 5, FPVIe_MV_X10)','K126_V1P5_CAP','ERROR_RES','K57_CAP_BST_SW']}
print('  invariants:',inv)
print('  bare126:',len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',code)),'| K5+K44+K45:',code.count('K5_VBUS_Cap')+code.count('K44_Cap_SW2_BST2')+code.count('K45_Cap_SW1_BST1'))
print('  PMID 10V:',('FXVIe_PLUS_20V' in code) and ('Set(FV, 10, FXVIe_PLUS_10V' not in code),'| BOM',r[:3]==b'\xef\xbb\xbf','| loneLF',r.count(b'\n')-r.count(b'\r\n'))
t6=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM600_HS_RDSON'))
t7=next(i for i,l in enumerate(L) if l.startswith('DUT_API int TM601_LS_RDSON'))
print('  TM600 SetOn calls:',sum(1 for i in range(t6,t7) if 'cbite.SetOn(' in L[i]),'| ACM Sets TM600/TM601:',
 sum(1 for i in range(t6,t7) if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',L[i])),
 sum(1 for i in range(t7,len(L)) if 'SW12_U1REF_BST_ACM.Set' in re.sub(r'//.*$','',L[i])))
# rebuild sandbox from THESE bytes
cur=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
body=u[u.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
with open(sbx,'w',encoding='utf-8',newline='') as f:
    f.write(cur[:pre]+'\n'+body.rstrip('\r\n')+'\n'+(cur[e:] if e<len(cur) else ''))
rs=open(sbx,'rb').read()
print()
print('=== sandbox rebuilt from 66abc088 ===')
print('  %d B / %s'%(len(rs),hashlib.sha256(rs).hexdigest()))
seg=rs.decode('utf-8-sig')
seg=seg[seg.find('DUT_API int TM600_HS_RDSON'):seg.find('DUT_API int TM601_LS_RDSON')]
for l in seg.split('\n'):
    if 'cbite.SetOn(' in l: print('  sandbox TM600 SetOn:',l.strip()[:170])