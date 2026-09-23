import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
M=json.loads(open(r'D:\Newtest\DSH\ATE-Coding-Plat\project\DALI\meta\dali_tm_meta.json','rb').read().decode('utf-8-sig'))
for e in M['functions']:
    if e.get('functionName') in ('TM600_HS_RDSON','TM601_LS_RDSON'):
        s=json.dumps(e,ensure_ascii=False)
        print('=== %s ==='%e['functionName'])
        print('  VBUS occurrences in the whole entry:',s.count('VBUS'))
        for m in re.finditer('VBUS',s):
            print('     ...',s[max(0,m.start()-90):m.start()+60].replace('\\n',' ')[:160])
        print('  entry-level keys:',[k for k in e][:14])
        print()
print('=== FR-001 reverse exemption mechanics (verify_relay_trace.py:325) ===')
g=open(r'D:\Newtest\DSH\ATE-Coding-Plat\scripts\verify_relay_trace.py','rb').read().decode('utf-8-sig',errors='replace').split('\n')
for i in (324,325):
    if i<len(g): print('  %d| %s'%(i+1,g[i].rstrip()[:130]))
print()
print('=== consequence for the cap closure requirement ===')
def cap_pin(n):
    m=re.match(r'^K\d*_(.+)$',n,re.I)
    if not m: return None
    parts=m.group(1).split('_'); ci=[i for i,p in enumerate(parts) if p.lower()=='cap']
    if not ci: return None
    c=ci[0]
    return '_'.join(parts[:c]) if c>0 else None
for r_ in ['K57_CAP_BST_SW','K13_VBAT_Cap','K85_CAP_PMID','K126_V1P5_CAP']:
    print('  cap_pin(%s) = %s'%(r_,cap_pin(r_)))
print('  TM601 mi_pins now:',[e.get('capAuthority',{}).get('mi_pins') for e in M['functions'] if e.get('functionName')=='TM601_LS_RDSON'])