import sys,io,os,hashlib,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
print('=== FACT: current payload, measured now ===')
r=open(pay,'rb').read()
print('  %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  BOM:',r[:3]==b'\xef\xbb\xbf','| CRLF count:',r.count(b'\r\n'),'| lone LF:',r.count(b'\n')-r.count(b'\r\n'))
# rebuild sandbox from the CURRENT payload (post-CRLF-fix)
cur=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
body=r.decode('utf-8-sig'); body=body[body.find('DUT_API int TM600_HS_RDSON'):]
s=cur.find('DUT_API int TM600_HS_RDSON'); pre=cur.rfind('\n//',0,s)
j=cur.find('DUT_API int TM601_LS_RDSON',s); e=cur.find('\nDUT_API int',j+10)
sbx=os.path.join(d,'gate-check-t21','source','test.cpp')
with open(sbx,'w',encoding='utf-8',newline='') as f:
    f.write(cur[:pre]+'\n'+body.rstrip('\n')+'\n'+(cur[e:] if e<len(cur) else ''))
rs=open(sbx,'rb').read()
print()
print('=== FACT: sandbox rebuilt from the CURRENT (post-CRLF-fix) payload ===')
print('  sandbox %d B / %s'%(len(rs),hashlib.sha256(rs).hexdigest()))
t=rs.decode('utf-8-sig')
seg=t[t.find('DUT_API int TM600_HS_RDSON'):t.find('DUT_API int TM601_LS_RDSON')]
for l in seg.split('\n'):
    if 'cbite.SetOn(' in l: print('  sandbox TM600 SetOn:',l.strip()[:170])