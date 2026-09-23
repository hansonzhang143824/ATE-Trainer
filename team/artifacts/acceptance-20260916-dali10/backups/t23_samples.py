import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
M=json.loads(open(os.path.join(d,'implementation-manifest.json'),'rb').read().decode('utf-8-sig'))
s=json.dumps(M,ensure_ascii=False)
print('=== does the manifest already state the sampling fact? ===')
for k in ['200','50, 5','(50,5)','golden-exclusive','samples','noise']:
    print('  %-18s %d occurrence(s)'%(k,s.count(k)))
print()
for i,x in enumerate(M['limitations']):
    if 'sampl' in x.lower() or '200' in x or 'noise' in x.lower():
        print('  limitation[%d]: %s'%(i,x[:220]))
print()
hit=[x for x in M['limitations'] if 'noise' in x.lower()]
print('correctness-neutral sampling stated:',bool(hit))