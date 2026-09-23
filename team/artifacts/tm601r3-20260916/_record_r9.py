# -*- coding: utf-8 -*-
"""Round-9 recorder: BST path resolution -> ledger + status + plan + pin."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
DOC = os.path.join(RUN, "bst-path-resolution-r9.md")
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

ledger = [
    "",
    "",
    "## 2026-09-17 01:0x +0800 四方矛盾消解（R9）：ch5 可达 BST 有四份行为证据",
    "",
    "- 新增 " + B + "bst-path-resolution-r9.md" + B + " = %d B / " % ds + B + dh + B + "。",
    "- **事实 A（我实测，逐函数定界）**：闭 K48/K76 **且**驱动 ch5（" + B + "Set(FV,>0)" + B + "）的函数 = "
    + B + "TM607(6985-7072) / TM608(7073-7159) / TM609(7160-7249) / TM640(7503-7605)" + B
    + "，四个**全部 True**；而 " + B + "TM600(9057-9216)" + B + " 与 " + B + "TM601(9217-9353)" + B
    + " 驱动 ch5 却**都不闭 K48/K76**。⇒ 「本板 ACM200 到不了 BST」**不成立**；TM600/TM601 是**漏闭**。",
    "- **事实 B（消解）**：" + B + "test.cpp:9024-9033" + B + " 那段「ACM200 reaches SW only and cannot reach BST」"
      "**上下文是「黄金案例用两个独立地参考源 BTST_ACM + SW_ACM 拼 BST−SW」的那套安排**，作者在论证「它无法构成一对」；"
      "该句是该安排下的陈述，**不是本板硬件限制**。⇒ 我 R8 回执里称「注释与端子图直接矛盾」**属越出上下文的引用，现更正**："
      "两者不矛盾，是那段注释的局部论证被字面扩张。",
    "- **事实 C（对 R8「四字段耦合」的更正）**：" + B + "test.cpp:9035-9037" + B + " 逐字写明 "
      + B + "「the archived revision pairs 11 / 7.5 mohm with pmid 5 V, while DFT.csv pairs 10 / 8 mohm with pmid 15 / 9 V」"
    + B + " ⇒ 部署态实现者已认定 **11/7.5 mΩ 与 PMID=5 V 是同一套来源**、DFT.csv 的 10/8 与 15/9 V 是另一套。"
      "⇒ A 项不是「四个零散冲突字段」，而是**选哪一套来源**；工作簿那套（5 V + 11/7.5）自洽，且与门禁期望集（pmid2sw+bst2sw 并集）取向一致。",
    "- **可执行结论**：① TM600 在 " + B + ":9081" + B + " 那一次 SetOn 内补 " + B + "K48_ACM5_AMP_REF + K76_ACM_BST" + B
    + "（= TM640:7513 形状，正好补齐门禁 missing=[48,76]）；② TM601 要给 BST 腿登记 K48/K76，否则 " + B + ":9269" + B
    + " 的 5 V 永远到不了 BST；③ TM600 需 " + B + "BST_abs=10 V" + B + " 才有 BST−SW=5 V（SW 跟随到 5 V），TM601 单值 5 V 即 BST−SW≈4.99 V；"
      "④ 多源互斥须显式释放（TM641/643 先例 " + B + ":7598/:7621/:7714" + B + "）。",
    "- **仍未证实**：K48/K76 的实际物理贯通（需台架/端子测量）、" + B + "vset" + B + " 权威语义、PMID 上 FV+FI 共存性、"
      "部署态 20 V 台阶是否真的到过 BST（未闭腿 ⇒ 大概率未到达，但属 INFERENCE）；第二个复核 " + B + "e1aec5f2-…" + B + " 尚未回收。",
    "- 边界：只读；未改脚本/契约/计划/源码；未落盘 payload；" + B + "devel" + B + " 零写入；目标树 " + B + "15c7d2b8…" + B + " 未变；无机台验证。",
    "",
]

status = [
    "",
    "",
    "## 2026-09-17 01:0x +0800 ch5→BST 四方矛盾消解（R9）",
    "",
    "- 新增 " + B + "team/artifacts/tm601r3-20260916/bst-path-resolution-r9.md" + B + " = %d B / " % ds + B + dh + B + "。",
    "- **普查（我实测）**：闭 K48/K76 且驱动 ch5 的函数 = TM607/TM608/TM609/TM640（**4/4 全 True**）；"
      "TM600 与 TM601 驱动 ch5 却**都不闭 K48/K76** ⇒ 「本板 ACM200 到不了 BST」不成立，TM600/TM601 属**漏闭**。",
    "- **更正 R8**：" + B + "test.cpp:9024-9033" + B + " 的「ACM200 reaches SW only and cannot reach BST」是其"
      "**黄金案例双地参考源安排**的局部论证，**不是硬件限制**，与 " + B + "SCH:672-674" + B + " 并不矛盾；"
      "我 R8 回执的「注释与端子图矛盾」说法**撤回**。",
    "- **更正 R8 之二**：" + B + "test.cpp:9035-9037" + B + " 部署态已写明「11/7.5 mΩ 配 pmid 5 V；DFT.csv 的 10/8 配 15/9 V」"
      "⇒ A 项不是四个零散字段冲突，而是**两套来源二选一**；工作簿那套自洽且与门禁取向一致。",
    "- **修法**：TM600 补 " + B + "K48+K76" + B + "（同一次 SetOn）；TM601 补 BST 腿登记（否则其 ch5 5 V 到不了 BST）；"
      "TM600 需 " + B + "BST_abs=10 V" + B + " 才有 BST−SW=5 V。",
    "- 未证实：K48/K76 物理贯通、vset 语义、PMID 上 FV+FI 共存、部署态台阶是否真到过 BST；第二个复核未回收。",
    "",
]

plan_add = ("""

