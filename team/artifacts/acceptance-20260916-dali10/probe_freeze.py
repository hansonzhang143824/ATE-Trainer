# probe_freeze.py — 冻结证据：现盘哈希/mtime/revision/U 一致性/pin/短时稳定复读
import hashlib
import json
import os
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep


def snap(name):
    p = D + name
    if not os.path.exists(p):
        return None
    b = open(p, "rb").read()
    st = os.stat(p)
    return {
        "name": name,
        "size": len(b),
        "sha256": hashlib.sha256(b).hexdigest(),
        "mtime": time.strftime("%H:%M:%S", time.localtime(st.st_mtime)),
        "now": time.strftime("%H:%M:%S"),
    }


print("=== 现盘快照（第一次读取）===")
first = {}
for f in ("setup-contract.json", "test-plan.json", "setup-contract-pin.json"):
    s = snap(f)
    first[f] = s
    if s:
        print("  %-28s %8d B  %s  mtime=%s  read_at=%s" % (s["name"], s["size"], s["sha256"], s["mtime"], s["now"]))
    else:
        print("  %-28s MISSING" % f)

c = json.loads(open(D + "setup-contract.json", encoding="utf-8").read())
print("\n  contract revision =", c.get("revision"), "| generatedAt =", str(c.get("generatedAt"))[:60])
print("  BD08-SCOPE-01 present:", "BD08-SCOPE-01" in json.dumps(c, ensure_ascii=False))
for tm in ("TM102", "TM103", "TM108", "TM109"):
    d = (c.get("tmDeltas") or {}).get(tm) or {}
    print("    %-6s ateStimulus=%-5s stimulusScopeNote=%-5s simRef=%-5s" % (
        tm, "ateStimulus" in d, "stimulusScopeNote" in d, "simulationDomainReference" in d))

print("\n=== 短时稳定复读（间隔 6 秒）===")
time.sleep(6)
for f in ("setup-contract.json", "test-plan.json"):
    s = snap(f)
    same = s["sha256"] == first[f]["sha256"]
    print("  %-28s %s  (hash %s, mtime %s)" % (f, "STABLE" if same else "CHANGED", s["sha256"][:16], s["mtime"]))

p = json.loads(open(D + "setup-contract-pin.json", encoding="utf-8").read())
print("\n=== pin ===")
for k in ("revision", "sizeBytes", "sha256", "measuredAt", "frozen", "frozenBy", "freezeRule"):
    if k in p:
        print("  %-12s %s" % (k, str(p[k])[:110]))
print("  pin.sha256 == artifact.sha256 :", p.get("sha256") == first["setup-contract.json"]["sha256"])
