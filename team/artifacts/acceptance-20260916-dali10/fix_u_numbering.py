# ⛔ OBSOLETE / DO NOT RUN (marked by the captain, 2026-09-16)
# The authority cited in the original header below (a frozen test-plan v12) is SUPERSEDED.
# CANONICAL MAPPING (user instruction): U10 = QVM channel-0 concurrency, U11 = FI SIGN-CONVENTION.
# Running this script would push artifacts AWAY from the canonical mapping. Kept only for audit history.
#
# fix_u_numbering.py — 把契约生成器里的 U10/U11 编号对调回来
# 口径依据：test-plan.json（已冻结 v12）用 U10 = QVM ch0 并发性、U11 = SIGN-CONVENTION。
# 运行：python team/artifacts/acceptance-20260916-dali10/fix_u_numbering.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "setup-contract-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")

if "U10" not in t and "U11" not in t:
    print("no U-numbering tokens found; nothing to do")
    raise SystemExit(0)

a, b = t.count("U10"), t.count("U11")
tmp = "@@U10TMP@@"
t = t.replace("U10", tmp).replace("U11", "U10").replace(tmp, "U11")

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)

print("swapped U10(%d) <-> U11(%d) in setup-contract-build.py" % (a, b))
print("now: U10=%d U11=%d" % (t.count("U10"), t.count("U11")))
print("bytes:", len(data), "| BOM:", bom)
