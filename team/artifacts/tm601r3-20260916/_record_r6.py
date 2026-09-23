# -*- coding: utf-8 -*-
"""Round-6 recorder: BST supply resource notes -> ledger + pin."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(RUN, "bst-supply-resource-notes.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")

BT = chr(96)  # backtick


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


ds, dh = sig(DOC)

lines = [
    "",
    "",
    "## 2026-09-17 00:0x +0800 BST 供给资源事实 + TM601 通路缺失的代码级证据",
    "",
    "- 新增 " + BT + "bst-supply-resource-notes.md" + BT + " = %d B / " % ds + BT + dh + BT + "。",
    "- **FACT（TM601）**：部署态唯一 " + BT + "cbite.SetOn" + BT + " 在 " + BT + "test.cpp:9255" + BT
    + "，逐字为 " + BT + "K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, "
      "K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP" + BT
    + " ⇒ **不含 K48/K76/K46/K49/K109/K110**；而 " + BT + ":9269" + BT
    + " 却把 ch5 " + BT + "Set(FV,5,ACM200_10V,100MA,RELAY_ON)" + BT
    + " ⇒ **源设了 5 V 但没有闭合到 BST 的通路**，BST=5 V 到不了 BST 节点。" + BT + ":9246" + BT
    + " 既有注释亦写明 SW1 需 K46、SW2 需 K46+K49，与 SW 是不同节点。",
    "- **FACT（TM600 栅格）**：" + BT + ":9081" + BT
    + " 闭集 = K83(PMID) + K60/K61(SW) + K13/K85/K57/K126(cap)，**缺 K48/K76** ⇒ 与门禁实跑「缺失 [48,76]」一致。",
    "- **FACT（ch5 归属）**：驱动性 " + BT + ".Set" + BT + " 见 TM607(:7008)/TM608(:7096,7100)/TM609(:7179,7184)/"
      "TM640(:7521,7526)/TM600(:9097-9115)/TM601(:9269)；" + BT + "TM641/643" + BT + " 注释 "
    + BT + ":7598/:7621/:7714" + BT + " 逐字写「K48/K76 把 ch5 输出接 BST ⇒ 该源全程 RELAY_OFF 不驱动」，"
      "即**多源互斥与显式释放的既有先例**。",
    "- **FACT（ch18）**：" + BT + "PB0_BST_ACM" + BT + " 的实际用途是 **PWM1/PB0 引脚测量**（"
    + BT + ":5003/5022/5026/5041/5045" + BT + "、" + BT + ":5185-5199" + BT + " 含 " + BT + "MeasureVI(50,5)" + BT
    + "+" + BT + "MIRET" + BT + "；" + BT + ":4994/5160" + BT + " 注释 " + BT + "default NC" + BT
    + "）⇒ ch18 当 BST 供电源需另证（交 " + BT + "t2" + BT + "）。",
    "- **INFERENCE**：新版 TM600 的 5 V 工况形状由部署态 TM640 给出（" + BT + ":7521" + BT + " BST=5、SW=0 → "
    + BT + ":7524" + BT + " PMID=5 → " + BT + ":7526" + BT + " BST=10、BST-SW=5），且 " + BT + ":7513" + BT
    + " 同时闭 " + BT + "K48,K76" + BT + "；沿用 15 V 台阶在 5 V 工况下会得 BST-SW=15 V，与门禁自身规则 "
    + BT + "0<=BST-SW<=5V" + BT + "（" + BT + ":545" + BT + "）冲突 ⇒ 支持 A1。",
    "- **自我更正（第 5 次）**：我曾据被 " + BT + "Select-Object -First" + BT + " 截断的输出推测「部署态 TM600 不含 "
    + BT + "PMID_HG2_FXVI.Set" + BT + "」——**撤回**；普查为 59 处、" + BT + ".Set" + BT + " 51 处，"
      "TM600 体内确有（" + BT + ":9102/9107/9112" + BT + " 等）。",
    "- 未改任何文件；未落盘 payload；" + BT + "devel" + BT + " 零写入；目标树 " + BT + "15c7d2b8…" + BT
    + " 未变；非电性结论。",
    "",
]

with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + "\n".join(lines).encode("utf-8"))

ls, lh = sig(LEDGER)
man = json.load(open(PIN, encoding="utf-8"))
man["bstSupplyResourceNotes"] = {"path": DOC, "size": ds, "sha256": dh}
man["files"]["run_ledger"] = {"path": LEDGER, "size": ls, "sha256": lh}
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
print("ledger:", ls, lh)
print("pin:", sig(PIN))
