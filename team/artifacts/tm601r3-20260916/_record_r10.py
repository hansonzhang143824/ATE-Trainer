# -*- coding: utf-8 -*-
"""Round-10 recorder: sandbox fix verification -> ledger + status + plan + pin."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
DOC = os.path.join(RUN, "sandbox-fix-verification.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PLAN = os.path.join(WS, "team", "EXECUTION_PLAN.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")
B = chr(96)


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


ds, dh = sig(DOC)
copy_sig = sig(os.path.join(RUN, "sandbox", "test.cpp.copy"))
fix_sig = sig(os.path.join(RUN, "sandbox", "test.cpp.k48k76"))
res_sig = sig(os.path.join(RUN, "sandbox", "fix-test-result.json"))

ledger = [
    "",
    "",
    "## 2026-09-17 01:2x +0800 沙箱实证：TM600 补 K48/K76 使门禁契约断言由红转绿",
    "",
    "- 新增 " + B + "sandbox-fix-verification.md" + B + " = %d B / " % ds + B + dh + B + "；脚本 " + B + "sandbox_fix_test.py" + B
    + "；结果 " + B + "sandbox/fix-test-result.json" + B + " = %d B / " % res_sig[0] + B + res_sig[1] + B + "。",
    "- **方法**：逐字节复制目标树到 " + B + "sandbox/test.cpp.copy" + B + "（= 原件 " + B + "15c7d2b8…" + B + "），"
      "仅在 TM600 那一次 SetOn 内追加 " + B + "K48_ACM5_AMP_REF, K76_ACM_BST" + B + "（锚点唯一，脚本内 assert n==1），"
      "产出 " + B + "sandbox/test.cpp.k48k76" + B + " = %d B / " % fix_sig[0] + B + fix_sig[1] + B + "（+31 B）。",
    "- **结果（逐字）**：用例 A（未编辑）" + B + "TM600 缺失=[48,76]" + B + "、" + B + "targets=4 FAIL=2" + B
    + "、exit **1**；用例 B（加两腿）" + B + "TM600 缺失=[]" + B + "、" + B + "FAIL=0" + B
    + "、输出 " + B + "BST-SW SEQUENCE PASSED" + B + "、exit **0**。",
    "- **结论 1**：该修法**在沙箱内被实证**可使契约闭集断言转绿（非预测）。",
    "- **结论 2（重要限制）**：该门**只校验闭集、不校验阶梯** —— BST 源设 5 V / 10 V / 20 V 都不影响本门红绿 ⇒ "
      "**门禁绿 ≠ 操作点正确**，V 值与阶梯必须由 " + B + "t7" + B + " 计划 + " + B + "t8" + B
    + " 独立审查 + 台架签核保证。",
    "- **结论 3**：本门只做文本集合比对，**不证明 K48/K76 的实际物理贯通**；TM601 因其契约闭集不含 BST 腿，"
      "该门对 TM601 的 BST 供给**仍无约束**，须经 " + B + "t6" + B + " 修订后才有效。",
    "- **边界**：目标树 " + B + "15c7d2b8…" + B + " 与 " + B + "devel " + B + "5c9cb3f9…" + B
    + " 前后哈希不变（实测）；沙箱副本仅存在于本 run 目录；未改门禁脚本/契约/计划；无机台验证。",
    "",
]

status = [
    "",
    "",
    "## 2026-09-17 01:2x +0800 沙箱实证：TM600 补 K48/K76 ⇒ 门禁契约断言转绿（R10）",
    "",
    "- 新增 " + B + "team/artifacts/tm601r3-20260916/sandbox-fix-verification.md" + B + " = %d B / " % ds + B + dh + B
    + "；沙箱副本 " + B + "sandbox/test.cpp.k48k76" + B + " = %d B / " % fix_sig[0] + B + fix_sig[1] + B + "。",
    "- **实证**：未编辑副本 → " + B + "TM600 缺失 [48,76]" + B + "、exit 1；**仅追加 K48+K76** → "
    + B + "TM600 缺失 []" + B + "、exit 0（" + B + "BST-SW SEQUENCE PASSED" + B + "）**。",
    "- **关键限制**：本门**只校验继电器闭集、不校验 BST 阶梯电压** ⇒ **门禁绿不等于操作点正确**；"
      "且它不证明继电器实际物理贯通。",
    "- **未动**：目标树 " + B + "15c7d2b8…" + B + "、devel " + B + "5c9cb3f9…" + B + "（前后哈希一致，实测）；未改脚本/契约/计划；无机台验证。",
    "",
]

plan_add = ("""

