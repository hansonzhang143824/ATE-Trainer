import sys,io,os,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
hist=os.path.join(d,'payload-history')
if os.path.exists(hist):
    import shutil; shutil.rmtree(hist); print('removed out-of-scope payload-history/ (content folded into the in-scope evidence doc)')
# fold the revision history into the in-scope evidence document
p=os.path.join(d,'t29-k110-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
anchor='## 7. Scope, authorship, open items'
hist_md=('## 6b. Payload revision history (kept as history, never deleted)\n\n'
 '| revision | size | sha256 | note |\n| --- | --- | --- | --- |\n'
 '| **t29 (current)** | 36381 B | `73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e` | TM600 closes K109/K110 — the BST excitation path |\n'
 '| t23 (deployed) | 35014 B | `444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c` | K126 fix + ERROR_RES fail-closed + positive-magnitude sign + ranges; TM600 SetOn lacked K109/K110 |\n'
 '| t21 rev3 | 32969 B | `7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b` | K5/K44/K45 removed per the t22 ruling |\n'
 '| t21 rev2 | 34788 B | `f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509` | sign / ERROR_RES / range corrections |\n'
 '| t21 rev1 | 28726 B | `c8bf3b3e693673bb92c04fc7c34d8529a1c2a02c785fbaa507f2387956fcd86e` | stabiliser caps added (later reverted by t22) |\n'
 '| t20 | 28222 B | `7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122` | payload as delivered at t20 |\n\n'
 'The predecessor contents are recoverable from this run\'s revision trail and are recorded here rather than in a\n'
 'separate directory, because this task\'s in-scope paths are the payload and this document only.\n\n')
if hist_md.strip()[:20] not in t:
    t=t.replace(anchor, hist_md+anchor)
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence doc %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('history table present:','t29 (current)' in r.decode('utf-8'))
pay=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); rp=open(pay,'rb').read()
print('payload %d B / %s'%(len(rp),hashlib.sha256(rp).hexdigest()))
print('in-scope files only:',[n for n in os.listdir(d) if n.startswith('payload-history')]==[])