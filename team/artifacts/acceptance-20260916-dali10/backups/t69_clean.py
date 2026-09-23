import sys,io,os,re,hashlib,tempfile,shutil
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
b=os.path.join(d,'backups')
print('=== t4 check: scratch scripts with NOW-FALSE hash assertions ===')
for f in sorted(os.listdir(b)):
    if not f.endswith('.py'): continue
    p=os.path.join(b,f); t=open(p,encoding='utf-8-sig',errors='replace').read()
    has_old='6034af71' in t
    has_assert=bool(re.search(r"'6034af71|MATCH",t))
    if has_old:
        print('  %-28s mentions 6034af71: True | has MATCH-style assert: %s'%(f,has_assert))
        for i,l in enumerate(t.split('\n')):
            if '6034af71' in l: print('       L%d: %s'%(i+1,l.strip()[:110]))
print()
print('=== and the current scratch dir contents ===')
files=sorted(os.listdir(b))
print('  %d files'%len(files))
for f in files[:8]: print('   ',f)
print('   ...' if len(files)>8 else '')
print()
print('=== ACTION: retire the scratch scripts to a subdir with a README (non-destructive) ===')
sub=os.path.join(b,'superseded-scratch')
os.makedirs(sub,exist_ok=True)
moved=[]
for f in files:
    if f.endswith('.py'):
        src=os.path.join(b,f); dst=os.path.join(sub,f)
        shutil.move(src,dst); moved.append(f)
readme=('''# superseded-scratch — one-off verification helpers, NOT authoritative

These scripts were used during the t29/t38/t50/t55/t56 work to *verify* states at the moment they ran.
**They contain hardcoded hash assertions that were true at the time and are NOT true now** — e.g. several
assert or print `MATCH` for `6034af71...` (the t50 UNION revision, 41,797 B), which was written to the
canonical payload path at 20:48:18 and superseded at 20:59:12. Running them today will report a mismatch,
and that mismatch is EXPECTED; it is not a defect in the payload.

They are kept only because they are the receipts that the union revision *existed* (t4/rule-reviewer used
them that way). For any current verification use the live commands instead:

    python scripts/verify_relay_trace.py --meta --src <sandbox test.cpp> --defines <sandbox StdAfx.h>
    python scripts/verify_bst_sw_sequence.py --src <sandbox test.cpp>
    python scripts/verify_awg_params.py --src <sandbox test.cpp>

Canonical payload: implementation-payload-TM600-TM601.cpp = %s B / %s
Recorded by: ate-implementer. Frozen: no payload writes since 21:09:24.
''')
r=open(os.path.join(d,'implementation-payload-TM600-TM601.cpp'),'rb').read()
open(os.path.join(sub,'README.md'),'w',encoding='utf-8').write(readme%(len(r),hashlib.sha256(r).hexdigest()))
print('  moved %d .py files into superseded-scratch/ and wrote a README warning'%len(moved))
print('  remaining in backups/: %s'%sorted(os.listdir(b)))