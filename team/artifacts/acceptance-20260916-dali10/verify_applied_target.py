# verify_applied_target.py — 精确校验落盘结果（追加区块逐字节重建 + 定义计数 + 行尾结构）
import hashlib
import json
import os
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
TARGET = "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
BAK = D + "backups/test.cpp.before_TM600_TM601.bak"
PAYLOAD = D + "implementation-payload-TM600-TM601.cpp"


def stat(b):
    return {"bytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "loneLF": b.count(b"\n") - b.count(b"\r\n"),
            "crlf": b.count(b"\r\n"), "bom": b[:3] == b"\xef\xbb\xbf"}


before = open(BAK, "rb").read()
after = open(TARGET, "rb").read()
praw = open(PAYLOAD, "rb").read()

sb, sa = stat(before), stat(after)
print("BASELINE (from backup) : %d B / loneLF=%d / crlf=%d / BOM=%s" % (sb["bytes"], sb["loneLF"], sb["crlf"], sb["bom"]))
print("AFTER    (live target) : %d B / loneLF=%d / crlf=%d / BOM=%s" % (sa["bytes"], sa["loneLF"], sa["crlf"], sa["bom"]))
print("sha256 after = %s" % sa["sha256"])

# 1) 原有部分的行尾结构必须不变
v1 = (sa["loneLF"] == sb["loneLF"])
print("\n[%s] baseline lone-LF count preserved (%d -> %d)" % ("PASS" if v1 else "FAIL", sb["loneLF"], sa["loneLF"]))

# 2) 追加区块必须与"归一后的 payload"逐字节相同
body = praw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
btext = before.decode("utf-8-sig")
if not btext.endswith("\n"):
    btext += "\r\n"
expected = btext.encode("utf-8")
if not expected.startswith(b"\xef\xbb\xbf"):
    expected = b"\xef\xbb\xbf" + expected
expected += body.encode("utf-8")
v2 = (expected == after)
print("[%s] live target == baseline + normalised payload, byte-for-byte" % ("PASS" if v2 else "FAIL"))
if not v2:
    print("      expected %d B / %s" % (len(expected), hashlib.sha256(expected).hexdigest()[:32]))

# 3) 追加区块自身的行尾纯净度
vb = body.encode("utf-8")
v3 = (vb.count(b"\n") - vb.count(b"\r\n")) == 0
print("[%s] appended block has 0 lone LF (block loneLF=%d)" % ("PASS" if v3 else "FAIL", vb.count(b"\n") - vb.count(b"\r\n")))

# 4) 两个 DUT_API 定义各恰好一次（按定义式匹配，排除注释提及）
rt = after.decode("utf-8-sig")
defs = re.findall(r"DUT_API\s+int\s+(TM600_HS_RDSON|TM601_LS_RDSON)\s*\(\s*short\s+funcindex", rt)
d600 = defs.count("TM600_HS_RDSON")
d601 = defs.count("TM601_LS_RDSON")
v4 = (d600 == 1 and d601 == 1)
print("[%s] DUT_API definitions: TM600_HS_RDSON=%d  TM601_LS_RDSON=%d (expect 1/1)" % ("PASS" if v4 else "FAIL", d600, d601))

# 5) 追加区块内的一致性（**代码级**：先剥离 // 行注释与 /* */ 块注释，再做计数）
def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in src.split("\n"))


code = strip_comments(body)


def blk(pat, s=None):
    return len(re.findall(pat, code if s is None else s))


checks = {
    "delay_ms(1) in block": blk(r"delay_ms\(1\)"),
    "delay_ms(2) in block": blk(r"delay_ms\(2\)"),
    "SetClamp(50,50) in block": blk(r"SetClamp\(\s*50\s*,\s*50\s*\)"),
    "MeasureVI(200,5 in block": blk(r"MeasureVI\(200\s*,\s*5"),
    "FPVIe_10A in block": blk(r"FPVIe_10A\b"),
    "FPVIe_10UA in block": blk(r"FPVIe_10UA"),
    "rampi_capv in block": blk(r"rampi_capv"),
    "rampv_capv in block": blk(r"rampv_capv"),
}
print("\n      --- 代码级（去注释）---")
for k, v in checks.items():
    print("      %-32s %d" % (k, v))
print("      --- 整块（含注释，供对照）---")
for k, pat in (("delay_ms(1)", r"delay_ms\(1\)"), ("delay_ms(2)", r"delay_ms\(2\)"),
               ("SetClamp(50,50)", r"SetClamp\(\s*50\s*,\s*50\s*\)"), ("MeasureVI(200,5", r"MeasureVI\(200\s*,\s*5"),
               ("FPVIe_10A", r"FPVIe_10A\b"), ("FPVIe_10UA", r"FPVIe_10UA"),
               ("rampi_capv", r"rampi_capv"), ("rampv_capv", r"rampv_capv")):
    print("      %-32s %d" % (k, blk(pat, body)))
v5 = (checks["delay_ms(2) in block"] == 0 and checks["delay_ms(1) in block"] >= 2
      and checks["SetClamp(50,50) in block"] == 2 and checks["MeasureVI(200,5 in block"] == 2
      and checks["FPVIe_10A in block"] == 0 and checks["rampi_capv in block"] == 0 and checks["rampv_capv in block"] == 0)
print("[%s] appended-block CODE matches the frozen payload expectations" % ("PASS" if v5 else "FAIL"))

# 6) 首次使用面：新符号在 baseline 中不存在
bs = before.decode("utf-8-sig")
v6 = ("TM600_HS_RDSON" not in bs and "TM601_LS_RDSON" not in bs)
print("[%s] genuine new capability: symbols absent from baseline" % ("PASS" if v6 else "FAIL"))

verdict = all([v1, v2, v3, v4, v5, v6])
print("\n=== OVERALL: %s ===" % ("PASS" if verdict else "FAIL"))
json.dump({"before": sb, "after": sa, "checks": [v1, v2, v3, v4, v5, v6], "defs": {"TM600": d600, "TM601": d601},
           "blockCounts": checks, "verdict": verdict},
          open(D + "t20-apply-verification.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("wrote t20-apply-verification.json")
raise SystemExit(0 if verdict else 1)
