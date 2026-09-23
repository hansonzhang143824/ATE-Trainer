# -*- coding: utf-8 -*-
"""t35/t41: explicit 'K110 conclusion corrected' statements + sharpen (a') (K109 belongs to FPVIe[L]/QVM[L], not ch18); t34: same sharpening in the (a)(b)(c) block."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"

def show(fn, pat):
    p = os.path.join(A, fn)
    s = open(p, encoding="utf-8").read()
    for i, l in enumerate(s.splitlines(), 1):
        if re.search(pat, l):
            print("  %s:%d | %s" % (fn, i, l.strip()[:180]))

print("=== locate (a')/K109-ch18 statements ===")
show("t35-contract-reconciliation.md", r"K109/K110 属|属 ch18|ch18 路线")
show("t41-tm601-bst-path-determination.md", r"K109/K110 属|属 ch18|ch18 路线")
show("acceptance-report.json", r"K109/K110 belong|channel-18 route")

NEW_A = ("`K110` 属**通道 18 路线**（`K110_ACM18_BST` / `PB0_BST_ACM`）；**`K109` 属 FPVIe[L]/QVM[L] 低域路线**（其 pins 3/6 = `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`；IR 与 `SCH:538/539` 双源已证）；"
         "**两者都不属本案仪器 `SW12_U1REF_BST_ACM` 的通道 5 路线**。")

# --- t35: sharpen (a') wherever the old phrasing appears, and state the K110 conclusion correction explicitly ---
p35 = os.path.join(A, "t35-contract-reconciliation.md")
s = open(p35, encoding="utf-8").read()
b0 = open(p35, "rb").read()
reps = [
    ("`K109/K110` 属 ch18、本项不闭",
     "`K110` 属通道 18（`PB0_BST_ACM`）、`K109` 属 FPVIe[L]/QVM[L] 低域路线，**两者都不属本案仪器 ch5 路线、本项均不闭**"),
    ("`K109/K110` 属 ch18 路线，**不是本案仪器（ch5）的路线**",
     "`K110` 属通道 18 路线、`K109` 属 FPVIe[L]/QVM[L] 低域路线（" + NEW_A + "），**两者都不是本案仪器（ch5）的路线**"),
]
for old, new in reps:
    if old in s:
        s = s.replace(old, new, 1); print("t35 sharpened:", old[:40])
add35 = ("\n\n> **K110 结论更正声明（v1.23，复核方要求明写）**：**`t39` 与 `t35` 附录 D/E/F 的“到 BST 必须 `K110` 置位 / K110 必需且充分”结论予以更正** —— "
         "该结论**只对通道 18（`PB0_BST_ACM`）成立**；**本案仪器 `SW12_U1REF_BST_ACM` = 通道 5 ⇒ BST 腿 = `K48_ACM5_AMP_REF` + `K76_ACM_BST`（`required_on=[48,76]`）**。"
         "四方独立证据（驱动宏通道索引／派生表 `SCH:662+672-674`／IR `[48,76]`／在役生产代码 `:6997/:7085` 注释与 `:7000/7087/7170/7513` SetOn）**经复核方逐条独立复核通过**。"
         "**跨域闭集 = BST `[48,76]` + SW `[60,61]` = `[48,60,61,76]`**（**SW 侧须写全 `K60`+`K61`**：同族 `pmid2sw=[83,60,61]`、`sw2pgnd=[154,155,60,61]` 与部署四处均如此；`[48,61,76]` **不完整**）。")
anchor_x = "## 附录 L（Captain 授权的**定点更正**，v1.15）— ch5 口径定案；D/E/F 的\"K110 必需\"前提作废"
if anchor_x in s and "K110 结论更正声明（v1.23" not in s:
    s = s.replace(anchor_x, anchor_x + add35, 1); print("t35 K110-correction statement added")
open(p35, "w", encoding="utf-8").write(s)
b1 = open(p35, "rb").read()
print("t35:", len(b0), "->", len(b1), "|", hashlib.sha256(b1).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(p35).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# --- t41: same correction statement in appendix L2 ---
p41 = os.path.join(A, "t41-tm601-bst-path-determination.md")
s2 = open(p41, encoding="utf-8").read(); c0 = open(p41, "rb").read()
add41 = ("\n\n> **K110 结论更正声明（v1.9）**：**`t39` 的“到 BST 必须 `K110` 置位”予以更正** —— 只对**通道 18（`PB0_BST_ACM`）**成立；**本案仪器（通道 5）⇒ BST `[48,76]`**，"
          "跨域闭集 **`[48,60,61,76]`**（SW 侧写全 `K60`+`K61`）。**TM601 侧结论不变**：其 `SetOn` 中 `K48/K76` 与 `K109/K110` 四者皆无 ⇒ **两读法下都到不了 BST ⇒ 移除正确**。")
anchor41 = "## 附录 L2（Captain 授权的**定点更正**，v1.6）— ch5 定案对 §1/§H.2/附录 J 的结论更正"
if anchor41 in s2 and "K110 结论更正声明（v1.9" not in s2:
    s2 = s2.replace(anchor41, anchor41 + add41, 1); print("t41 correction statement added")
open(p41, "w", encoding="utf-8").write(s2)
c1 = open(p41, "rb").read()
print("t41:", len(c0), "->", len(c1), "|", hashlib.sha256(c1).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(p41).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# --- t34: sharpen the (a) clause inside L19 ---
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
hit = 0
for i, x in enumerate(d["limitations"]):
    if "K109/K110 belong to the channel-18 route" in x:
        d["limitations"][i] = x.replace(
            "K109/K110 belong to the channel-18 route",
            "K110 belongs to the channel-18 route (PB0_BST_ACM) while K109 belongs to the FPVIe[L]/QVM[L] low-domain routes (pins 3/6 = FPVIe1_FL/SL_BUS_S1; IR + SCH:538/539); neither belongs to THIS instrument's channel-5 route")
        hit += 1
print("t34 sharpened entries:", hit)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# --- anchors ---
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
for k, f in (("t35-contract-reconciliation.md", p35), ("t41-tm601-bst-path-determination.md", p41), ("acceptance-report.json", f34)):
    bb = open(f, "rb").read()
    doc["anchors"][k] = {"path": f.replace("\\", "/"), "sizeBytes": len(bb), "sha256": hashlib.sha256(bb).hexdigest(),
                         "measuredAt": datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B")
