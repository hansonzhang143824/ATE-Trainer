import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
m=r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\meta\dali_tm_meta.json'
st=os.stat(m); r=open(m,'rb').read()
print('meta now: %d B / %s  mtime %s'%(len(r),hashlib.sha256(r).hexdigest(),time.strftime('%H:%M:%S',time.localtime(st.st_mtime))))
print("t4 claim : 147520 B / 50efba4ec6c271923c5f956b9c2a9f2f19173f7c0900a24ce0ec2ac3704b1f42  mtime 18:52:27")
print()
M=json.loads(r.decode('utf-8-sig'))
for e in M['functions']:
    if e.get('functionName') in ('TM600_HS_RDSON','TM601_LS_RDSON'):
        ca=e.get('capAuthority') or {}
        print('=== %s ==='%e['functionName'])
        print('  powered_pins:',ca.get('powered_pins'))
        print('  mi_pins     :',ca.get('mi_pins'))
        print('  ramp_pins   :',ca.get('ramp_pins'))
        print('  has _t26OverrideNote:', any(k for k in e if 't26' in str(k).lower()))
        print('  VBUS in any pin list:', 'VBUS' in json.dumps(ca).upper())
        hi=e.get('hardwareInit')
        print('  hardwareInit vset/iset:',[ (x.get('cmd'),x.get('pin'),x.get('value')) for x in (hi or []) if x.get('cmd') in ('vset','iset')])
        print()