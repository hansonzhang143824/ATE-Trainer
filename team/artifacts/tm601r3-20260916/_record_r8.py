# -*- coding: utf-8 -*-
"""Round-8 recorder: independent review recovery + retractions."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
REV = os.path.join(RUN, "review", "independent-review-pmid-ruling.md")
NOTE = os.path.join(RUN, "review", "captain-recovery-r8-independent-review.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")
BT = chr(96)


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


rs, rh = sig(REV)

note = """# Captain 回执：独立复核 `6fe11f3f-…` 的裁定与被迫撤回项（R8）

> 时间：2026-09-17 00:4x +0800。复核件：`review/independent-review-pmid-ruling.md` = {rs} B / `{rh}`（子代理 `6fe11f3f-94c7-43f6-bb9b-f020acc73fa5`，同模型路由 **deepseek-v4-flash**；**独立执行、未复用我的推理**）。
> 我已**抽查复核其关键引用**（见 §2），未逐行复核全篇 178 行。

## 1. 复核裁定：**DISAGREE with Ruling A1 as written**

要点：**方向（5 V）大概对，但我的论证是 non-sequitur、权威面不完整、字面执行是最危险的动作**。

## 2. 我已抽查确认的引用（我实测）

| 复核主张 | 我的核对 | 判定 |
| --- | --- | --- |
| 见证件显示**改动前** TM600 就已是 `vset[pmid,5,100e-6,0]` + `ExpectValue=11` | `dft-raw/overview-dft.json` 自记 xlsx `sha256=d9d721a3…`，其 TM600 行逐字含 `vset[pmid,5,100e-6,0]`、`ExpectValue: 11` | **确认** ⇒ 我此前「TM600 在新 DFT 下仍是 PMID=5 V」的说法虽结论对，但**「修改后 DFT」的框架具有误导性**：改动**只在 TM601 行新增 `vset[bst,5,…]`**（见证件 TM601 `Code1` 只有 3 行 vset） |
| 部署态 TM600 注释自述 **ACM200 到不了 BST** | `test.cpp:9027-9028` 逐字：`ACM200 reaches SW only and cannot reach BST, and FXVIe_PLUS reaches PMID/PGND only with its low side returning to AGND_F` | **确认**，且**与 `SCH-Connect-Map.txt:672-674`（`S5_ACM200_FH5 -> K48 -> K76 -> BST_F`）直接矛盾** ⇒ 这是**契约/门禁/已部署代码/实施者注释四方不一致** |
| clamp 语义是保护而非限值；0.5 V 对应 500 mΩ 上限 | `test.cpp:9011-9016` 逐字，含「the expected drop is ~11 mV / 7.5 mV at 1 A, three orders below the 0.5 V clamp」 | **确认** |

## 3. 被迫撤回/下调（对我的产出）

| 我此前写的 | 状态 | 更正 |
| --- | --- | --- |
| 「沿用 15 V 台阶在 PMID=5 V 工况下会得 **BST−SW=15 V**，支持 A1」 | **撤回** | 该论证**建立在一个未成立的假设上**：部署态 TM600 **从未闭合 K48/K76** ⇒ **20 V 台阶根本没被证明到达过 BST 节点**。因此「15 V 台阶在 5 V 工况下会怎样」不是已证事实；我也**不能**用 `TM640`（闭了 K48/K76 的兄弟）去断言 TM600 的「正确形状」，因为同文件的 `:9027-9028` 又声称 ACM200 到不了 BST —— 先例自相矛盾。 |
| 「`voltage-inference.md` 的 15 V 台阶 = 部署态那条台阶，只是另一种工况；建议采用 5 V 并标注」 | **降级为不充分** | 复核指出 `voltage-inference.md:142-143` 是**逐字转录 `DFT.csv`**，而 `DFT.csv`（`b92d203f…`，现盘未变）是**契约明确引用的权威输入**（`bst2sw`:92 / `pmid2sw`:97）⇒ **改标记文件并不能退役 15 V**。两者差异是**四个耦合字段**（PMID 5/15、VBAT 3.5/4.2、`iset[sw,…]` vs `iset[pmid2sw,…]`、限值 11/10 mΩ），**不能只挑 PMID 一个字段采纳**。 |
| 「TM601 的 `vset[bst,5,…]` 与 BST−SW=5 V 在数值上几乎等价（≈4.99 V）」 | **限定作用域** | 该算术**只在 TM601（SW≈0）**成立。对 TM600（SW 跟随 PMID 至 5 V），`BST−SW=5 V` **要求 BST 绝对值 = 10 V**——正是部署态 TM640 的做法（`:7521/:7526`，`:7566` 注释 `BST-SW: 5V→0V`）。**「BST=5 V」字面执行 ⇒ BST−SW=0**（FET 不导通、被 0.5 V clamp 挡住 ⇒ 100% 假失败）。 |

