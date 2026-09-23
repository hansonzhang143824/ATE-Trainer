import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'test-plan.json'); r=open(p,'rb').read()
P=json.loads(r.decode('utf-8-sig')); s=json.dumps(P,ensure_ascii=False)
print('live test-plan.json: %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('revision:',str(P.get('revision'))[:80])
print()
print('=== ruling (ii) markers in the live plan ===')
for k in ['GROUND-REFERENCED','ruling (ii)','INTENDED BUT CURRENTLY UNREALISABLE','intended but currently unrealisable',
          'supersedes the earlier floating-channel-1 baseline','SW12_U1REF_BST_ACM','[110,61]',
          'K_FPVIH_TO_BST_B','131,132,134,135','K_FPVIL_TO_SW_A','60,61']:
    print('  %-46s %d'%(k,s.count(k)))
print()
it=[x for x in P['items'] if x.get('tm')=='TM600'][0]
a=[x for x in it.get('assumptions',[]) if 'arbitration' in str(x).lower()]
print('=== TM600 arbitration assumption (verbatim, first 700 chars) ===')
print(a[0][:700] if a else '(none)')