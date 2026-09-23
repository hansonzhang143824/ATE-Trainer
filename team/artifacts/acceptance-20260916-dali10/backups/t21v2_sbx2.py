import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
tgt=os.path.join(r'D:\PROJECT6-DALI\ForCodexDebug','source','test.cpp')
cur=open(tgt,'rb').read().decode('utf-8-sig')
pay=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read().decode('utf-8-sig')
body=pay[pay.find('DUT_API int TM600_HS_RDSON'):]
# locate the existing t20-era TM600..end-of-TM601 region in the target and replace it with the new body
s=cur.find('DUT_API int TM600_HS_RDSON')
if s<0:
    print('TM600 not found in target — model changes'); raise SystemExit(1)
# find the comment banner that precedes the t20 block so we drop it too
pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s)
e=cur.find('\nDUT_API int',j+10)
if e<0: e=len(cur)
print('replacing target bytes [%d,%d) = %d bytes with payload body %d bytes'%(pre,e,e-pre,len(body)))
patched = cur[:pre] + '\n' + body.rstrip('\n') + '\n' + (cur[e:] if e<len(cur) else '')
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
open(sbx,'w',encoding='utf-8',newline='').write(patched)
r=open(sbx,'rb').read()
print('sandbox: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  TM600 defs:',patched.count('DUT_API int TM600_HS_RDSON'),'| TM601:',patched.count('DUT_API int TM601_LS_RDSON'))
for k in ['i_meas[site] > 0.1','FXVIe_PLUS_30V','FXVIe_PLUS_20V','ACM200_20V','K5_VBUS_Cap','K126_V1P5_CAP',', 126,']:
    print('  %-24s %d'%(k,patched.count(k)))