## 4. 复核新增的重要事实（我未逐一复核，标注来源）

- **工作簿自相矛盾（复核实测）**：`AH132` 的 `I=0.2A / pmid-sw=46mV` ⇒ **230 mΩ ≈ 21× 同行的 `E132=11 mΩ`**；`AH133` 的 `SW-PGND=0.3`（无单位）同样与 7.5 mΩ 不自洽。⇒ 该调试列**不能作为任何定标依据**（与我在 `bst-node-source-table.md` §4 的判断一致，但复核给了更强的量化）。
- **`test.cpp:9112` 是 `vset[pmid,15]` 的部署翻译**；全 VS 树 **0 处运行期 `vset()` 调用**，235 处全是注释（复核实测）⇒ 支持「`vset` = FV 强制」的机制判断。
- **ABS 表证据**：复核引 `docs/BST-SW通用知识介绍.txt` 与工作簿 ABS M29/M30/M44/M50 作为 BST−SW 上限（5–6 V 级）与 15 V 现状合规性的依据；我**未核对**这些表。
- **阻断性 UNKNOWN（复核列 U-A…U-F）**：`vset` 语义（工作区无 DFT 工具手册）、K48/K76 默认态、DUT `Rds,on` vs PMID（无 datasheet）、21:46 改动的完整范围、PMID 上 FV+FI 共存性（FXVIe 100 mA 档 vs FPVIe 1 A）、BST−SW 绝对上限。
- **能定案的动作（复核建议）**：BST 在 **K48/K76 未闭合** 下的**贯通性实测**；DFT 工具对 `vset` 与「floating source」的定义；DFT 作者对 `iset[sw]` vs `iset[pmid2sw]` 的意图；台架双操作点 `Rds,on` 对比。

## 5. 我据此给出的修正建议（不代替裁定）

1. **不要把本议题当作「PMID 5 V vs 15 V 二选一」**；它是一个**四字段耦合的工况对账**（PMID/VBAT/激励名/限值），必须整体裁定，且必须解释 `voltage-inference.md` 与 `DFT.csv` 的关系（前者转录后者）。
2. **更优先的问题是「BST 到底通不通」**：`test.cpp:9027-9028`（ACM200 到不了 BST）与 `SCH:672-674`（经 K48→K76 可达）**不能同时为真**。这一条决定：
   - 部署态 TM600 的 20 V 台阶**是否曾经真的到达 BST**（若没有，则既有「15 V 台阶 + BST=20 V」的整套推理都缺物理依据）；
   - 新 TM600/TM601 的 BST 供给应当选哪条来路。
   ⇒ 交 `t2`（物理判定）+ `t6`（契约）+ `t8`（独立审查），**并需用户裁定「以哪份证据为权威」**：实施者注释 / 端子图 / 契约。
3. **A1 方向仍可维持为工作假设，但不得再引用我的旧论证**；正式结论等第二个复核 `e1aec5f2-…`（已带全部代码级事实）回收后再定。

## 6. 边界

