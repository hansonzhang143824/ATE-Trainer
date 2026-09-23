# fix_u_semantics.py — 语义化修正：SIGN-CONVENTION 的引用统一为 U11（QVM 并发性为 U10）
# 只改明确指向 SIGN-CONVENTION 却被标为 U10 的 3 处字符串；不做全局 token 替换。
# 运行：python team/artifacts/acceptance-20260916-dali10/fix_u_semantics.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "setup-contract-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")
orig = t

reps = [
    ("register as U10 bring-up verification with the three criteria below.",
     "register as U11 bring-up verification with the three criteria below."),
    ("so it is the U10 bring-up check, not an established fact.",
     "so it is the U11 bring-up check, not an established fact."),
    ("the bring-up check is U10.",
     "the bring-up check is U11."),
]

for old, new in reps:
    n = t.count(old)
    if n != 1:
        print("WARN expected 1 match, got %d for: %s" % (n, old[:70]))
    t = t.replace(old, new)
    print("replaced %d x  <- %s" % (n, old[:70]))

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("changed:", t != orig, "| bytes:", len(data))
