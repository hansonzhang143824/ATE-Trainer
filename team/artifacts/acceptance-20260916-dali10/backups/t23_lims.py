import sys,io,os,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
J=json.loads(open(os.path.join(d,'implementation-manifest.draft.json'),'rb').read().decode('utf-8-sig'))
print('=== all limitations ===')
for i,x in enumerate(J['limitations']): print('[%2d] %s'%(i,x[:150]))
print()
print('dedicated TM643 deviation entry present:',any('PRE-EXISTING and are recorded here rather than' in x for x in J['limitations']))