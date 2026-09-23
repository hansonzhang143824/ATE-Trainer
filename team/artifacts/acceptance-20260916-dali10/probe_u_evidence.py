# probe_u_evidence.py — 现盘 U 编号证据（openItems + polarityDecision 四子字段 + pin）
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep

b = open(D + "setup-contract.json", "rb").read()
c = json.loads(b.decode("utf-8"))
print("setup-contract.json = %d B / %s" % (len(b), hashlib.sha256(b).hexdigest()))
print("revision =", c.get("revision"), "| generatedAt =", c.get("generatedAt"))

print("\n--- openItems U10/U11 ---")
for i in c.get("openItems", []):
    if isinstance(i, dict) and i.get("id") in ("U10", "U11"):
        print("  %-4s topic=%s" % (i.get("id"), i.get("topic")))
        print("       detail[:150]=%s" % str(i.get("detail"))[:150])

print("\n--- polarityDecision.signConventionFinding 四子字段 ---")
f = (c.get("polarityDecision") or {}).get("signConventionFinding") or {}
ac = f.get("derivationChain") or {}
for k in ("status", "captainRuling", "escalation"):
    v = str(f.get(k, ""))
    print("  %-16s ...%s" % (k, v[-160:] if k != "captainRuling" else v[-200:]))
print("  assumptionToVerify ...%s" % str(ac.get("assumptionToVerify", ""))[:160])

print("\n--- 计数（U10/U11 及其与主题的关键词共现）---")
s = json.dumps(c, ensure_ascii=False)
print("  'U10' hits=%d  'U11' hits=%d" % (s.count("U10"), s.count("U11")))
print("  U10+QVM 同串=%d  U11+SIGN-CONVENTION 同串=%d" % (
    s.count("U10 = QVM ch0 concurrency"), s.count("U11 = SIGN-CONVENTION")))

pin = os.path.join(D, "setup-contract-pin.json")
if os.path.exists(pin):
    pb = open(pin, "rb").read()
    p = json.loads(pb.decode("utf-8"))
    print("\n--- setup-contract-pin.json (%d B) ---" % len(pb))
    for k in ("revision", "size", "sizeBytes", "sha256", "mtime", "measuredAt", "idempotency", "t16checks"):
        if k in p:
            print("  %-14s %s" % (k, str(p[k])[:160]))
    print("  top-level keys:", list(p.keys())[:14])
else:
    print("\nNO pin file")