## 2026-09-17 01:2x +0800 沙箱实证补记（R10）

`team/artifacts/tm601r3-20260916/sandbox-fix-verification.md` = %d B / `%s`

- 在**沙箱副本**（非目标树）内仅追加 `K48_ACM5_AMP_REF, K76_ACM_BST` 到 TM600 的 SetOn：门禁契约断言由 `缺失=[48,76] exit 1` 变为 `缺失=[] exit 0`。
- **该门只校验闭集、不校验阶梯**：BST 设 5/10/20 V 都不影响它的红绿 ⇒ `t11` 不得以「门禁绿」替代操作点正确性；阶梯/寄存器/下电仍须 `t7`+`t8`+台架。
- 沙箱副本 `sandbox/test.cpp.k48k76` = %d B / `%s`（可作 `t9` 的实现对照，**但不得当作已审查候选**）。
""" % (ds, dh, fix_sig[0], fix_sig[1])).encode("utf-8")

with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + "\n".join(ledger).encode("utf-8"))

with open(STATUS, "rb") as f:
    sb = f.read()
with open(STATUS, "wb") as f:
    f.write(sb + "\n".join(status).encode("utf-8"))

with open(PLAN, "rb") as f:
    pb = f.read()
with open(PLAN, "wb") as f:
    f.write(pb + plan_add)

man = json.load(open(PIN, encoding="utf-8"))
man["sandboxFixVerification"] = {
    "doc": {"path": DOC, "size": ds, "sha256": dh},
    "script": {"path": os.path.join(RUN, "sandbox_fix_test.py"), "size": sig(os.path.join(RUN, "sandbox_fix_test.py"))[0],
               "sha256": sig(os.path.join(RUN, "sandbox_fix_test.py"))[1]},
    "copy": {"path": copy_sig and os.path.join(RUN, "sandbox", "test.cpp.copy"), "size": copy_sig[0], "sha256": copy_sig[1]},
    "fixed": {"path": os.path.join(RUN, "sandbox", "test.cpp.k48k76"), "size": fix_sig[0], "sha256": fix_sig[1]},
    "result": {"path": os.path.join(RUN, "sandbox", "fix-test-result.json"), "size": res_sig[0], "sha256": res_sig[1]},
    "outcome": "unedited copy exit 1 (TM600 missing [48,76]); +K48/K76 exit 0 (missing []); gate checks closures only, not the staircase",
}
for name, path in (("run_ledger", LEDGER), ("current_status", STATUS), ("execution_plan", PLAN)):
    s, h = sig(path)
    man["files"][name] = {"path": path, "size": s, "sha256": h, "note": "refreshed after this session's own appends"}
for key in ("old_team_json", "setup_contract_old", "test_plan_old"):
    rec = man["files"].get(key) or {}
    p = rec.get("path")
    if p and os.path.exists(p):
        s, h = sig(p)
        if h != rec.get("sha256"):
            rec.update({"size": s, "sha256": h, "note": "live artifact of the OTHER run; refreshed after observed drift"})
            print("refreshed", key, s, h[:12])
json.dump(man, open(PIN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("doc:", ds, dh)
print("fixed copy:", fix_sig)
print("ledger:", sig(LEDGER))
print("status:", sig(STATUS))
print("plan:", sig(PLAN))
print("pin:", sig(PIN))
