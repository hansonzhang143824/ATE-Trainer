# t23_verify_delta.py — 正确口径复验：区块字节保真 + delta 计数（live - baseline == payload 自身）
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
TARGET = "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
PAYLOAD = D + "implementation-payload-TM600-TM601.cpp"
BAK = D + "backups/test.cpp.before_TM600_TM601.bak"


def code_of(b):
    t = b.decode("utf-8-sig")
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in t.split("\n"))


TOK = {
    "delay_ms(1)": r"delay_ms\(1\)",
    "delay_ms(2)": r"delay_ms\(2\)",
    "SetClamp(50,50)": r"SetClamp\(\s*50\s*,\s*50\s*\)",
    "MeasureVI(200,5": r"MeasureVI\(200\s*,\s*5",
    "rampi_capv": r"rampi_capv",
    "rampv_capv": r"rampv_capv",
    "bare126": r"(?<![\w.])126(?![\w.])",
    "K126_V1P5_CAP": r"K126_V1P5_CAP",
    "ERROR_RES": r"ERROR_RES",
    "K5_VBUS_Cap": r"K5_VBUS_Cap",
    "K44_Cap_SW2_BST2": r"K44_Cap_SW2_BST2",
    "K45_Cap_SW1_BST1": r"K45_Cap_SW1_BST1",
    "K57_CAP_BST_SW": r"K57_CAP_BST_SW",
    "FPVIe_10A": r"FPVIe_10A\b",
}

live = open(TARGET, "rb").read()
base = open(BAK, "rb").read()
praw = open(PAYLOAD, "rb").read()

body = praw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
body_b = body.encode("utf-8")

print("live   = %d B / %s" % (len(live), hashlib.sha256(live).hexdigest()))
print("base   = %d B / %s" % (len(base), hashlib.sha256(base).hexdigest()))
print("payload= %d B / %s" % (len(praw), hashlib.sha256(praw).hexdigest()))

checks = []
# 1) 区块字节保真：live 必须以归一化 payload 结尾（区块位于 EOF）
ends = live.endswith(body_b) or live[3:].endswith(body_b)
checks.append(("payload block appended verbatim at EOF", ends, "endswith(normalised payload)=%s" % ends))
# 2) BOM 与行尾结构：与 baseline 相比孤立 LF 数不变
lb, ll = base.count(b"\n") - base.count(b"\r\n"), live.count(b"\n") - live.count(b"\r\n")
checks.append(("lone-LF structure unchanged vs baseline", lb == ll, "%d -> %d" % (lb, ll)))
checks.append(("BOM preserved", live[:3] == b"\xef\xbb\xbf", str(live[:3] == b"\xef\xbb\xbf")))
# 3) 两个 DUT_API 定义各一次；且 block 内代码级不变量 == payload 自身
rt = live.decode("utf-8-sig")
for nm, pat in (("TM600_HS_RDSON", r"DUT_API\s+int\s+TM600_HS_RDSON\s*\(\s*short\s+funcindex"),
                ("TM601_LS_RDSON", r"DUT_API\s+int\s+TM601_LS_RDSON\s*\(\s*short\s+funcindex")):
    n = len(re.findall(pat, rt))
    checks.append(("definition count %s == 1" % nm, n == 1, str(n)))

lc, bc, pc = code_of(live), code_of(base), code_of(body_b)
print("\n%-20s %8s %8s %8s %8s" % ("token", "baseline", "live", "delta", "payload"))
mismatch = []
for k, pat in TOK.items():
    a, b, c = len(re.findall(pat, bc)), len(re.findall(pat, lc)), len(re.findall(pat, pc))
    ok = (b - a) == c
    if not ok:
        mismatch.append(k)
    print("%-20s %8d %8d %8d %8d  %s" % (k, a, b, b - a, c, "OK" if ok else "MISMATCH"))

checks.append(("delta(live-baseline) == payload, all tokens", not mismatch, "mismatch=%s" % (mismatch or "NONE")))
checks.append(("bare 126 fixed (payload code has 0)", len(re.findall(TOK["bare126"], pc)) == 0, str(len(re.findall(TOK["bare126"], pc)))))
checks.append(("K5/K44/K45 absent from the new block", all(len(re.findall(TOK[t], pc)) == 0 for t in ("K5_VBUS_Cap", "K44_Cap_SW2_BST2", "K45_Cap_SW1_BST1")), "checked"))
checks.append(("K57 present in the new block", len(re.findall(TOK["K57_CAP_BST_SW"], pc)) == 2, str(len(re.findall(TOK["K57_CAP_BST_SW"], pc)))))
checks.append(("ERROR_RES present in the new block", len(re.findall(TOK["ERROR_RES"], pc)) == 2, str(len(re.findall(TOK["ERROR_RES"], pc)))))

print("\n=== checks ===")
bad = []
for nm, ok, ev in checks:
    print("  [%s] %-46s %s" % ("PASS" if ok else "FAIL", nm, ev))
    if not ok:
        bad.append(nm)
verdict = not bad
print("\nVERDICT: %s" % ("PASS" if verdict else "FAIL"))
out = {"live": {"bytes": len(live), "sha256": hashlib.sha256(live).hexdigest()},
       "baseline": {"bytes": len(base), "sha256": hashlib.sha256(base).hexdigest()},
       "payload": {"bytes": len(praw), "sha256": hashlib.sha256(praw).hexdigest()},
       "checks": [{"name": n, "pass": o, "ev": e} for n, o, e in checks], "mismatch": mismatch, "verdict": verdict}
json.dump(out, open(D + "t23-apply-verification.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("wrote t23-apply-verification.json")
raise SystemExit(0 if verdict else 1)
