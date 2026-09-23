import sys,io,os,re,hashlib,shutil,json
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
# archive the predecessor revision so the old version is preserved on disk as history
hist=os.path.join(d,'payload-history'); os.makedirs(hist,exist_ok=True)
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp')
cur=open(p,'rb').read()
print('current payload: %d B / %s'%(len(cur),hashlib.sha256(cur).hexdigest()))
note=os.path.join(hist,'README.md')
open(note,'w',encoding='utf-8').write(
 '# Payload revision history (kept, never deleted)\n\n'
 '| revision | size | sha256 | note |\n| --- | --- | --- | --- |\n'
 '| t29 (current) | 36381 B | 73b511b775beda61cc91ea41fdc5358e53579fb4e32cc553bf47792667fea19e | TM600 closes K109/K110 (BST excitation path, contract conformance) |\n'
 '| t23 | 35014 B | 444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c | K126 fix + ERROR_RES fail-closed + sign fix + ranges; TM600 SetOn lacked K109/K110 |\n'
 '| t21 rev3 | 32969 B | 7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b | K5/K44/K45 removed per t22 |\n'
 '| t21 rev2 | 34788 B | f2e020bf64ab7384c9b547a8fd8a0f4cdda1b4595eed9a3d60a6bf3f9cbcc509 | sign/ERROR_RES/ranges applied |\n'
 '| t21 rev1 | 28726 B | c8bf3b3e693673bb92c04fc7c34d8529a1c2a02c785fbaa507f2387956fcd86e | caps added (later reverted) |\n'
 '| t20 | 28222 B | 7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122 | delivered payload at t20 |\n')
print('history README written:',os.path.exists(note))
# confirm deployed revision identifies the predecessor, not this one
t=open(r'D:\PROJECT6-DALI\ForCodexDebug\source\test.cpp','rb').read().decode('utf-8-sig')
s=t.find('DUT_API int TM600_HS_RDSON'); e=t.find('DUT_API int TM601_LS_RDSON')
blk=t[s:e]
print()
print('=== deployed TM600/TM601 blocks: cap/relay counts (executable) ===')
code=[l for l in blk.split('\n') if not l.strip().startswith('//')]
for k in ['K5_VBUS_Cap','K44_Cap_SW2_BST2','K45_Cap_SW1_BST1','K109','K110','K126_V1P5_CAP']:
    print('  %-22s %d'%(k,sum(l.count(k) for l in code)))