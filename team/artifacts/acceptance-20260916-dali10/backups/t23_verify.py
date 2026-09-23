import sys,io,os,json,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.draft.json')
raw=open(p,'rb').read()
print('on disk: %d B / %s'%(len(raw),hashlib.sha256(raw).hexdigest()))
J=json.loads(raw.decode('utf-8-sig'))
print('limitations count:',len(J['limitations']))
hits=[i for i,x in enumerate(J['limitations']) if 'TM643' in x]
print('TM643 entries:',hits)
for i in hits: print('  [%d] %s'%(i,J['limitations'][i][:190]))
print()
print('payload hash recorded in draft:',J['changes'][0]['payloadSha256'][:16],'size',J['changes'][0]['payloadSize'])