import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
r=open(p,'rb').read(); u=r.decode('utf-8-sig'); L=u.split('\n')
print('payload %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('  canonical 6034af71... -> MATCH:',hashlib.sha256(r).hexdigest()=='6034af710a348e578099886737cc7cc086c8297808189cfa283ad8ce4ec7c4fa')
print()
print('=== t50 acceptance items: which are ALREADY satisfied by the frozen payload? ===')
print('  (1) K48/K76 appended, single SetOn   :', u.count('K48_ACM5_AMP_REF')>0 and u.count('K76_ACM_BST')>0)
print('  (2) K109/K110 retained               :', u.count('K109_BUSL1_PB0')>0 and u.count('K110_ACM18_BST')>0)
print('  (2b) coupling cost registered in comment:', 'FPVIe1_FL_BUS_S1' in u or 'coupling' in u.lower())
print('  (4) --check-extra prohibition annotated:', '--check-extra' in u)
print()
print('=== (3) L416-420: current text (is it the mechanism statement?) ===')
for i in range(410,432):
    if i<len(L): print('  L%-4d %s'%(i+1,L[i].rstrip()[:135]))