## 2026-09-17 01:0x +0800 执行口径更新（R9，**本节覆盖本文中更早的门禁/PMID 口径**）

`team/artifacts/tm601r3-20260916/bst-path-resolution-r9.md` = %d B / `%s`：

1. **四方矛盾已消解**：`test.cpp:9024-9033` 的「ACM200 到不了 BST」是其**黄金案例双地参考源安排**的局部论证，非硬件限制；本板实测 **TM607/608/609/640 四个函数全部「闭 K48/K76 且驱动 ch5」** ⇒ ch5→BST 可达。
2. **TM600 修法**：`:9081` 同一次 `SetOn` 内补 `K48_ACM5_AMP_REF`+`K76_ACM_BST`（= TM640 `:7513` 形状；正好补齐门禁 `missing=[48,76]`）。
3. **TM601 修法**：`:9255` 的 SetOn 无 BST 腿 ⇒ 必须给 TM601 登记 `K48/K76`，否则 `:9269` 的 `Set(FV,5)` 到不了 BST。
4. **操作点**：部署态 `:9035-9037` 自述「11/7.5 mΩ 配 pmid 5 V；DFT.csv 的 10/8 配 15/9 V」⇒ 采纳工作簿那套时，TM600 需 `BST_abs=10 V`（SW 跟随到 5 V）；TM601（SW≈0）单值 5 V ⇒ BST−SW≈4.99 V。
5. **仍未证实**：K48/K76 物理贯通、`vset` 权威语义、PMID 上 FV+FI 共存、部署态 20 V 台阶是否真到过 BST；`t8` 独立审查与第二个复核 `e1aec5f2-…` 未回收。
""" % (ds, dh)).encode("utf-8")

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
man["bstPathResolutionR9"] = {"path": DOC, "size": ds, "sha256": dh}
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
print("ledger:", sig(LEDGER))
print("status:", sig(STATUS))
print("plan:", sig(PLAN))
print("pin:", sig(PIN))
