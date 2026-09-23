import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'APPLY-TM600-TM601.md')
t=open(p,'rb').read().decode('utf-8-sig')
old='## Target state at preparation time'
add=('> ## ⚠ THE TREE HAS ALREADY BEEN WRITTEN — COMPARE BEFORE WRITING\n'
 '> A write has already occurred: `test.cpp` = **469714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**\n'
 '> (mtime 2026-09-16 18:53:33), and it landed the **earlier t23** revision: `TM600_HS_RDSON` at L9057 with its SetOn\n'
 '> at **L9081** closing 60/61/83 and **neither K109 nor K110**, `TM601_LS_RDSON` at L9217 with its SetOn at L9255.\n'
 '> So the tree contains this feature area but **carries the t29 defect** (the BST excitation path is unclosed).\n'
 '> **Executor: first recompute the hash of `source/test.cpp`.** If it is `15c7d2b8…`, the region must be **REPLACED**\n'
 '> with the current payload (`73b511b7…`) — do not append a second copy. If it already contains `K109_BUSL1_PB0`\n'
 '> and `K110_ACM18_BST`, the repair is already in place and only verification is owed. Any other hash: stop and\n'
 '> re-derive, because the tree has moved again.\n\n')
if 'THE TREE HAS ALREADY BEEN WRITTEN' not in t:
    t=t.replace(old, add+old)
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('APPLY doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('applied-write warning present:','THE TREE HAS ALREADY BEEN WRITTEN' in r.decode('utf-8'))