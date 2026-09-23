# apply_payload_to_target.py — 由具备写权限的一方执行 t20 的外部写入（步骤 1–4）
# 前置断言失败即在写入前中止；写后回读并记录 before/after 明文哈希。
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CST = timezone(timedelta(hours=8))
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
TARGET = "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
PAYLOAD = D + "implementation-payload-TM600-TM601.cpp"
BAK = D + "backups/test.cpp.before_TM600_TM601.bak"
EXPECT_BEFORE = "5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317"
EXPECT_PAYLOAD = "7902f5d91b0c07545b20ccc3103ca0f9bf76d5cb23dc44be6b5efd32312a9122"


def sha(b):
    return hashlib.sha256(b).hexdigest()


report = {"appliedAt": datetime.now(CST).isoformat(timespec="seconds"), "target": TARGET}

# ---- 1) 前置断言 ----
before = open(TARGET, "rb").read()
report["beforeBytes"], report["beforeSha256"] = len(before), sha(before)
print("target BEFORE: %d B / %s" % (len(before), report["beforeSha256"]))
if report["beforeSha256"] != EXPECT_BEFORE:
    print("ABORT: target hash != pinned baseline; tree changed since preparation.")
    raise SystemExit(2)

bak = open(BAK, "rb").read()
report["backupBytes"], report["backupSha256"] = len(bak), sha(bak)
if bak != before:
    print("ABORT: backup is not byte-identical to the live target.")
    raise SystemExit(3)
print("backup verified byte-identical to live target: %d B / %s" % (len(bak), report["backupSha256"]))

praw = open(PAYLOAD, "rb").read()
report["payloadBytes"], report["payloadSha256"] = len(praw), sha(praw)
if report["payloadSha256"] != EXPECT_PAYLOAD:
    print("ABORT: payload hash != pinned value %s (live %s)" % (EXPECT_PAYLOAD, report["payloadSha256"]))
    raise SystemExit(4)
print("payload verified: %d B / %s" % (len(praw), report["payloadSha256"]))

# ---- 2) 组装（CRLF 归一 + BOM 保持）----
body = praw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
text = before.decode("utf-8-sig")
if not text.endswith("\n"):
    text += "\r\n"
new_text = text + body
data = new_text.encode("utf-8")
if not data.startswith(b"\xef\xbb\xbf"):
    data = b"\xef\xbb\xbf" + data

# ---- 3) 写入（二进制）----
with open(TARGET, "wb") as f:
    f.write(data)

# ---- 4) 写后回读 ----
rb = open(TARGET, "rb").read()
report["afterBytes"], report["afterSha256"] = len(rb), sha(rb)
report["bomOk"] = rb[:3] == b"\xef\xbb\xbf"
report["loneLF"] = rb.count(b"\n") - rb.count(b"\r\n")
rt = rb.decode("utf-8-sig")
report["tm600SymbolHits"] = rt.count("TM600_HS_RDSON")
report["tm601SymbolHits"] = rt.count("TM601_LS_RDSON")
report["delay1"] = rt.count("delay_ms(1)")
report["delay2"] = rt.count("delay_ms(2)")
report["setClamp"] = rt.count("SetClamp(50,50)")
report["measureVI200x5"] = rt.count("MeasureVI(200,5")
report["fpvi10A"] = rt.count("FPVIe_10A")
report["fpvi10UA"] = rt.count("FPVIe_10UA")
report["payloadAppendedVerbatim"] = (rb.endswith(data[-4000:]) and report["afterBytes"] == len(data))
report["bytesAdded"] = report["afterBytes"] - report["beforeBytes"]

print("\ntarget AFTER : %d B / %s (added %d B)" % (report["afterBytes"], report["afterSha256"], report["bytesAdded"]))
print("  BOM ok=%s  loneLF=%d" % (report["bomOk"], report["loneLF"]))
print("  TM600_HS_RDSON=%d  TM601_LS_RDSON=%d  delay_ms(1)=%d  delay_ms(2)=%d  SetClamp=%d  MeasureVI(200,5=%d  FPVIe_10A=%d FPVIe_10UA=%d"
      % (report["tm600SymbolHits"], report["tm601SymbolHits"], report["delay1"], report["delay2"],
         report["setClamp"], report["measureVI200x5"], report["fpvi10A"], report["fpvi10UA"]))

outp = D + "t20-apply-result.json"
with open(outp, "w", encoding="utf-8") as f:
    json.dump(report, f, ensure_ascii=False, indent=2)
print("\nwrote", outp)
