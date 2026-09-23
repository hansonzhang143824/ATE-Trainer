# probe_review_items.py — 用户独立审查项的现场核验（不改任何被审产物）
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
W = "D:/Newtest/DSH/ATE-Coding-Plat/"
D = W + "team/artifacts/acceptance-20260916-dali10/"
PAYLOAD = D + "implementation-payload-TM600-TM601.cpp"

print("=== A. gate_baseline.json 读取形态 ===")
gb = open(W + "scripts/gate_baseline.json", "rb").read()
print("  bytes=%d  first6=%s  BOM=%s" % (len(gb), gb[:6].hex(), gb[:3] == b"\xef\xbb\xbf"))
print("  utf-8-sig decode ->", json.loads(gb.decode("utf-8-sig")))
try:
    json.loads(gb.decode("utf-8"))
    print("  plain utf-8 decode -> OK")
except Exception as e:
    print("  plain utf-8 decode -> FAILS: %s" % e)

print("\n=== B. run_gates.ps1 里 cbit 基线的读取/比较点 ===")
rg = open(W + "scripts/run_gates.ps1", encoding="utf-8-sig").read().splitlines()
for i, ln in enumerate(rg, 1):
    if re.search(r"baseline|cbit|KNOWN|ConvertFrom-Json|Get-Content|-Raw", ln, re.I):
        print("  %3d: %s" % (i, ln.strip()[:150]))

print("\n=== C. payload 中 126 / K126 / FXVIe 量程 相关行 ===")
pb = open(PAYLOAD, "rb").read().decode("utf-8-sig")
for i, ln in enumerate(pb.splitlines(), 1):
    if re.search(r"\b126\b|K126|FXVIe|PMID_HG2|cbite|SetOn", ln):
        print("  %3d: %s" % (i, ln.strip()[:170]))

print("\n=== D. 目标树 StdAfx.h 中的 K126 / V1P5 宏 ===")
for cand in ("D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h",
             "D:/PROJECT6-DALI/ForCodexDebug/StdAfx.h"):
    if os.path.exists(cand):
        t = open(cand, "rb").read().decode("utf-8-sig", errors="replace")
        print("  file:", cand, "(%d B)" % len(t.encode("utf-8")))
        for pat in (r"K126\w*", r"\w*V1P5\w*", r"#define\s+K126\w*.*"):
            hits = sorted(set(re.findall(pat, t)))
            print("    %-22s -> %s" % (pat, hits[:12]))
        break
else:
    print("  StdAfx.h not found at the two candidate paths")

print("\n=== E. 冻结契约/计划中的量程规则与 +-1 A 措辞（只读引用）===")
sc = open(D + "setup-contract.json", "rb").read().decode("utf-8")
for pat in (r"2x range", r"2 x range", r"range rule", r"FXVIe_PLUS_10V", r"FXVIe_PLUS_100V"):
    print("  contract %-20s hits=%d" % (pat, len(re.findall(pat, sc))))
