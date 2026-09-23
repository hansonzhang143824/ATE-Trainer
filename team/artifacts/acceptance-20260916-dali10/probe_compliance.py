# probe_compliance.py — Captain 只读探针：本代如何表达 force 的 clamp/compliance（回答 t5 问题 #1）
# 运行：python team/artifacts/acceptance-20260916-dali10/probe_compliance.py
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
SRC = "D:/PROJECT6-DALI/ForCodexDebug/source"
test = open(f"{SRC}/test.cpp", encoding="utf-8-sig", errors="replace").read()
stdafx = open(f"{SRC}/StdAfx.h", encoding="utf-8-sig", errors="replace").read()
lines = test.splitlines()


def ctx(pattern, limit=6, width=170):
    print(f"\n--- /{pattern}/ (first {limit}) ---")
    rx = re.compile(pattern)
    n = 0
    for i, l in enumerate(lines, 1):
        if rx.search(l):
            print("  test.cpp:%d %s" % (i, l.strip()[:width]))
            n += 1
            if n >= limit:
                break
    if n == 0:
        print("  (no hits in test.cpp)")


# 1) 被误报为 0 的名字到底在哪
ctx(r"FOVIe_100MA", 5)
ctx(r"FOVIe_40V", 3)
ctx(r"VBAT_ACM", 5)

# 2) 本代 force 仪器调用形态
ctx(r"\.Set\s*\(", 8)
ctx(r"\.MeasureVI\s*\(", 6)
ctx(r"\.GetMeasResult\s*\(", 6)
ctx(r"SetMeas[IV]Trig", 4)

# 3) StdAfx.h 里 FPVI/FXVI/FOVIe 枚举定义（clamp/range 可能编码在枚举里）
print("\n--- StdAfx.h enumerator definitions mentioning PVI/FXVI/FOVIe ---")
shown = 0
for i, l in enumerate(stdafx.splitlines(), 1):
    if re.search(r"(FPVIe_|FXVIe_|FOVIe_|FPVI_|FXVI_)", l) and shown < 18:
        print("  StdAfx.h:%d %s" % (i, l.strip()[:150]))
        shown += 1
print("  (total enumerator-ish lines:",
      len([1 for l in stdafx.splitlines() if re.search(r"(FPVIe_|FXVIe_|FOVIe_)", l)]), ")")
