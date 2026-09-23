import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
# the payload's executable part = everything from the first DUT_API int onward (header is documentation)
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
# rebuild the sandbox copy: target up to TM600 insertion point + payload body
marker='DUT_API int TM600_HS_RDSON'
assert marker not in cur, 'target unexpectedly already contains the new functions'
# target currently ends with the old TM1205 function; append payload body after a separating newline
patched = cur.rstrip('\n') + '\n' + body.rstrip('\n') + '\n'
sbx=os.path.join(d,'gate-check-t21','source')
open(os.path.join(sbx,'test.cpp'),'w',encoding='utf-8',newline='').write(patched)
r=open(os.path.join(sbx,'test.cpp'),'rb').read()
print('sandbox test.cpp rebuilt: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  TM600 defs:',patched.count('DUT_API int TM600_HS_RDSON'),'| TM601:',patched.count('DUT_API int TM601_LS_RDSON'))
for k in ['i_meas[site] > 0.1','FXVIe_PLUS_30V','FXVIe_PLUS_20V','ACM200_20V','K5_VBUS_Cap','K126_V1P5_CAP']:
    print('  %-22s %d'%(k,patched.count(k)))