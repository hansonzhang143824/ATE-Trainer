# t29_apply_replace.py — 以 REPLACE 语义落盘 t29 payload（73b511b7…）到 debug 副本
# 安全设计：前置断言 → 带边界断言的切除 → 写入 → 增量口径回读校验 → **任一校验失败自动回滚为写入前字节**。
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
EXPECT_TARGET = "15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a"   # t23 落盘态（含 K109/K110 缺陷）
EXPECT_PRE = "5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317"      # 改动前基线（可恢复备份）
# canonical = t29 final（owner 声明 + 三名成员实测：含 K109/K110 + TM601 逐函数理由块）
EXPECT_PAYLOAD = "272667f3f79393b6b1365237c7ac01bed7a527d2984d53d1d5ae6804515057c0"
EXPECT_PAYLOAD_SIZE = 38147
BANNERS = ("// t5 implementation payload", "// TM600_HS_RDSON", "// t29")


def sha(b):
    return hashlib.sha256(b).hexdigest()


def stripped(src):
    src = re.sub(r"/\*.*?\*/", "", src, flags=re.S)
    return "\n".join(re.sub(r"//.*$", "", ln) for ln in src.split("\n"))


TOK = {
    "delay_ms(1)": r"delay_ms\(1\)", "delay_ms(2)": r"delay_ms\(2\)",
    "SetClamp(50,50)": r"SetClamp\(\s*50\s*,\s*50\s*\)", "MeasureVI(200,5": r"MeasureVI\(200\s*,\s*5",
    "rampi_capv": r"rampi_capv", "rampv_capv": r"rampv_capv", "bare126": r"(?<![\w.])126(?![\w.])",
    "K126_V1P5_CAP": r"K126_V1P5_CAP", "ERROR_RES": r"ERROR_RES", "K5_VBUS_Cap": r"K5_VBUS_Cap",
    "K44_Cap_SW2_BST2": r"K44_Cap_SW2_BST2", "K45_Cap_SW1_BST1": r"K45_Cap_SW1_BST1",
    "K57_CAP_BST_SW": r"K57_CAP_BST_SW", "K109": r"K109", "K110": r"K110",
}

rep = {"appliedAt": datetime.now(CST).isoformat(timespec="seconds"), "target": TARGET, "mode": "REPLACE"}
before = open(TARGET, "rb").read()
rep["beforeBytes"], rep["beforeSha256"] = len(before), sha(before)
print("target BEFORE: %d B / %s" % (len(before), rep["beforeSha256"]))
if rep["beforeSha256"] != EXPECT_TARGET:
    print("ABORT: target != documented t23 state (%s)" % EXPECT_TARGET); raise SystemExit(2)

bak = open(BAK, "rb").read()
if sha(bak) != EXPECT_PRE:
    print("ABORT: backup != pre-change baseline"); raise SystemExit(3)
rep["backupSha256"] = sha(bak)

praw = open(PAYLOAD, "rb").read()
rep["payloadBytes"], rep["payloadSha256"] = len(praw), sha(praw)
if rep["payloadSha256"] != EXPECT_PAYLOAD or rep["payloadBytes"] != EXPECT_PAYLOAD_SIZE:
    print("ABORT: payload != expected (%s / %d)" % (EXPECT_PAYLOAD, EXPECT_PAYLOAD_SIZE)); raise SystemExit(4)
print("payload verified: %d B / %s" % (len(praw), rep["payloadSha256"]))

text = before.decode("utf-8-sig")
idx = -1
for b in BANNERS:
    idx = text.find(b)
    if idx >= 0:
        rep["bannerUsed"] = b
        break
if idx < 0:
    idx = text.find("DUT_API int TM600_HS_RDSON")
    rep["bannerUsed"] = "(none: cut at first DUT_API)"
    print("WARN: no banner found; cutting at the first DUT_API definition")
if idx < 0:
    print("ABORT: cannot locate the previously appended region"); raise SystemExit(5)
excised = text[idx:]
if not excised.lstrip().startswith("//"):
    print("ABORT: excision start is not a comment banner — refusing to cut mid-code"); raise SystemExit(6)
rep["excisedBytes"] = len(excised.encode("utf-8"))
rep["excisedHasTM601"] = "TM601_LS_RDSON" in excised
if not rep["excisedHasTM601"]:
    print("ABORT: excised region lacks the previous TM601"); raise SystemExit(7)

head = text[:idx]
if not head.endswith("\n"):
    head += "\r\n"
body = praw.decode("utf-8-sig").replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\r\n")
data = (head + body).encode("utf-8")
if not data.startswith(b"\xef\xbb\xbf"):
    data = b"\xef\xbb\xbf" + data

with open(TARGET, "wb") as f:
    f.write(data)
rb = open(TARGET, "rb").read()

# ---- 回读校验（区块保真 + 增量口径）----
base_c, live_c, pay_c = stripped(bak.decode("utf-8-sig")), stripped(rb.decode("utf-8-sig")), stripped(body.encode("utf-8"))
deltas = {k: len(re.findall(p, live_c)) - len(re.findall(p, base_c)) for k, p in TOK.items()}
payload_counts = {k: len(re.findall(p, pay_c)) for k, p in TOK.items()}
checks = {
    "blockVerbatimAtEOF": rb.endswith(body.encode("utf-8")) or rb[3:].endswith(body.encode("utf-8")),
    "bomPreserved": rb[:3] == b"\xef\xbb\xbf",
    "loneLFUnchanged": (rb.count(b"\n") - rb.count(b"\r\n")) == (before.count(b"\n") - before.count(b"\r\n")),
    "defsTM600": len(re.findall(r"DUT_API\s+int\s+TM600_HS_RDSON\s*\(\s*short\s+funcindex", rb.decode("utf-8-sig"))),
    "defsTM601": len(re.findall(r"DUT_API\s+int\s+TM601_LS_RDSON\s*\(\s*short\s+funcindex", rb.decode("utf-8-sig"))),
    "deltaMatchesPayload": deltas == payload_counts,
    "K109Delta": deltas["K109"], "K110Delta": deltas["K110"],
}
rep.update({"afterBytes": len(rb), "afterSha256": sha(rb), "deltas": deltas,
            "payloadCounts": payload_counts, "checks": checks})
ok = (checks["blockVerbatimAtEOF"] and checks["bomPreserved"] and checks["loneLFUnchanged"]
      and checks["defsTM600"] == 1 and checks["defsTM601"] == 1 and checks["deltaMatchesPayload"]
      and deltas["K109"] >= 2 and deltas["K110"] >= 2 and deltas["bare126"] == 0)
rep["verdict"] = bool(ok)

if not ok:
    with open(TARGET, "wb") as f:      # 自动回滚为写入前字节
        f.write(before)
    rep["rolledBack"] = True
    rep["rollbackSha256"] = sha(open(TARGET, "rb").read())
    print("VERIFICATION FAILED → ROLLED BACK to %s" % rep["rollbackSha256"])
else:
    rep["rolledBack"] = False

print("after: %d B / %s | K109Δ=%s K110Δ=%s bare126Δ=%s" %
      (rep["afterBytes"], rep["afterSha256"], deltas["K109"], deltas["K110"], deltas["bare126"]))
json.dump(rep, open(D + "t29-apply-result.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("VERDICT: %s (wrote t29-apply-result.json)" % ("PASS" if ok else "FAIL"))
raise SystemExit(0 if ok else 8)
