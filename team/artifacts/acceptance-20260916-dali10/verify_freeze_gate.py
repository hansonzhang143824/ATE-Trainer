# verify_freeze_gate.py — 实现任务前的独立冻结复验（Captain）
# 检查：双字节哈希/大小、revision、schema、U canonical、BST (ii)、pin 全项 true 且哈希一致、短时稳定复读
import hashlib
import json
import os
import subprocess
import sys
import time

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
W = "D:/Newtest/DSH/ATE-Coding-Plat/"
D = W + "team/artifacts/acceptance-20260916-dali10/"
results = []


def rec(name, ok, ev):
    results.append((name, ok, ev))
    print("  [%s] %-52s %s" % ("PASS" if ok else "FAIL", name, ev))


def snap(f):
    b = open(D + f, "rb").read()
    st = os.stat(D + f)
    return b, hashlib.sha256(b).hexdigest(), len(b), st.st_mtime


print("=== 1. 现盘快照（同一次读取）===")
sc_b, sc_h, sc_n, sc_m = snap("setup-contract.json")
tp_b, tp_h, tp_n, tp_m = snap("test-plan.json")
pin_b, pin_h, pin_n, pin_m = snap("setup-contract-pin.json")
ip_b, ip_h, ip_n, ip_m = snap("implementation-input-pin.json")
for nm, n, h, m in (("setup-contract.json", sc_n, sc_h, sc_m),
                    ("test-plan.json", tp_n, tp_h, tp_m),
                    ("setup-contract-pin.json", pin_n, pin_h, pin_m),
                    ("implementation-input-pin.json", ip_n, ip_h, ip_m)):
    print("  %-32s %8d B  %s  mtime=%s" % (nm, n, h, time.strftime("%H:%M:%S", time.localtime(m))))

sc = json.loads(sc_b.decode("utf-8"))
tp = json.loads(tp_b.decode("utf-8"))
pin = json.loads(pin_b.decode("utf-8"))

print("\n=== 2. schema ===")
for art, path in (("setup-contract", "setup-contract.json"), ("test-plan", "test-plan.json")):
    r = subprocess.run([sys.executable, "scripts/validate_team_artifact.py", art, D + path],
                       cwd=W, capture_output=True, text=True)
    rec("schema " + art + " exit 0", r.returncode == 0, "exit=%d" % r.returncode)

print("\n=== 3. U 编号 canonical ===")


def oi(doc, iid):
    for i in (doc.get("openItems") or []):
        if isinstance(i, dict) and i.get("id") == iid:
            return str(i.get("topic", "")) + " " + str(i.get("detail", ""))
    return ""


rec("setup-contract U10 = QVM concurrency", "QVM" in oi(sc, "U10") and "concurr" in oi(sc, "U10").lower(),
    oi(sc, "U10")[:60])
rec("setup-contract U11 = SIGN-CONVENTION", "SIGN-CONVENTION" in oi(sc, "U11"), oi(sc, "U11")[:60])
tps = tp_b.decode("utf-8")
rec("test-plan limitations U10 = QVM", "U10 - QVM" in tps, "U10 - QVM hits=%d" % tps.count("U10 - QVM"))
rec("test-plan limitations U11 = SIGN-CONVENTION", "U11 - SIGN-CONVENTION" in tps,
    "U11 - SIGN-CONVENTION hits=%d" % tps.count("U11 - SIGN-CONVENTION"))

print("\n=== 4. BST-SW 裁定 (ii) ===")
rec("test-plan BST baseline = SW12_U1REF_BST_ACM", tps.count("SW12_U1REF_BST_ACM") >= 1,
    "hits=%d" % tps.count("SW12_U1REF_BST_ACM"))
rec("test-plan FPVIe1-CH1 = unrealisable", "INTENDED BUT CURRENTLY UNREALISABLE" in tps,
    "hits=%d" % tps.count("INTENDED BUT CURRENTLY UNREALISABLE"))
scs = sc_b.decode("utf-8")
rec("setup-contract BST = SW12_U1REF_BST_ACM", scs.count("SW12_U1REF_BST_ACM") >= 1,
    "hits=%d" % scs.count("SW12_U1REF_BST_ACM"))

print("\n=== 5. pin ===")
checks = pin.get("checks") or {}
rec("pin all checks true", bool(checks) and all(checks.values()), json.dumps(checks, ensure_ascii=False))
rec("pin.sha256 == setup-contract sha256", pin.get("sha256") == sc_h, "%s" % str(pin.get("sha256"))[:24])
rec("pin twoRunsByteIdentical", pin.get("twoRunsByteIdentical") is True and pin.get("twoConsecutiveRunsIdentical") is True,
    str(pin.get("twoRunHashes"))[:70])
rec("pin frozenAt is real wall clock", "real wall clock" in str(pin.get("frozenAtKind", "")),
    "%s | %s" % (pin.get("frozenAt"), pin.get("frozenAtKind")))

print("\n=== 6. t18 撤回与冲突登记 ===")
deltas = sc.get("tmDeltas") or {}
rec("four items: ateStimulus removed", all("ateStimulus" not in (deltas.get(t) or {}) for t in ("TM102", "TM103", "TM108", "TM109")), "TM102/103/108/109")
rec("conflict registered with both sides", "Neither side is averaged or deleted" in scs and "DFT.csv lines 12" in scs,
    "both-side locator text present")
rec("provenance: keep-ruling superseded", "SUPERSEDED, not pending" in scs, "provenance sentence present")

print("\n=== 7. 短时稳定复读（间隔 6 秒）===")
time.sleep(6)
for f, h0 in (("setup-contract.json", sc_h), ("test-plan.json", tp_h)):
    b2, h2, n2, m2 = snap(f)
    rec("stable: " + f, h2 == h0, "%s (mtime %s)" % (h2[:24], time.strftime("%H:%M:%S", time.localtime(m2))))

bad = [n for n, ok, _ in results if not ok]
print("\n=== 汇总结论 ===")
print("  checks=%d  PASS=%d  FAIL=%d" % (len(results), len(results) - len(bad), len(bad)))
print("  FAILED:", bad if bad else "NONE")
print("  FROZEN INPUTS: setup-contract.json %s (%d B) | test-plan.json %s (%d B)" % (sc_h, sc_n, tp_h, tp_n))
raise SystemExit(1 if bad else 0)
