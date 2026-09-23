# -*- coding: utf-8 -*-
"""Apply the reviewer-requested in-place two-family qualifiers in t35 and rewrite t34's L1 (live-hazard wording + two-cause split)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"

# ---------- t35 in-place qualifiers ----------
p = os.path.join(A, "t35-contract-reconciliation.md")
s = open(p, encoding="utf-8").read()
b0 = open(p, "rb").read()

head_old = "## 附录 F（IR 级复核，v1.6，**本附录取代附录 B.1 的那句定性**）— K110 必需且充分；K109 不属 ACM 基线路径"
head_new = head_old + "\n\n> **⚠️ 标题级更正（v1.21，Captain 授权的事实性更正）**：本标题的两句**只对 ch18 腿成立** —— **ch18（`S5_ACM200_FH18/SH18`）→ BST 需 `[110]`；ch5（`S5_ACM200_FH5/SH5`，本仪器 `SW12_U1REF_BST_ACM`）→ BST 需 `[48,76]`**；`K110` 属 `PB0_BST_ACM`（ch18）。本附录正文其余内容保留为历史；现行依据见 §L（ch5 收窄）与 §L.3。"

corr_old = "> **正确表述**：**K110 必需且充分**；**`K109` 不是 ACM 基线路径所需**。"
corr_new = "> **正确表述（v1.21 更正）**：**ch18（`FH18/SH18`）→ BST 需 `[110]`**；**ch5（`FH5/SH5`，本仪器）→ BST 需 `[48,76]`**；**`K109` 不出现在任何 `S5_ACM200_*→BST` 路径上**。原句\"K110 必需且充分\"的整体结论**只对 ch18 成立**；本仪器按 ch5 ⇒ `[48,76]`（见 §L）。"

l119_old = "⇒ ⚠️ **本节结论已被附录 F.2 取代（以此为准）**：**K110 必需且充分；`K109` 不是 ACM 基线路径所需**"
l119_new = l119_old + "\n> **⚠️ 追加 v1.21 限定**：该句的\"必需且充分\"**只对 ch18 腿成立**；**本仪器（`SW12_U1REF_BST_ACM`，ch5）→ BST 需 `[48,76]`**（见 §L / §L.3）。"

for label, old, new in (("F-heading", head_old, head_new), ("A-correct-statement", corr_old, corr_new), ("L119", l119_old, l119_new)):
    if old in s:
        s = s.replace(old, new, 1)
        print("t35 patched:", label)
    else:
        print("t35 ANCHOR MISSING:", label)

open(p, "w", encoding="utf-8").write(s)
b1 = open(p, "rb").read()
print("t35:", len(b0), "->", len(b1), "|", hashlib.sha256(b1).hexdigest(),
      "@", datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# ---------- t34 L1 rewrite ----------
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
newL1 = (
    "L1 (T32-F1 blocker, DEPLOYED state - LIVE HAZARD wording, per the reviewer's measurement and the captain's): the deployed TM600_HS_RDSON block (test.cpp:9057-9216) DOES drive the ACM200 channel-5 source "
    "(measured: SW12_U1REF_BST_ACM referenced 10 times and .Set called 10 times, with a voltage ladder containing non-zero steps up to 20 V), while that same block closes NONE of K48 / K76 / K49 / K109 / K110 (all measured 0). "
    "Consequence, per the re-routing mechanism (SCH-Connect-Map.txt:774/775): the excitation is steered to SW1_F / SW2_F and never reaches BST - this is a LIVE HAZARD (a source driven into a rail outside the item's scope, "
    "with SW1 not among TM600.scopePins), NOT a benign 'BST is missing one closure'. The bst-sw gate should therefore be red (t30's positive control is exactly this). It does not contradict t29's verdict=pass: t29 judged the "
    "workspace payload; not landing is a process state. CORRECTED per the captain: it must NOT be phrased as 'the deployed tree lacks K109/K110' - K109/K110 belong to the channel-18 route and are not this instrument's required closure. "
    "Corrected authoritative closure: BST side [48,76] (ACM200 family) + SW side [60,61] (FPVIe[L] family) = [48,60,61,76]. "
    "TWO-CAUSE SPLIT (never to be merged in the books): (i) the real cause of the deployed red = the missing K48/K76 closure, which re-routes the source to SW1/SW2 (live hazard above); (ii) a second and different cause used to be that "
    "aliasResolution[bst2sw].closedRelayNumbers had not been re-pointed, which demanded 110 and produced a FALSE red - that cause was REMOVED when the field was switched to the channel-5 route (contract rev 33+; the gate now computes "
    "[48,60,61,76,83]). Only cause (i) remains, and the deployed tree still fails the gate solely because nothing has been landed."
)
d["limitations"] = [newL1 if x.startswith("L1 (") else x for x in d["limitations"]]
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(),
      "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# ---------- refresh my own anchors file ----------
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

def rec(fp):
    bb = open(fp, "rb").read()
    return {"path": fp.replace("\\", "/"), "sizeBytes": len(bb), "sha256": hashlib.sha256(bb).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(fp).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

for k, f in (("t35-contract-reconciliation.md", p), ("acceptance-report.json", f34)):
    doc["anchors"][k] = rec(f)
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())