本回执只读（未改脚本/契约/计划/源码）；未落盘 payload；`devel` 零写入；目标树 `15c7d2b8…` 未变；**无硬件验证**（复核亦声明无法在本环境做台架/贯通性实测）。
""".format(rs=rs, rh=rh)

with open(NOTE, "w", encoding="utf-8") as f:
    f.write(note)
ns, nh = sig(NOTE)

ledger_lines = [
    "",
    "",
    "## 2026-09-17 00:4x +0800 独立复核回收（DISAGREE）+ 三项被迫撤回",
    "",
    "- 复核件 " + BT + "review/independent-review-pmid-ruling.md" + BT + " = %d B / " % rs + BT + rh + BT
    + "（子代理 " + BT + "6fe11f3f-…" + BT + "，deepseek-v4-flash 路由，独立执行）。Captain 回执 = "
    + BT + "review/captain-recovery-r8-independent-review.md" + BT + " = %d B / " % ns + BT + nh + BT + "。",
    "- **裁定：DISAGREE with Ruling A1 as written** —— 方向（5 V）大概对，但**论证是 non-sequitur**、"
      "权威面不完整、**字面执行最危险**。",
    "- **撤回 1**：「沿用 15 V 台阶会得 BST−SW=15 V ⇒ 支持 A1」。根因：部署态 TM600 " + BT + ":9081" + BT
    + " **从未闭 K48/K76** ⇒ 20 V 台阶**未被证明到达 BST**，故该论证前提不成立；且不能用 TM640 反推 TM600 形状，"
      "因为同文件 " + BT + ":9027-9028" + BT + " 又声称「ACM200 reaches SW only and cannot reach BST」，"
      "**与 " + BT + "SCH-Connect-Map.txt:672-674" + BT + " 直接矛盾**（四方不一致：契约/门禁/已部署代码/注释）。",
    "- **撤回 2（降级）**：「把 " + BT + "voltage-inference.md" + BT + " 的 15 V 台阶标为另一工况即可」不充分 —— "
      "复核实测该文档 " + BT + ":142-143" + BT + " 是**逐字转录 DFT.csv**，而 DFT.csv（" + BT + "b92d203f…" + BT
    + "，现盘未变）是**契约明确引用的权威输入**（bst2sw:92 / pmid2sw:97）⇒ 改标记退役不了 15 V；差异是**四个耦合字段**"
      "（PMID 5/15、VBAT 3.5/4.2、iset[sw] vs iset[pmid2sw]、限值 11/10 mΩ），不能只挑一个。",
    "- **撤回 3（限定作用域）**：「BST=5 V 与 BST−SW=5 V 数值等价」**只在 TM601（SW≈0）成立**；对 TM600（SW 跟随 PMID 到 5 V），"
      "BST−SW=5 V 要求 **BST 绝对值=10 V**（部署态 TM640 " + BT + ":7521/:7526/:7566" + BT + " 即此形状）；"
      "字面「BST=5 V」⇒ BST−SW=0 ⇒ FET 不导通 + 0.5 V clamp ⇒ **100% 假失败**。",
    "- **抽查确认的复核引用（我实测）**：见证件 " + BT + "overview-dft.json" + BT + "（自记 xlsx " + BT + "d9d721a3…" + BT
    + "）**改动前 TM600 已是 " + BT + "vset[pmid,5]" + BT + " + ExpectValue 11** ⇒ 21:46 那次改动的可见 delta "
      "**只在 TM601 行新增 " + BT + "vset[bst,5,…]" + BT + "**；" + BT + "test.cpp:9027-9028" + BT + " 与 "
    + BT + ":9011-9016" + BT + "（clamp=保护、0.5 V↔500 mΩ）逐字确认。",
    "- **复核新增（我未逐一复核）**：工作簿自相矛盾 —— " + BT + "AH132" + BT + " 的 " + BT + "I=0.2A/pmid-sw=46mV" + BT
    + " ⇒ 230 mΩ ≈ 21× 同行 " + BT + "E132=11 mΩ" + BT + "；全 VS 树 0 处运行期 " + BT + "vset()" + BT
    + " 调用（235 处皆注释）；BST−SW 上限引 ABS M29/M30/M44/M50 与 " + BT + "docs/BST-SW通用知识介绍.txt" + BT + "。",
    "- **阻断 UNKNOWN（U-A…U-F）**：" + BT + "vset" + BT + " 语义（无 DFT 工具手册）、K48/K76 默认态、DUT Rds,on vs PMID"
      "（无 datasheet）、21:46 改动完整范围、PMID 上 FV+FI 共存性、BST−SW 绝对上限。",
    "- **修正后的建议**：本议题**不是 PMID 二选一**，而是**四字段耦合工况对账**；**更优先的问题是「BST 到底通不通」**"
      "（" + BT + "test.cpp:9027-9028" + BT + " vs " + BT + "SCH:672-674" + BT + " 不能同时为真），"
      "它决定既有 20 V 台阶是否真到过 BST；A1 仅保留为**工作假设**，正式结论等第二个复核 " + BT + "e1aec5f2-…" + BT + " 回收。",
    "- 边界：只读；未落盘 payload；" + BT + "devel" + BT + " 零写入；目标树 " + BT + "15c7d2b8…" + BT + " 未变；无硬件验证。",
    "",
]

with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + "\n".join(ledger_lines).encode("utf-8"))

status_lines = [
    "",
    "",
    "## 2026-09-17 00:4x +0800 独立复核 DISAGREE + 三项撤回（覆盖本页 A 项口径）",
    "",
    "- 复核件 " + BT + "team/artifacts/tm601r3-20260916/review/independent-review-pmid-ruling.md" + BT + " = %d B / " % rs
    + BT + rh + BT + "；回执 " + BT + "review/captain-recovery-r8-independent-review.md" + BT + " = %d B / " % ns + BT + nh + BT + "。",
    "- **裁定：DISAGREE with Ruling A1 as written**（方向 5 V 大概对，但论证 non-sequitur、权威面不全、字面执行最危险）。",
    "- **撤回**：「15 V 台阶在 5 V 工况会得 BST−SW=15 V ⇒ 支持 A1」——前提不成立：部署态 TM600 " + BT + ":9081" + BT
    + " **从未闭 K48/K76**，20 V 台阶**未被证明到达 BST**。",
    "- **四方矛盾（决定性）**：" + BT + "test.cpp:9027-9028" + BT + " 声称「ACM200 reaches SW only and cannot reach BST」，"
      "而 " + BT + "SCH-Connect-Map.txt:672-674" + BT + " 是 `S5_ACM200_FH5 -> K48 -> K76 -> BST_F`，"
      "TM640 " + BT + ":7513" + BT + " 又确实闭了 K48/K76 ⇒ **契约/门禁/已部署代码/注释四方不一致**，须先由用户裁定哪份权威。",
    "- **修正后的建议**：议题应改为**四字段耦合工况对账**（PMID 5/15、VBAT 3.5/4.2、iset[sw] vs iset[pmid2sw]、11/10 mΩ），"
      "并优先回答「BST 是否可达」；A1 仅作**工作假设**，等第二个复核 " + BT + "e1aec5f2-…" + BT + " 回收后定。",
    "- 已知事实：" + BT + "voltage-inference.md:142-143" + BT + " 逐字转录 " + BT + "DFT.csv" + BT + "（契约引用的权威输入）；"
      "21:46 那次改动**只有 TM601 行新增 " + BT + "vset[bst,5,…]" + BT + "**（见证件 " + BT + "d9d721a3…" + BT + " 已在改动前含 " + BT + "vset[pmid,5]" + BT + "）。",
    "",
]

with open(STATUS, "rb") as f:
    sb = f.read()
with open(STATUS, "wb") as f:
    f.write(sb + "\n".join(status_lines).encode("utf-8"))

man = json.load(open(PIN, encoding="utf-8"))
man["independentReviewPmidRuling"] = {"path": REV, "size": rs, "sha256": rh,
                                      "verdict": "DISAGREE with Ruling A1 as written",
                                      "reviewer": "subagent 6fe11f3f (deepseek-v4-flash route)"}
man["captainRecoveryR8"] = {"path": NOTE, "size": ns, "sha256": nh}
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
print("review:", rs, rh)
print("note:", ns, nh)
print("ledger:", sig(LEDGER))
print("status:", sig(STATUS))
print("pin:", sig(PIN))
