# t13 patch (part 2) — stimuliSourceNote 的 BD-08 归属改写
# 运行：python team/artifacts/acceptance-20260916-dali10/apply_t13_patch2.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "setup-contract-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")
orig = t

reps = [
    ('" (BD-08). The IR text below cites reg_config .sv as its source; per BD-08 that is a "',
     '" taken from THIS item\'s OWN DFT.csv row (BD-08\'s \'standby/supply = 4.2 V\' clause covers TM600/TM601 ONLY and is NOT the basis here). The IR text below cites reg_config .sv as its source, which per the stimulus-layer rule is a "'),
    ('"simulation-domain reference only and does not govern the ATE stimulus. Registered divergence: "',
     '"simulation-domain reference only and does not govern the ATE stimulus. Registered divergence: "'),
    ('" (BD-08)"', '" (own DFT.csv row)"'),
    ('BD-08 \'standby/supply = 4.2 V\' as declared by the DFT.csv row',
     'THIS item\'s OWN DFT.csv row (BD-08 covers TM600/TM601 only)'),
]

for old, new in reps:
    n = t.count(old)
    if n:
        t = t.replace(old, new)
    print("replaced %d x  <- %s" % (n, old[:60]))

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("changed:", t != orig, "| bytes:", len(data))
