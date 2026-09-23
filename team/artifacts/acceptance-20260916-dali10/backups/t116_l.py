import sys,io,os,re
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
print('=== TESTING THEIR PREDICTION: an L1-style citation carries L-a qualifiers; an L2-style one drops them ===')
print()
print('  MY MANIFEST (I control it) — how do I cite OTHER artefacts?')
mp=os.path.join(d,'implementation-manifest.json')
J=open(mp,'rb').read().decode('utf-8-sig')
for pat in ['t40-tm601-bst-evidence.md','t42','t44']:
    for m in re.finditer(re.escape(pat),J):
        seg=J[max(0,m.start()-120):m.start()+160]
        has_hash=bool(re.search(r'[0-9a-f]{16,}',seg))
        print('    %-26s window has hash: %-5s  ...%s'%(pat,has_hash,seg.replace('\\n',' ')[:110]))
        break
print()
print('  => if my manifest cites others by PATH with no value, that is L2 and I should DROP their value-level qualifiers.')
print()
print('=== and does my manifest cite my OWN payload L1 or L2? ===')
m=re.search(r'"artefact":\s*"implementation-payload-TM600-TM601\.cpp"',J)
if m:
    seg=J[m.start():m.start()+420]
    print('    %s'%seg.replace('\\n',' ')[:400])