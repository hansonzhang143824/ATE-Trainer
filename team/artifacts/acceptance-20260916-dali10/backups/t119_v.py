import sys,io,os,json,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
J=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('=== THEIR CLAIM: L1/L2 cannot be mechanically recovered because "what counts as a reference" is undefined ===')
dict_nodes=0; value_nodes=0; refs=[]; status=[]
def walk(o,path=''):
    global dict_nodes,value_nodes
    if isinstance(o,dict):
        dict_nodes+=1
        hasval=False
        for k,v in o.items():
            if isinstance(v,str) and re.search(r'\b[0-9a-f]{32,64}\b',v): hasval=True
            if isinstance(v,str) and ('/' in v and (v.endswith('.json') or v.endswith('.md') or v.endswith('.cpp') or v.endswith('.h'))):
                refs.append(path+'/'+k)
        if hasval: value_nodes+=1
        for k,v in o.items(): walk(v,path+'/'+str(k))
    elif isinstance(o,list):
        for i,v in enumerate(o): walk(v,path+'[%d]'%i)
walk(J)
print('  dict nodes: %d | nodes carrying a hash value: %d | string-form path references: %d'%(dict_nodes,value_nodes,len(refs)))
print()
print('  sample string-form path references (these are L2 by intent, but have no hash):')
for r in refs[:8]: print('     %s'%r)
print()
print('=== and can a MECHANICAL rule distinguish reference from status? ===')
print('  fields named "path"            -> reference by NAME')
print('  fields named "artefact"        -> reference by NAME')
print('  fields like runId/status/authoredBy -> NOT a reference, but structurally identical (a string)')
print('  => so a machine sees strings; only the NAME tells it which are references. THEIR POINT STANDS.')