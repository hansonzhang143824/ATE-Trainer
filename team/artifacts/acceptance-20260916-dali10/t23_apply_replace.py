# t23_apply_replace.py — 以 REPLACE 语义落盘 t23 payload（444810dd…）到 debug 副本
# 前置断言失败即在写入前中止；写后回读并记录 before/after 明文哈希。
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CST = timezone(timedelta(hours=8))
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
TARGET = "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
PAYLOAD = D + "implementation-payload-TM600-TM601.cpp"
BAK = D + "backups/test.cpp.before_TM600_TM601.bak"
EXPECT_TARGET = "3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479"   # t20 appended state
EXPECT_PRE = "5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317"      # pre-change baseline
EXPECT_PAYLOAD = "444810dde99f79ed1ef1939bb1659d5769f547bfc1103e9b9187ee46f455675c"
BANNER = "// t5 implementation payload"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def strip_comments(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in src.split("\n"))


rep = {"appliedAt": datetime.now(CST).isoformat(timespec="seconds"), "target": TARGET, "mode": "REPLACE"}

# ---- 1) 前置断言 ----
before = open(TARGET, "rb").read()
rep["beforeBytes"], rep["beforeSha256"] = len(before), sha(before)
print("target BEFORE: %d B / %s" % (len(before), rep["beforeSha256"]))
if rep["beforeSha256"] != EXPECT_TARGET:
    print("ABORT: target is not at the documented t20 appended state (%s)" % EXPECT_TARGET)
    raise SystemExit(2)

bak = open(BAK, "rb").read()
rep["backupBytes"], rep["backupSha256"] = len(bak), sha(bak)
if rep["backupSha256"] != EXPECT_PRE:
    print("ABORT: backup hash != pre-change baseline %s (live %s)" % (EXPECT_PRE, rep["backupSha256"]))
    raise SystemExit(3)
print("backup verified (pre-change baseline): %d B / %s" % (len(bak), rep["backupSha256"]))

praw = open(PAYLOAD, "rb").read()
rep["payloadBytes"], rep["payloadSha256"] = len(praw), sha(praw)
if rep["payloadSha256"] != EXPECT_PAYLOAD:
    print("ABORT: payload hash != %s (live %s)" % (EXPECT_PAYLOAD, rep["payloadSha256"]))
    raise SystemExit(4)
print("payload verified: %d B / %s" % (len(praw), rep["payloadSha256"]))

# ---- 2) 定位并切除旧的 TM600/TM601 区段（banner 起到 EOF）----
text = before.decode("utf-8-sig")
idx = text.find(BANNER)
if idx < 0:
    idx = text.find("DUT_API int TM600_HS_RDSON")
    print("WARN: banner marker not found; truncating at the first DUT_API definition instead")
if idx < 0:
    print("ABORT: cannot locate the previously appended region")
    raise SystemExit(5)
excised = text[idx:]
rep["excisedBytes"] = len(excised.encode("utf-8"))
rep["excisedHadTM601"] = "TM601_LS_RDSON" in excised
rep["excisedEndsFile"] = text.rstrip() == text[:idx].rstrip() + excised.rstrip()
print("excising %d B from offset %d (contains TM601_LS_RDSON=%s)" % (rep["excisedBytes"], idx, rep["excisedHadTM601"]))
if not rep["excisedHadTM601"]:
    print("ABORT: the excised region does not contain the previous TM601 function")
    raise SystemExit(6)

head = text[:idx]
if not head.endswith("\n"):
    head += "\r\n"

# ---- 3) 组装（payload 全文，CRLF 归一）----
body = praw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
new_text = head + body
data = new_text.encode("utf-8")
if not data.startswith(b"\xef\xbb\xbf"):
    data = b"\xef\xbb\xbf" + data

# ---- 4) 写入 + 回读 ----
with open(TARGET, "wb") as f:
    f.write(data)
rb = open(TARGET, "rb").read()
rep["afterBytes"], rep["afterSha256"] = len(rb), sha(rb)
rt = rb.decode("utf-8-sig")
code = strip_comments(rt)
rep["bomOk"] = rb[:3] == b"\xef\xbb\xbf"
rep["loneLF"] = rb.count(b"\n") - rb.count(b"\r\n")
rep["defsTM600"] = len(re.findall(r"DUT_API\s+int\s+TM600_HS_RDSON\s*\(\s*short\s+funcindex", rt))
rep["defsTM601"] = len(re.findall(r"DUT_API\s+int\s+TM601_LS_RDSON\s*\(\s*short\s+funcindex", rt))
rep["code"] = {
    "delay_ms(1)": len(re.findall(r"delay_ms\(1\)", code)),
    "delay_ms(2)": len(re.findall(r"delay_ms\(2\)", code)),
    "SetClamp(50,50)": len(re.findall(r"SetClamp\(\s*50\s*,\s*50\s*\)", code)),
    "MeasureVI(200,5": len(re.findall(r"MeasureVI\(200\s*,\s*5", code)),
    "rampi_capv": len(re.findall(r"rampi_capv", code)),
    "rampv_capv": len(re.findall(r"rampv_capv", code)),
    "bare126": len(re.findall(r"(?<![\w.])126(?![\w.])", code)),
    "K126_V1P5_CAP": len(re.findall(r"K126_V1P5_CAP", code)),
    "ERROR_RES": len(re.findall(r"ERROR_RES", code)),
    "K5_VBUS_Cap": len(re.findall(r"K5_VBUS_Cap", code)),
    "K44_Cap_SW2_BST2": len(re.findall(r"K44_Cap_SW2_BST2", code)),
    "K45_Cap_SW1_BST1": len(re.findall(r"K45_Cap_SW1_BST1", code)),
    "K57_CAP_BST_SW": len(re.findall(r"K57_CAP_BST_SW", code)),
    "inert for the measurement": rt.count("inert for the measurement"),
}
print("\ntarget AFTER : %d B / %s" % (rep["afterBytes"], rep["afterSha256"]))
print("  BOM=%s loneLF=%d | defs TM600=%d TM601=%d" % (rep["bomOk"], rep["loneLF"], rep["defsTM600"], rep["defsTM601"]))
print("  code:", json.dumps(rep["code"], ensure_ascii=False))

ok = (rep["bomOk"] and rep["loneLF"] == 0 and rep["defsTM600"] == 1 and rep["defsTM601"] == 1
      and rep["code"]["delay_ms(1)"] == 6 and rep["code"]["delay_ms(2)"] == 0
      and rep["code"]["SetClamp(50,50)"] == 2 and rep["code"]["MeasureVI(200,5"] == 2
      and rep["code"]["rampi_capv"] == 0 and rep["code"]["rampv_capv"] == 0
      and rep["code"]["bare126"] == 0 and rep["code"]["K126_V1P5_CAP"] == 2
      and rep["code"]["ERROR_RES"] == 2 and rep["code"]["K5_VBUS_Cap"] == 0
      and rep["code"]["K44_Cap_SW2_BST2"] == 0 and rep["code"]["K45_Cap_SW1_BST1"] == 0
      and rep["code"]["K57_CAP_BST_SW"] == 2 and rep["code"]["inert for the measurement"] == 0)
rep["verdict"] = bool(ok)
with open(D + "t23-apply-result.json", "w", encoding="utf-8") as f:
    json.dump(rep, f, ensure_ascii=False, indent=2)
print("\nVERDICT: %s" % ("PASS" if ok else "FAIL"))
print("wrote t23-apply-result.json")
raise SystemExit(0 if ok else 7)
