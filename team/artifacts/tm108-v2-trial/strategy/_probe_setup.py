# read-only probe: dump structure keys of the frozen setup baseline (plaintext view via python)
import io
import re
import sys

sys.stdout.reconfigure(encoding='utf-8', errors='replace')

p = r'team/artifacts/acceptance-20260916-dali10/setup-contract.json'
lines = io.open(p, encoding='utf-8', errors='replace').read().splitlines()
pat = re.compile(r'^"([A-Za-z_][A-Za-z0-9_]*)"\s*:')
mode = sys.argv[1] if len(sys.argv) > 1 else 'keys'
if mode == 'keys':
    for i, l in enumerate(lines, 1):
        st = l.strip()
        m = pat.match(st)
        if m and (len(l) - len(l.lstrip())) <= 4:
            print(i, st[:130])
elif mode == 'range':
    a = int(sys.argv[2])
    b = int(sys.argv[3])
    for i in range(a, min(b, len(lines)) + 1):
        print(i, lines[i - 1])
