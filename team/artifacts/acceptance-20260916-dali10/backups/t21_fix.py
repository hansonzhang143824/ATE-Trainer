import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
u=open(p,'rb').read().decode('utf-8-sig')
n126=u.count(', 126, -1); print('bare ", 126, -1" occurrences:',n126)
# 1) bare 126 -> the single-point define, everywhere
u=u.replace(', 126, -1', ', K126_V1P5_CAP, -1')
# 2) TM601: add the four stabiliser caps the gate reports (K45/K44 for the BST-SW rails, K57 was present, K5 for VBUS)
old601='    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K126_V1P5_CAP, -1);'
new601=('    // FR-001 reverse (powered rail => its stabiliser cap must be closed), each name from the\n'
        '    // generate/testauthority set, verified against StdAfx.h single-point defines:\n'
        '    //   K44_Cap_SW2_BST2 (:205) and K45_Cap_SW1_BST1 (:206) - the two BST-SW rail caps;\n'
        '    //   K57_CAP_BST_SW (:220); K5_VBUS_Cap (:161) for the VBUS rail reachable through\n'
        '    //   K154_BUSH0_AMUX. Closure is a protection/stabiliser requirement, inert for the 1 A\n'
        '    //   measurement which returns through SW and PGND.\n'
        '    cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K44_Cap_SW2_BST2, K45_Cap_SW1_BST1, K5_VBUS_Cap, K126_V1P5_CAP, -1);')
n=u.count(old601); print('TM601 SetOn matched:',n)
if n==1: u=u.replace(old601,new601)
else: print('WARNING: TM601 SetOn not matched exactly')
open(p,'wb').write(b'\xef\xbb\xbf'+u.replace('\r\n','\n').replace('\n','\r\n').encode('utf-8'))
r=open(p,'rb').read(); v=r.decode('utf-8-sig'); code=[l for l in v.split('\n') if not l.strip().startswith('//')]
print()
print('payload %d B BOM=%s CRLF=%d loneLF=%d'%(len(r),r[:3]==b'\xef\xbb\xbf',r.count(b'\r\n'),r.count(b'\n')-r.count(b'\r\n')))
print('sha256',hashlib.sha256(r).hexdigest())
print('bare 126 left:',sum(1 for l in code if re.search(r',\s*126\s*,',l)) if (re:=__import__('re')) else 0)
print('K126_V1P5_CAP:',sum(l.count('K126_V1P5_CAP') for l in code))
for l in code:
    if 'SetOn(' in l: print('  SetOn:',l.strip()[:160])