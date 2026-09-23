# -*- coding: utf-8 -*-
"""Record round-4 BST node source table: run ledger + CURRENT_STATUS + pin refresh."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
WS = r"D:\Newtest\DSH\ATE-Coding-Plat"
DOC = os.path.join(RUN, "bst-node-source-table.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
STATUS = os.path.join(WS, "team", "CURRENT_STATUS.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


dsize, dsha = sig(DOC)

ledger_entry = """

## 2026-09-16 23:4x +0800 BST 节点源表（物理事实）+ B 项降级修正

- 新增 `bst-node-source-table.md` = __D_SIZE__ B / `__D_SHA__`。来源 pin：`project/DALI/SCH-Connect-Map.txt` = 66,403 B / `cc8009fb…83cb427`（966 行）；`knowledge/hardware/relays.md` = 13,624 B / `8029ee13…1934fcdb`（246 行）。
- **BST 节点 8 条来路（逐行 locator）**：① ACM200 ch5 `K48,K76`（SCH:672-674）② FPVIe CH0-High `K46,K48,K76`（39-41）③ FPVIe CH0-Low `K109,K110,K138,K139,K145,K146`（42-44）④ S10_CH0_A `K141,K46,K48,K76`（461）⑤ QVM 高端 `K137,K46,K48,K76`（536）⑥ QVM 低端 `K109,K110,K139`（538）⑦ FPVIe CH1-High `K131,K132,K134,K135`（265-267）⑧ FPVIe CH1-Low `K109,K110`（268-270）。
- **多源互斥的具体形态**：ACM200 在 BST 上有两个可达通道 —— ch5 经 `K48/K76`、ch18 经 `K110` ⇒ 同一时刻只能选一路。连同「漏闭 K48 ⇒ 改道到 SW1/SW2 而非开路」（t47 结论），ch5 的三目的地天然互斥。
- **继电器语义（FACT, relays.md）**：`K46~K59` 列为 **MOS P2P，默认断开**（`relays.md:99`）；Share 继电器释放=通默认通道（`:96`）；BUS 释放=不通（`:95`）。⇒ **来路②④⑤要经 K46（默认断开=开路）**，来路①不经 K46（释放即改道）。**t48「显式 RELAY_OFF 配对非承重」的作用域应限定为来路①**。
- **B 项降级修正（对我上一轮措辞的实质更正）**：先前景象「BST=5 V」与「BST−SW=5 V」被我当作互相矛盾；实算后：LS 导通加 1 A 时 `V(SW)≈7.5 mV`，故 **BST=5 V（单端）⇒ BST−SW≈4.99 V**，两种读法在数值上几乎等价。⇒ 二者应视为**同一物理意图的两种说法**，真正待定的是「BST 由哪一路源驱动」与是否需要 `bst_sw` 差分行。工作簿 `AH133` 的 `SW-PGND=0.3`（无单位）**不足以定标**（与 7.5 mΩ 限值算术不自洽，子代理亦判其非限值列）。
- **待复核张力**：`relays.md:99` 把 K48/K49 列为 P2P(MOS)，但别处按 Share/BUS 使用（`:96/:95/:105-108`）⇒ 该归类由 `t2` 用端子图/网表定案，本汇编只按字面转述。
- 独立复核子代理 `6fe11f3f-…` 仍在跑 ⇒ 裁 A1 维持 **provisional**。
- 边界：未改脚本/契约/计划/源码；未落盘 payload；`devel` 零写入；目标树 469,714 B / `15c7d2b8…` 未变；非电性结论。
"""

status_entry = """

## 2026-09-16 23:4x +0800 BST 节点源表与 B 项降级修正（新增）

- 新增证据件 `team/artifacts/tm601r3-20260916/bst-node-source-table.md` = __D_SIZE__ B / `__D_SHA__`：BST 节点**8 条来路**逐行 locator（ACM200 ch5 `K48,K76`；FPVIe CH0-High `K46,K48,K76`；CH0-Low `K109,K110,K138,K139,K145,K146`；S10_CH0_A `K141,K46,K48,K76`；QVM 高/低端；FPVIe CH1-High `K131,K132,K134,K135`；CH1-Low `K109,K110`），以及 ACM200 **ch5/ch18 两路可达 ⇒ 多源互斥**、漏闭 K48 ⇒ **改道 SW1/SW2 而非开路**。
- **归类张力（待 t2 定案）**：`knowledge/hardware/relays.md:99` 把 `K46~K59` 列为 **MOS P2P 默认断开**，而 `K48/K49` 在别处按 Share/BUS 使用（`:95/:96/:105-108`）。
- **B 项修正**：TM601「BST=5 V」与「BST−SW=5 V」在 LS 导通（`V(SW)≈7.5 mV`）下数值几乎等价（≈4.99 V）⇒ 不再当作互相矛盾；真正待定 = 由哪一路源驱动 BST、是否需要 `bst_sw` 差分行。工作簿 `AH133` 的 `SW-PGND=0.3`（无单位）不足以定标。
- 裁 A1（TM600 PMID）仍 **provisional**（独立复核未回收）。
"""

with open(LEDGER, "rb") as f:
    lb = f.read()
with open(LEDGER, "wb") as f:
    f.write(lb + ledger_entry.replace("__D_SIZE__", str(dsize)).replace("__D_SHA__", dsha).encode("utf-8"))

with open(STATUS, "rb") as f:
    sb = f.read()
with open(STATUS, "wb") as f:
    f.write(sb + status_entry.replace("__D_SIZE__", str(dsize)).replace("__D_SHA__", dsha).encode("utf-8"))

man = json.load(open(PIN, encoding="utf-8"))
man["bstNodeSourceTable"] = {"path": DOC, "size": dsize, "sha256": dsha}
ls, lh = sig(LEDGER)
ss, sh = sig(STATUS)
man["files"]["run_ledger"] = {"path": LEDGER, "size": ls, "sha256": lh}
man["files"]["current_status"] = {"path": STATUS, "size": ss, "sha256": sh,
                                 "note": "refreshed after this session's own appends"}
for key in ("old_team_json", "setup_contract_old", "test_plan_old"):
    rec = man["files"].get(key) or {}
    p = rec.get("path")
    if p and os.path.exists(p):
        sz, h = sig(p)
        if h != rec.get("sha256"):
            rec.update({"size": sz, "sha256": h, "note": "live artifact of the OTHER run; refreshed after observed drift"})
            print("refreshed", key, sz, h[:12])
json.dump(man, open(PIN, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("doc:", dsize, dsha)
print("ledger:", ls, lh)
print("status:", ss, sh)
print("pin:", sig(PIN))
