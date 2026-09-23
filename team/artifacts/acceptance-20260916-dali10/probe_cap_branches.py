# probe_cap_branches.py — 逐条核查四条电容支路（SCH-Connect-Map）+ 当前 payload 的 K 列表/注释
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
W = "D:/Newtest/DSH/ATE-Coding-Plat/"
D = W + "team/artifacts/acceptance-20260916-dali10/"

cfg = json.loads(open(W + "project_config.json", encoding="utf-8-sig").read())
inter = cfg.get("intermediates", {})
print("=== intermediates ===")
for k, v in inter.items():
    print("  %-24s %s" % (k, v))
map_path = inter.get("sch_connect_map")
print("\nsch_connect_map =", map_path, "exists=", os.path.exists(map_path) if map_path else None)

KEYS = ["K44", "K45", "K57", "K5_", "K154", "K155", "K83", "K60", "K61", "VBUS", "BUSH0_AMUX", "PGND", "BST"]
if map_path and os.path.exists(map_path):
    raw = open(map_path, "rb").read()
    txt = raw.decode("utf-8-sig", errors="replace")
    print("map bytes=%d lines=%d" % (len(raw), len(txt.splitlines())))
    lines = txt.splitlines()
    for key in KEYS:
        hits = [(i, l.strip()) for i, l in enumerate(lines, 1) if key in l]
        print("\n--- %s : %d 行 ---" % (key, len(hits)))
        for i, l in hits[:6]:
            print("  L%-5d %s" % (i, l[:190]))

print("\n=== 当前 payload 的 SetOn 列表与电容相关注释 ===")
pb = open(D + "implementation-payload-TM600-TM601.cpp", "rb").read().decode("utf-8-sig")
for i, ln in enumerate(pb.splitlines(), 1):
    if re.search(r"SetOn\(|K44|K45|K57|K5_VBUS|inert|stabilis|stabiliz|protection", ln):
        print("  L%-4d %s" % (i, ln.strip()[:185]))
