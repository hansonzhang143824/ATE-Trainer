import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
base=r'D:\Newtest\DSH\ATE-Coding-Plat'
print('=== locate t28-anchors.json anywhere in the workspace ===')
hits=[]
for root,dirs,files in os.walk(base):
    for f in files:
        if 'anchor' in f.lower() and f.endswith('.json'):
            p=os.path.join(root,f)
            try: sz=os.path.getsize(p)
            except: continue
            hits.append((os.path.relpath(p,base),sz))
for p,s in hits[:12]: print('  %-72s %d B'%(p,s))
print('  total:',len(hits))
print()
print('=== my manifest authoritativeCurrentValues + supersededValuesSeenInHandoffs ===')
d=os.path.join(base,'team','artifacts','acceptance-20260916-dali10')
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
h=M['handoffCitationRisk']
print('  authoritativeCurrentValues:',json.dumps(h.get('authoritativeCurrentValues'),ensure_ascii=False)[:400])
print()
print('  supersededValuesSeenInHandoffs:',json.dumps(h.get('supersededValuesSeenInHandoffs'),ensure_ascii=False)[:400])
print()
print('  instructionToReviewer:',json.dumps(h.get('instructionToReviewer'),ensure_ascii=False)[:500])