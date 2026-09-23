import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
n126=u.count(', 126, -1')
print('bare 126 tokens:',n126)
u=u.replace(', 126, -1', ', K126_V1P5_CAP, -1')
old601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K126_V1P5_CAP, -1);'
new601=('\n'.join([
 '    // FR-001 reverse (a powered rail requires its stabiliser cap closed). Names verified against',
 '    // the StdAfx.h single-point defines: K44_Cap_SW2_BST2 (:205), K45_Cap_SW1_BST1 (:206),',
 '    // K57_CAP_BST_SW (:220), K5_VBUS_Cap (:161) for the VBUS rail reachable via K154_BUSH0_AMUX.',
 '    // These closures are stabiliser/protection only and inert for the measurement, which returns',
 '    // through SW and PGND.',
 '    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, K126_V1P5_CAP, -1);']))
n=u.count(old601)
print('TM601 SetOn matched:',n)
u=u.replace(old601,new601)
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B BOM=%s CRLF=%d loneLF=%d'%(len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print('sha256',hashlib.sha256(r).hexdigest())
print('bare 126 left in code:',sum(1 for l in code if re.search(r',\s*126\s*,',l)))
print('SetOn lines:')
for l in code:
    if 'SetOn(' in l: print('  ',l.strip()[:170])
print('code invariants: delay_ms(1)=%d delay_ms(2)=%d SetClamp=%d MeasureVI=%d ramp=%d'%(
 sum(l.count('delay_ms(1)') for l in code),sum(l.count('delay_ms(2)') for l in code),
 sum(l.count('SetClamp(50, 50)') for l in code),sum(l.count('MeasureVI(200, 5, FPVIe_MV_X10)') for l in code),
 sum(l.count('rampi_capv')+l.count('rampv_capv') for l in code)))