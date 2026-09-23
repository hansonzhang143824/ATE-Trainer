import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t50-payload-k76-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
add=('## 1b. Exit-code clarification, and a fact that widens the finding\n\n'
 'My first exit-code capture reported `bst-sw` exit **0**; that was **wrong** — the PowerShell pipeline was capturing\n'
 '`Select-Object`\'s status rather than the gate\'s. Re-measured with the exit code captured immediately after the\n'
 'invocation:\n\n'
 '```\n'
 'python scripts/verify_bst_sw_sequence.py --src <sandbox>   ->  exit 1\n'
 'python scripts/verify_bst_sw_sequence.py                  ->  exit 1   (scanning the DEPLOYED tree)\n'
 '```\n\n'
 '**And the second line matters more than the first:** the gate fails against the **deployed** `test.cpp`\n'
 '(`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp:9081`, which closes `K83, K60, K61, K13, K57, K85, K126` — no\n'
 '`K109/K110`, no `K48/K76`) **under the same rev-25 contract**. So this is **not** a consequence of my change: the\n'
 'rev-25 contract demands `K110` for TM600 while **neither the deployed tree nor the current payload closes it**.\n'
 'The mismatch is between the contract and the tree, and it pre-dates this edit. It does however mean the gate cannot\n'
 'pass in its described form until the rev-25 expectation is reconciled with what any implementation can satisfy.\n\n')
if 'Exit-code clarification' not in t:
    t=t.replace('## 2. The change applied', add+'## 2. The change applied')
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('section present:','Exit-code clarification' in r.decode('utf-8'))