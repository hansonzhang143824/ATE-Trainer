import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-manifest.json')
M=json.loads(open(p,'rb').read().decode('utf-8-sig'))
print('manifest now: %d B / %s @%s'%(os.path.getsize(p),hashlib.sha256(open(p,'rb').read()).hexdigest(),time.strftime('%H:%M:%S',time.localtime(os.stat(p).st_mtime))))
blk=M['handoffCitationRisk']
print()
print('=== my criterion wording (does it carry the executable-code qualifier?) ===')
c=blk['criterion']
print('  contains "COMMENTS STRIPPED":','COMMENTS STRIPPED' in c)
print('  contains "executable code":','executable code' in c.lower())
print()
print('=== my mustContain keys ===')
for k in blk['authoritativeCurrentValues'][0]['mustContain']: print('   -',k)
print()
print("=== t4's broadcast criterion lacks the qualifier? ===")
t4c="必须含 PER-FUNCTION JUSTIFICATION + K109_BUSL1_PB0/K110_ACM18_BST"
print("  t4 text:",t4c)
print("  says 'executable'?:", 'executable' in t4c.lower() or '可执行' in t4c)