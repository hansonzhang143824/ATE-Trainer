import sys,io,os,re,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
# 1) what does the meta declare for TM601_LS_RDSON (the gate's authority)?
p=os.path.join(base,'project','DALI','meta','dali_tm_meta.json')
print('meta exists:',os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else '')
if os.path.exists(p):
    M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
    def find(o):
        if isinstance(o,dict):
            if 'TM601_LS_RDSON' in o: return o['TM601_LS_RDSON']
            for v in o.values():
                r=find(v)
                if r is not None: return r
        elif isinstance(o,list):
            for v in o:
                r=find(v)
                if r is not None: return r
        return None
    e=find(M)
    print('TM601_LS_RDSON meta entry:')
    print(json.dumps(e,ensure_ascii=False,indent=1)[:1400] if e else '(not found)')
print()
# 2) connect-map locators cited by the captain
cm=os.path.join(base,'project','DALI','SCH-Connect-Map.txt')
t=open(cm,'rb').read().decode('utf-8-sig',errors='replace').split('\n')
print('=== connect-map lines for K5 / K57 / K44 / K45 / K154 / K3 / K46 / K49 ===')
for i,l in enumerate(t):
    if re.search(r'K5\b|K57\b|K44\b|K45\b|K154\b|K3\b|K46\b|K49\b',l) and ('需闭合' in l or 'VBUS' in l or '稳压' in l or 'BUS' in l):
        print('  %4d: %s'%(i+1,l.strip()[:135]))