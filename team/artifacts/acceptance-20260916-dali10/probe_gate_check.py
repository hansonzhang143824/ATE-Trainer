# probe_gate_check.py — 一致性门放行条件的可复现检查（Captain）
# 运行：python team/artifacts/acceptance-20260916-dali10/probe_gate_check.py
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep


def load(name):
    with open(D + name, "rb") as f:
        b = f.read()
    return b, b.decode("utf-8")


print("=== 现算哈希 ===")
for f in ["setup-contract.json", "test-plan.json", "dft-ir.json", "schematic-ir.json"]:
    try:
        b, _ = load(f)
    except OSError:
        print("  MISSING", f)
        continue
    print("  %-24s %9d B  %s" % (f, len(b), hashlib.sha256(b).hexdigest()))

print("\n=== test-plan.json：t11 放行条件 ===")
tp = load("test-plan.json")[1]
T = json.loads(tp)
print("  bench-signoff             :", tp.count("bench-signoff"))
print("  simulationDomainReference :", tp.count("simulationDomainReference"))
print("  closed-for-this-run       :", tp.count("closed-for-this-run"))
print("  U11 (SIGN-CONVENTION)     :", tp.count("U11"))
print("  U10                       :", tp.count("U10"))
print("  delay_ms(1) / delay_ms(2) :", tp.count("delay_ms(1)"), "/", tp.count("delay_ms(2)"))
print("  '1 ms' settle mentions    :", len(re.findall(r"settle[^\"]{0,60}1 ms", tp)))
lim = T.get("limitations", [])
print("  limitations count         :", len(lim))
print("  U11 in limitations        :", any("U11" in json.dumps(x, ensure_ascii=False) for x in lim))
print("  BD-06/BD-07 in limitations:", any("BD-06" in json.dumps(x, ensure_ascii=False) for x in lim),
      "/", any("BD-07" in json.dumps(x, ensure_ascii=False) for x in lim))
for bid in ("BD-04", "BD-06", "BD-07", "BD-08"):
    for b in T.get("blockingDecisions", []):
        if b.get("id") == bid:
            print("   %-6s -> %s" % (bid, str(b.get("status"))[:80]))

print("\n=== setup-contract.json：t12 放行条件 ===")
raw = load("setup-contract.json")[1]
print("  simulationDomainReference :", raw.count("simulationDomainReference"))
print("  U10 / U11                 :", raw.count("U10"), "/", raw.count("U11"))
print("  voltageDifferentialPreferred:", raw.count("voltageDifferentialPreferred"))
print("  --- Step 2 power on 原文 ---")
for m in re.finditer(r"Step 2 power on[^\"]{0,220}", raw):
    print("   ", m.group(0))
print("  --- 3.5 作激励的上下文（排除 simulationDomain 段）---")
hit = False
for m in re.finditer(r"3\.5", raw):
    seg = raw[max(0, m.start() - 140): m.start() + 90].replace("\n", " ")
    if "simulationDomain" not in seg:
        print("   ...%s..." % seg)
        hit = True
if not hit:
    print("    （无：3.5 仅出现在 simulationDomainReference 内或已移除）")
