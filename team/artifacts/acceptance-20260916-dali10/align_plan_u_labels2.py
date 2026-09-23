# ⛔ OBSOLETE / DO NOT RUN (marked by the captain, 2026-09-16)
# CANONICAL MAPPING (user instruction): U10 = QVM channel-0 concurrency, U11 = FI SIGN-CONVENTION.
# This script asserts the OPPOSITE mapping (it was written against a superseded contract revision),
# so running it would push the plan away from canonical. Kept only for audit history.
#
# align_plan_u_labels2.py — 反相对齐：计划改回 U10 = QVM 并发性、U11 = SIGN-CONVENTION
#   依据：契约现盘（326,439 B）openItems = U10 QVM concurrency / U11 FI command-sign convention
# 运行：python team/artifacts/acceptance-20260916-dali10/align_plan_u_labels2.py
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
    ('"U11 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented;',
     '"U10 - QVM channel 0 concurrency with the floating channel forcing the same nodes is undocumented;'),
    ('"U10 - SIGN-CONVENTION: the floating channel 0 terminal assignment is fixed by the netlist',
     '"U11 - SIGN-CONVENTION: the floating channel 0 terminal assignment is fixed by the netlist'),
    ("U11 two-wire sense-meter channel concurrency", "U10 two-wire sense-meter channel concurrency"),
    ("U11 - QVM", "U10 - QVM"),
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
