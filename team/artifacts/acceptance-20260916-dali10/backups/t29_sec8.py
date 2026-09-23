import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t29-k110-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
add=('## 8. Deployed-tree state at the time of this repair (measured, not relayed)\n\n'
 '`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` = **469714 B / '
 '`15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a`**, mtime **2026-09-16 18:53:33**.\n\n'
 'Measured facts (my own read, cross-checked because a relayed description differed):\n\n'
 '- `DUT_API int TM600_HS_RDSON` occurs **1** time, at **L9057**; `DUT_API int TM601_LS_RDSON` occurs **1** time,\n'
 '  at **L9217**. (A relayed reading claimed 2 occurrences each; that is not what the file contains.)\n'
 '- **L9081** `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1)`\n'
 '  closes 60, 61, 83 — the PMID side — and **neither K109 nor K110**.\n'
 '- **L9255** closes `K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` — 154, 155, 60, 61.\n'
 '- `K109_BUSL1_PB0` = **0** and `K110_ACM18_BST` = **0** occurrences: the deployed build predates this repair.\n\n'
 '**Conclusion:** the write HAS happened (executor = the captain under the agreed split), and it landed the\n'
 '**t23** revision — the `K126_V1P5_CAP` rename and the `ERROR_RES` fail-closed guard are present. It therefore\n'
 '**carries the t29 defect** (BST excitation path unclosed), and `afterSha256` for THIS repair must not be filled\n'
 'with `15c7d2b8…`: that hash belongs to the superseded revision, and recording it as the after-state of the\n'
 'K109/K110 payload would assert a landing that has not happened.\n\n')
anchor='## 7. Scope, authorship, open items'
if 'Deployed-tree state at the time of this repair' not in t:
    t=t.replace(anchor, add.split('## 8. ')[0]+'## 8. '+'Deployed-tree state at the time of this repair (measured, not relayed)\n\n'+add.split('\n\n',1)[1]+anchor)
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('section 8 present:','Deployed-tree state at the time of this repair' in r.decode('utf-8'))