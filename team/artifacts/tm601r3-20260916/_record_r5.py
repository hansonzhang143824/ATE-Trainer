# -*- coding: utf-8 -*-
"""Record round-5 PMID operating-point evidence: ledger + CURRENT_STATUS + pin."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
DOC = os.path.join(RUN, "pmid-operating-point-evidence.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PLAN = os.path.join(WS, "team", "EXECUTION_PLAN.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


ds, dh = sig(DOC)

ledger = """

## 2026-09-16 23:5x +0800 A 项证据：已部署实现反证「15 V 台阶在 PMID=5 V 下成立」

- 新增 `pmid-operating-point-evidence.md` = __S__ B / `__H__`（证据源 = 部署态 `test.cpp` 469,714 B / `15c7d2b8…`，只读；函数体按 `DUT_API int <Name>(short funcindex` 定界，未用「最近前置 DUT_API」错法）。
- **FACT（TM600 L9057-9216）**：`:9086` 注释写 `PMID 15 V, VBAT 4.2 V`；`:9097-9115` 是 `SW12_U1REF_BST_ACM`（0→5→10→15→20 V）与 `PMID_HG2_FXVI`（0→5→10→15 V）**交替**的 BST−SW=5 V 台阶；`:9114` 终态 = PMID 15 V / BST 20 V。`:9081` 的 SetOn 只有 7 个继电器（无 K48/K76），与门禁实跑「缺失 [48,76]」一致。
- **FACT（TM640 L7503-7605）**：`:7492` 的 DFT 行 `vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5]` **与新版 TM600 DFT 逐字相同**；`:7521/:7526` 用 ACM200 10 V/100 MA 两步（`Set(FV,5)` 当 SW=0、`Set(FV,10)` 当 SW=5）实现 BST−SW=5 V；`:7513` 闭集含 `K48_ACM5_AMP_REF, K76_ACM_BST`。⇒ **本板既有「PMID=5 V + BST−SW=5 V」的已部署先例**。
- **FACT（TM601 L9217-9353）**：`:9269` `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON)` ⇒ **部署态 TM601 本来就在驱动 BST=5 V**。**更正旧 run 叙事**：「TM601 无 BST / 已移除 ACM 激励」与部署态代码不符；其 SetOn 只是未闭 K48/K76。
- **INFERENCE（裁 A 判定，强证据但未独立复核）**：A2（15 V）在算术上自我矛盾——把 15 V 台阶（PMID 5→10→15 与 BST 10→15→20）套到 PMID=5 V 的操作点会得到 **20 V BST** 且台阶注释自身要求 step4=PMID 15 V；A1（PMID=5 V + BST−SW=5 V）与 `TM640` 先例一致。⇒ 建议裁定：以新版 DFT 的 5 V 操作点为准，`voltage-inference.md` 的 15 V 台阶标注为**已部署的另一种工况**并保留；**不许拼用**。
- **证据强度声明**：TM640/TM600 的代码事实=强；「串台阶产生 20 V」=由注释推得（中，未实测）。
- **独立复核状态**：子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5` 仍在运行；其任务书只给了 A1 的原始理由，**未包含本条的代码级反证** ⇒ 结论标「强证据、未独立复核」，终判由 `t8` + 用户收口。
- 边界：只读；未改任何文件；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；非电性结论。
"""

status = """

## 2026-09-16 23:5x +0800 A 项（TM600 PMID）代码级证据 + TM601 叙事更正

- 新增 `team/artifacts/tm601r3-20260916/pmid-operating-point-evidence.md` = __S__ B / `__H__`。
- **部署态 TM600 是 15 V 台阶**：`test.cpp:9097-9115` 把 `BST`（0→5→10→15→20 V）与 `PMID`（0→5→10→15 V）**交替**递进以维持 BST−SW=5 V；`:9114` 终态 PMID 15 V / BST 20 V；`:9086` 注释自述 `PMID 15 V, VBAT 4.2 V`。⇒ `voltage-inference.md` 的 15 V 台阶 = **部署态那条台阶**。
- **部署态 TM640 是 5 V 工况先例**：`test.cpp:7492` 的 DFT 行 `vset[vbat,3.5] vset[pmid,5] vset[bst_sw,5] vset[vdrv,5]` **与新版 TM600 DFT 逐字相同**；`:7521/:7526` 用 ACM200 10 V/100 MA 两步实现 BST−SW=5 V；`:7513` 闭集含 `K48/K76`。
- **裁 A 建议（强证据、未独立复核）**：采用新版 DFT 的 `PMID=5 V` + `BST−SW=5 V`；把 15 V 台阶标注为已部署的另一种工况并保留；**禁止把两者拼用**（会产生 20 V BST 台阶且与台阶自身注释矛盾）。
- **TM601 叙事更正**：部署态 `test.cpp:9269` 就有 `SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, RELAY_ON)` ⇒ 旧 run「TM601 无 BST / 移除 ACM 激励」的表述与部署态代码不符（其 SetOn 仅未闭 K48/K76）。
"""

with open(LEDGER, "rb") as f:
    lb = f.read()
with open(LEDGER, "wb") as f:
    f.write(lb + ledger.replace("__S__", str(ds)).replace("__H__", dh).encode("utf-8"))

with open(STATUS, "rb") as f:
    sb = f.read()
with open(STATUS, "wb") as f:
    f.write(sb + status.replace("__S__", str(ds)).replace("__H__", dh).encode("utf-8"))

# keep the plan's appendix pointer accurate
with open(PLAN, "rb") as f:
    pb = f.read()
plan_add = ("""

### 补充（2026-09-16 23:5x）：A 项已有代码级证据

`pmid-operating-point-evidence.md`（team/artifacts/tm601r3-20260916/）= %d B / `%s`：部署态 TM600 是 **PMID 15 V 台阶**（`test.cpp:9097-9115`），而 **TM640 的 DFT 行与新版 TM600 DFT 逐字相同**且以 ACM200 10 V/100 MA 实现 PMID=5 V + BST−SW=5 V（`:7492/:7521/:7526`）。⇒ 建议采用 5 V 工况，15 V 台阶标为已部署的另一工况；**不得拼用**。
""" % (ds, dh)).encode("utf-8")
with open(PLAN, "wb") as f:
    f.write(pb + plan_add)

man = json.load(open(PIN, encoding="utf-8"))
man["pmidOperatingPointEvidence"] = {"path": DOC, "size": ds, "sha256": dh}
for name, path in (("run_ledger", LEDGER), ("current_status", STATUS), ("execution_plan", PLAN)):
    s, h = sig(path)
    man["files"][name] = {"path": path, "size": s, "sha256": h,
                          "note": "refreshed after this session's own appends" if name != "execution_plan" else "refreshed after append"}
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
