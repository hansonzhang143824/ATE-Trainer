# -*- coding: utf-8 -*-
"""Round-11 recorder: TM601 sandbox test + node-fact resolution."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
DOC = os.path.join(RUN, "r11-tm601-sandbox-and-node-facts.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")
B = chr(96)


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


ds, dh = sig(DOC)
fixed = sig(os.path.join(RUN, "sandbox", "test.cpp.tm601_bstleg"))
res = sig(os.path.join(RUN, "sandbox", "tm601-fix-test-result.json"))

ledger = [
    "",
    "",
    "## 2026-09-17 01:4x +0800 TM601 修法沙箱测试 + 「双驱动」假阳性更正",
    "",
    "- 新增 " + B + "r11-tm601-sandbox-and-node-facts.md" + B + " = %d B / " % ds + B + dh + B
    + "；副本 " + B + "sandbox/test.cpp.tm601_bstleg" + B + " = %d B / " % fixed[0] + B + fixed[1] + B
    + "；结果 " + B + "sandbox/tm601-fix-test-result.json" + B + " = %d B / " % res[0] + B + res[1] + B + "。",
    "- **沙箱结果（预期正确但必须写明）**：给 TM601 追加 K48/K76 后门禁 **exit 仍为 1**，因为**红因只在 TM600**；"
      "冻结契约 rev36 的 TM601 期望集只有 `[60,61,154,155]`、**不含任何 BST 腿** ⇒ **该门无法验证 TM601 的 BST 修法**，"
      "必须先由 `t6` 把 BST 腿写进契约。⇒ 写进 `t11` 口径，否则会误判「TM601 修法无效」。",
    "- **自我更正（第 6 次）**：我用裸 token 启发式扫描后怀疑「TM600/TM601 修法造出前所未有的电路组合（ACM200 与 FPVIe0 同接 SW）」——**撤回**。"
      "根因是部署态**大量使用复合宏**（`K_FPVIH_TO_PMID_A` 等），启发式漏识别；宏展开后 `TM640:7513` 的闭集 = `83+60+61+13+57+48+76+65`，"
      "**与 TM600 补两条腿后的形状同类**。",
    "- **电路消解（FACT + INFERENCE）**：" + B + "SCH:673-674" + B + " 与 " + B + ":178-179/775-776" + B
    + " 显示 `K48` 是**同一物理线上的接口开关**：通电 → `K76`（BST），释放 → 默认投 `K49`（SW1）；"
      "`K61` 另在 `SW_F/SW_S` 节点（`SCH:771-773`）上。⇒ `S5_ACM200_FH5` 与 `S1_FPVIe_FL0` **不是同时驱动的两源**，"
      "而是经互斥支路接向 BST 与 SW ⇒ **「双驱动」不成立**，修法是已知形状的复用。",
    "- **仍存在的真实限制**：① 门禁只比文本集合（不校验贯通与 V 值）；② `K48(NC)` 与 `K48(ON)` 通往不同目的地，"
      "必须**同一次 SetOn**、不得另起第二次调用；③ **TM640 闭集含 K46 而 TM600 既有闭集不含 K46** ⇒ "
      "「TM600 只补 K48/K76 是否够」须由 `t2` 判定；④ TM601 的 BST 供给是否必需仍是 `t2/t7` 的问题。",
    "- 边界：目标树 " + B + "15c7d2b8…" + B + " 与 devel " + B + "5c9cb3f9…" + B + " 前后哈希不变；未改脚本/契约/计划/源码；无机台验证。",
    "",
]

status = [
    "",
    "",
    "## 2026-09-17 01:4x +0800 TM601 修法沙箱测试 + K48 接口节点消解（R11）",
    "",
    "- 新增 " + B + "team/artifacts/tm601r3-20260916/r11-tm601-sandbox-and-node-facts.md" + B + " = %d B / " % ds + B + dh + B + "。",
    "- **沙箱**：TM601 追加 K48/K76 后门禁 exit 仍 1（红因只在 TM600），因为契约 rev36 **未给 TM601 登记 BST 腿** ⇒ "
      "该门**不能验证 TM601 的 BST 修法**，须先经 `t6` 改契约。",
    "- **撤回我的假阳性**：曾担心修法造出「ACM200 与 FPVIe0 同时驱动 SW」的新电路——宏展开核对后不成立；"
      "`K48` 是同一物理线上的接口开关（通电→K76→BST，释放→默认投 K49→SW1），两目的地互斥。`TM640:7513` 即为同类既有形状。",
    "- **待 `t2` 判定**：TM640 闭集含 `K46` 而 TM600 既有闭集不含 ⇒ 「TM600 只补 K48/K76 是否足够」；"
      "以及 TM601 是否必须驱动 BST。",
    "",
]

with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + "\n".join(ledger).encode("utf-8"))

with open(STATUS, "rb") as f:
    sb = f.read()
with open(STATUS, "wb") as f:
    f.write(sb + "\n".join(status).encode("utf-8"))

man = json.load(open(PIN, encoding="utf-8"))
man["r11Tm601Sandbox"] = {
    "doc": {"path": DOC, "size": ds, "sha256": dh},
    "fixed": {"path": fixed and os.path.join(RUN, "sandbox", "test.cpp.tm601_bstleg"), "size": fixed[0], "sha256": fixed[1]},
    "result": {"path": res and os.path.join(RUN, "sandbox", "tm601-fix-test-result.json"), "size": res[0], "sha256": res[1]},
    "outcome": "TM601 BST-leg added -> gate still exit 1 because the frozen contract registers no BST leg for TM601; red cause is TM600 only",
}
for name, path in (("run_ledger", LEDGER), ("current_status", STATUS)):
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
print("fixed:", fixed)
print("ledger:", sig(LEDGER))
print("status:", sig(STATUS))
print("pin:", sig(PIN))
