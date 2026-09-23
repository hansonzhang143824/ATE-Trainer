# align_plan_u_labels.py — [OBSOLETE / DO NOT RUN]
#   The canonical mapping it was written against has been REVERSED by the captain/user ruling:
#     canonical now = U10 = QVM channel-0 concurrency, U11 = SIGN-CONVENTION (FI command-sign, bring-up item).
#   This script swaps the labels the OTHER way, so running it would re-introduce the divergence it was
#   meant to fix. The plan (test-plan.json, revision v20+) already carries the canonical mapping.
#   Kept only as run history. Do not execute. (Marked obsolete per the captain's instruction.)
# 运行：python team/artifacts/acceptance-20260916-dali10/align_plan_u_labels.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "test-plan-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")
orig = t

reps = [
    # QVM 并发性：U10 -> U11
    ('"U10 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented;',
     '"U11 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented;'),
    # SIGN-CONVENTION：U11 -> U10
    ('"U11 - SIGN-CONVENTION: the floating channel 0 terminal assignment is fixed by the netlist',
     '"U10 - SIGN-CONVENTION: the floating channel 0 terminal assignment is fixed by the netlist'),
    # 条目内引用的 QVM 计数（若存在 "U10" 指 QVM 的其它文本）
    ("U10 two-wire sense-meter channel concurrency", "U11 two-wire sense-meter channel concurrency"),
    ("U10 - QVM", "U11 - QVM"),
]

for old, new in reps:
    n = t.count(old)
    if n:
        t = t.replace(old, new)
    print("replaced %d x  <- %s" % (n, old[:72]))

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("changed:", t != orig, "| bytes:", len(data))
