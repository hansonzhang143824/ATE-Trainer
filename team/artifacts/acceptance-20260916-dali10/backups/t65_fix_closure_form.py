# -*- coding: utf-8 -*-
"""Second pass: eliminate the incomplete [48,61,76] closure form (missing SW-side K60) from my documents, and record the sharpened K109/K110 attribution split."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
SHARP = ("`K110` belongs to the channel-18 route (PB0_BST_ACM / K110_ACM18_BST); `K109` belongs to the FPVIe[L]/QVM[L] low-domain routes (its pins 3/6 are FPVIe1_FL_BUS_S1 / FPVIe1_SL_BUS_S1; "
         "evidenced by IR and SCH-Connect-Map 538/539). NEITHER belongs to this instrument's channel-5 route. Cross-domain closure = BST [48,76] + SW [60,61] = [48,60,61,76] (the SW side must be written in full - "
         "K60_BUSL0_VCP AND K61_ACM8_SW - as the sibling aliases pmid2sw=[83,60,61] and sw2pgnd=[154,155,60,61] and the four deployed items do; the form [48,61,76] is INCOMPLETE).")

# --- files where the incomplete closure form must not survive ---
for fn in ("t35-contract-reconciliation.md", "t41-tm601-bst-path-determination.md"):
    p = os.path.join(A, fn)
    s = open(p, encoding="utf-8").read(); b0 = open(p, "rb").read()
    n = s.count("[48,61,76]")
    if n:
        s = s.replace("[48,61,76]", "[48,60,61,76]")
        # annotate each such line once
        s = s.replace("⇒ **BST–SW 闭集 = `[48,60,61,76]`**；**`K110` 属 ch18（`PB0_BST_ACM`），与本仪器无关**。",
                      "⇒ **BST–SW 闭集 = `[48,60,61,76]`**（v1.24 更正：此前写作 `[48,61,76]` **漏了 SW 侧 `K60`**）；**`K110` 属通道 18（`PB0_BST_ACM`）**、**`K109` 属 FPVIe[L]/QVM[L] 低域路线**（二者皆非本仪器 ch5 路线）。")
    open(p, "w", encoding="utf-8").write(s)
    b1 = open(p, "rb").read()
    print("%s: replaced %d occurrence(s) of [48,61,76] -> %d B / %s @%s" % (fn, n, len(b1), hashlib.sha256(b1).hexdigest(), datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%H:%M:%S")))

# --- t34: record the sharpened attribution split + the incomplete-form correction ---
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
L36 = ("L36 (attribution split sharpened per the reviewer, and an incomplete closure form removed): " + SHARP +
       " Practical consequence: any statement of the form 'K109/K110 are both channel-18' is imprecise - only K110 is; K109 is a FPVIe[L]/QVM[L] low-domain selector, and 'closing K109' therefore couples the FPVIe1 low-domain bus "
       "to this node (the coupling noted in L7/L30). Also corrected: earlier text of mine wrote the closure as [48,61,76]; the authoritative form is [48,60,61,76].")
if L36 not in d["limitations"]:
    d["limitations"].append(L36)
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%H:%M:%S"), "| limitations:", len(d["limitations"]))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
for k, f in (("t35-contract-reconciliation.md", os.path.join(A, "t35-contract-reconciliation.md")),
             ("t41-tm601-bst-path-determination.md", os.path.join(A, "t41-tm601-bst-path-determination.md")),
             ("acceptance-report.json", f34)):
    bb = open(f, "rb").read()
    doc["anchors"][k] = {"path": f.replace("\\", "/"), "sizeBytes": len(bb), "sha256": hashlib.sha256(bb).hexdigest(),
                         "measuredAt": datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B")
