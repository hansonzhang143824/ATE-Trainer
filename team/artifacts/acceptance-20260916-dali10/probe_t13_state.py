# probe_t13_state.py — t13 三项更正与冻结前状态的权威核对
import hashlib
import json
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep

for f in ("setup-contract.json", "test-plan.json"):
    b = open(D + f, "rb").read()
    print("%-24s %8d B  %s" % (f, len(b), hashlib.sha256(b).hexdigest()))

t = open(D + "setup-contract.json", "rb").read().decode("utf-8")
print("\n--- t13 三项核对（setup-contract.json）---")
print("  U10 hits            =", t.count("U10"))
print("  U11 hits            =", t.count("U11"))
print("  old key voltageDifferentialPreferred =", t.count("voltageDifferentialPreferred"))
print("  new key voltageDifferentialCandidateDisputed =", t.count("voltageDifferentialCandidateDisputed"))
mark = "THIS item's OWN DFT.csv row"
print("  own-DFT attribution =", t.count(mark))
print("  BD-08 scope-limited note =", t.count("TM600/TM601 ONLY"))

c = json.loads(t)
print("\n--- 四个 supply-rail 项的归属 ---")
for tm in ("TM102", "TM103", "TM108", "TM109", "TM600", "TM601"):
    d = c.get("tmDeltas", {}).get(tm, {})
    a = d.get("ateStimulus")
    print("  %-6s %s" % (tm, json.dumps(a, ensure_ascii=False)[:130]))

g = open(D + "setup-contract-build.py", "rb").read().decode("utf-8-sig")
print("\n--- 生成器状态 ---")
print("  build.py U10=%d U11=%d ownDFT=%d oZk=%d" % (
    g.count("U10"), g.count("U11"), g.count(mark), g.count("voltageDifferentialPreferred")))
