# -*- coding: utf-8 -*-
"""Round-7 recorder: verification prerequisites -> ledger + pin."""
import hashlib
import json
import os

RUN = os.path.dirname(os.path.abspath(__file__))
DOC = os.path.join(RUN, "verification-prerequisites.md")
LEDGER = os.path.join(RUN, "RUN-LEDGER.md")
PIN = os.path.join(RUN, "pin", "snapshot-manifest.json")
BT = chr(96)


def sig(p):
    with open(p, "rb") as f:
        b = f.read()
    return len(b), hashlib.sha256(b).hexdigest()


ds, dh = sig(DOC)
lines = [
    "",
    "",
    "## 2026-09-17 00:2x +0800 验证前置（复核拦截清单）",
    "",
    "- 新增 " + BT + "verification-prerequisites.md" + BT + " = %d B / " % ds + BT + dh + BT + "：把本轮确立的可执行判据、"
      "6 个必须由 owner 回答的拦截问题（Q1-Q6）、以及解锁后按序可跑的只读校验整理成清单。",
    "- 关键拦截项：**Q3** " + BT + "relays.md:99" + BT + "（K46~K59 归 MOS P2P）与 " + BT + ":96/:105-108" + BT
    + "（Share/BUS 归类）**存在张力**，决定「释放=开路」还是「释放=改道」；**Q6** 门禁对 TM600 的期望集 `[48,60,61,76,83]` "
      "是 pmid2sw+bst2sw 两支合并的结果，须由 " + BT + "t6/t8" + BT + " 确认是否含「契约提及但实现不该闭」的腿。",
    "- 新增独立对抗性复核子代理 " + BT + "e1aec5f2-6281-41ae-a132-0c3497358439" + BT
    + "（同模型路由），任务书**带上本轮全部代码级事实**并要求逐条 CONFIRMED/PARTLY/REFUTED + 找反证；"
      "产物拟落 " + BT + "review/independent-review-r7-findings.md" + BT + "。前一个复核 " + BT + "6fe11f3f-…" + BT + " 仍在跑。",
    "- 边界：只读；未改脚本/契约/计划/源码；未落盘 payload；" + BT + "devel" + BT + " 零写入；目标树 " + BT + "15c7d2b8…" + BT
    + " 未变；非电性结论。",
    "",
]

with open(LEDGER, "rb") as f:
    old = f.read()
with open(LEDGER, "wb") as f:
    f.write(old + "\n".join(lines).encode("utf-8"))

ls, lh = sig(LEDGER)
man = json.load(open(PIN, encoding="utf-8"))
man["verificationPrerequisites"] = {"path": DOC, "size": ds, "sha256": dh}
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
