# -*- coding: utf-8 -*-
"""Standing consistency audit for dft-ir.json: re-runs the producer and confirms the
sidecar digest, schema validation and self-checks all agree. Used as the t1 wrap-up gate."""
import os, subprocess, sys, hashlib, json
sys.stdout.reconfigure(encoding='utf-8')
ROOT = r"D:/Newtest/DSH/ATE-Coding-Plat"
RUN = "acceptance-20260916-dali10"
ART = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-ir.json')
SCRIPTS = os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'scripts')
PY = sys.executable

def run(args):
    p = subprocess.run([PY, '-X', 'utf8'] + args, cwd=ROOT, capture_output=True, text=True, encoding='utf-8', errors='replace')
    return p.returncode, (p.stdout or '') + (p.stderr or '')

def digest():
    b = open(ART, 'rb').read()
    return hashlib.sha256(b).hexdigest(), len(b)

rc1, out1 = run([os.path.join(SCRIPTS, 'dft_ir_hashes.py')])
d1 = digest()
rc2, out2 = run([os.path.join(SCRIPTS, 'dft_ir_verify.py')])
d2 = digest()
rc3, out3 = run([os.path.join(ROOT, 'scripts', 'validate_team_artifact.py'), 'dft-ir', ART.replace(ROOT + os.sep, '')])
d3 = digest()
side = json.load(open(os.path.join(ROOT, 'team', 'artifacts', RUN, 'dft-raw', 'dft-ir-hashes.json'), encoding='utf-8'))['deliverable']

print('hashes.py   exit', rc1, '| artifact', d1)
print('verify.py   exit', rc2, '| artifact', d2, '|', out2.strip().splitlines()[-1])
print('validate.py exit', rc3, '| artifact', d3, '|', out3.strip().splitlines()[-1])
print('sidecar digest', side['sha256'], side['size'])
ok = (rc1 == 0 and rc2 == 0 and rc3 == 0 and len({d1[0], d2[0], d3[0]}) == 1
      and side['sha256'] == d1[0] and side['size'] == d1[1])
print('CONVERGED' if ok else 'NOT CONVERGED')
sys.exit(0 if ok else 1)
