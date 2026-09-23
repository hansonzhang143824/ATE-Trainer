# -*- coding: utf-8 -*-
"""One-spot banners in t35/t41: mark every '现盘 = 39,457 / 2d0984d9' statement as historical and give the live payload value."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LIVE = "43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24"

BANNER = ("\n> ## ⚠️ 现盘 payload 更正横幅（v1.25，事实性更正；单点插入、不改既有正文）\n"
          "> **现盘交付件 = " + LIVE + "（566 行）**，TM600 SetOn = `[13,48,57,60,61,76,83,85,126]`（**含 `K48/K76`、可执行 `K109/K110` = 0**）；**canonical 已由 Captain 定格为该字节、写入已停**。\n"
          "> 本文件内所有把 **`39,457 B / 2d0984d992d5d8cb…`**（或 `38,147/272667f3…`、`36,381/73b511b7…`、`35,014/444810dd…`）写作\"**现盘**\"的表述，**均指 2026-09-16 21:09:24 之前的时点、属历史**；"
          "同一路径在 20:45–21:09 被**就地覆盖四次**、**从未有副本**，故旧值全树 0 命中是**正确结果**。引用一律以**现算**为准。\n")

for fn, lines in (("t35-contract-reconciliation.md", "335/337/350/352/431"), ("t41-tm601-bst-path-determination.md", "78/103/125/129/180/260")):
    p = os.path.join(A, fn)
    s = open(p, encoding="utf-8").read()
    if "现盘 payload 更正横幅" in s:
        print(fn, "banner already present"); continue
    b0 = open(p, "rb").read()
    # insert right after the first markdown heading line
    out = []
    done = False
    for l in s.splitlines(True):
        out.append(l)
        if not done and l.startswith("# "):
            out.append(BANNER.replace("（单点插入、不改既有正文）",
                                      "（单点插入、不改既有正文；受影响行号：" + lines + "）"))
            done = True
    if not done:
        out.append(BANNER)
    open(p, "w", encoding="utf-8").write("".join(out))
    b1 = open(p, "rb").read()
    print("%s: %d -> %d B | %s @%s" % (fn, len(b0), len(b1), hashlib.sha256(b1).hexdigest(),
                                       datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
for k in ("t35-contract-reconciliation.md", "t41-tm601-bst-path-determination.md"):
    p = os.path.join(A, k); b = open(p, "rb").read()
    doc["anchors"][k] = {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                         "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors refreshed:", os.path.getsize(ap), "B")
