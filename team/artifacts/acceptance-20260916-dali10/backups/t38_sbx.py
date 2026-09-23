import sys,io,os,re,hashlib
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
# final invariant re-verify on the payload after the nuance edit
u=pay; c=re.sub(r'//.*$','',u,flags=re.M)
print()
print('invariants: d1=%d d2=%d clamp=%d meas=%d K126=%d ERR=%d K57=%d K5/44/45=%d K109=%d K110=%d bare126=%d ramp=%d comp=%d'%(
 c.count('delay_ms(1)'),c.count('delay_ms(2)'),c.count('SetClamp(50, 50)'),c.count('MeasureVI(200, 5, FPVIe_MV_X10)'),
 c.count('K126_V1P5_CAP'),c.count('ERROR_RES'),c.count('K57_CAP_BST_SW'),
 c.count('K5_VBUS_Cap')+c.count('K44_Cap_SW2_BST2')+c.count('K45_Cap_SW1_BST1'),
 c.count('K109_BUSL1_PB0'),c.count('K110_ACM18_BST'),
 len(re.findall(r'(?<![\dA-Za-z_])126(?![\dA-Za-z_])',c)),c.count('rampi_capv')+c.count('rampv_capv'),
 c.count('K_FPVIH_TO_BST_B')+c.count('K_FPVIL_TO_SW_B')))
t601=u[u.find('DUT_API int TM601_LS_RDSON'):]
print('TM601 ACM sets in code:',len([l for l in t601.split('\n') if 'SW12_U1REF_BST_ACM.Set' in l and not l.strip().startswith('//')]))
print('PMID 10V step range:', 'FXVIe_PLUS_20V' in c and 'Set(FV, 10, FXVIe_PLUS_10V' not in c)