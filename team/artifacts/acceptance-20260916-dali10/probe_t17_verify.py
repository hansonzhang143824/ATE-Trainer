# probe_t17_verify.py — t17 收口核验：BST (ii) 文本 + 编号 + 幂等 + 哈希
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
b = open(D + "test-plan.json", "rb").read()
t = b.decode("utf-8")
c = json.loads(t)

print("test-plan.json = %d B / %s" % (len(b), hashlib.sha256(b).hexdigest()))
print("revision[:110] =", str(c.get("revision"))[:110])
print("generatedAt    =", str(c.get("generatedAt"))[:110])

keys = [
    "SW12_U1REF_BST_ACM",
    "INTENDED BUT CURRENTLY UNREALISABLE",
    "[110,61]",
    "ALTERNATIVE-NOT-ADOPTED",
    "U10 - QVM",
    "U11 - SIGN-CONVENTION",
    "revision-derived constant",
    "wall clock",
]
for k in keys:
    print("  %-42s hits=%d" % (k, t.count(k)))

print("\n--- assumptions 中的 BST 段（前 300 字）---")
for it in c.get("items", []):
    if it.get("tm") == "TM600":
        for a in (it.get("assumptions") or []):
            if "arbitration" in a.lower() or "BST" in a:
                print("  ", a[:300])
                break

print("\n--- globalRulesApplied 中的 R-BST-SW ---")
for r in (c.get("globalRulesApplied") or []):
    if "R-BST-SW" in r:
        print("  ", r[:300])
