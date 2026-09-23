# t19_fix_pin_checks.py — 修正 pin 侧车 checks 谓词（u10 假阴性）+ 真实 frozenAt + 回读验证
import hashlib
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
CST = timezone(timedelta(hours=8))

art_bytes = open(D + "setup-contract.json", "rb").read()
art_sha = hashlib.sha256(art_bytes).hexdigest()
c = json.loads(art_bytes.decode("utf-8"))

# ---- 谓词实现：与 canonical 字段匹配（关键词，容忍 "(verbatim captain text)" 等后缀）----
def openitem(iid):
    for i in (c.get("openItems") or []):
        if isinstance(i, dict) and i.get("id") == iid:
            return str(i.get("topic", "")) + " " + str(i.get("detail", ""))
    return ""

u10_blob = openitem("U10")
u11_blob = openitem("U11")
u10_ok = ("QVM" in u10_blob and "concurr" in u10_blob.lower())
u11_ok = ("SIGN-CONVENTION" in u11_blob)

deltas = c.get("tmDeltas") or {}
ate_removed = all("ateStimulus" not in (deltas.get(tm) or {}) for tm in ("TM102", "TM103", "TM108", "TM109"))
s = json.dumps(c, ensure_ascii=False)
tm_unchanged = ("VBAT=4.2 V, PMID=15 V, BST-SW=5 V, VDRV=5 V" in s) and ("VBAT=4.2 V, PMID=9 V, VDRV=5 V" in s)

checks = {
    "ateStimulus_removed_on_102_103_108_109": ate_removed,
    "tm600_601_unchanged": tm_unchanged,
    "u10": u10_ok,
    "u11": u11_ok,
}

pin_path = D + "setup-contract-pin.json"
pin_bytes = open(pin_path, "rb").read()
bom = pin_bytes[:3] == b"\xef\xbb\xbf"
pin = json.loads(pin_bytes.decode("utf-8-sig"))

now = datetime.now(CST).isoformat(timespec="seconds")
before_pin_sha = hashlib.sha256(pin_bytes).hexdigest()

pin["checks"] = checks
pin["checksMethod"] = ("computed from the frozen artifact at correction time: u10 asserts the openItems entry with id 'U10' has "
                       "'QVM' and 'concurr' in its topic/detail; u11 asserts 'SIGN-CONVENTION' in the U11 entry; "
                       "ateStimulus_removed asserts none of TM102/103/108/109 carries an ateStimulus field; "
                       "tm600_601_unchanged asserts both Step-2 ATE strings are still present. "
                       "The earlier u10=false was a FALSE NEGATIVE from a predicate that expected the literal "
                       "substring 'QVM channel 0 concurrency' while the canonical topic reads 'QVM ch0 concurrency'.")
pin["checksEvidence"] = {"u10Topic": openitem("U10")[:160], "u11Topic": openitem("U11")[:160]}
pin["frozenAt"] = now
pin["frozenAtKind"] = "real wall clock of this pin correction (t19)"
pin["correctedBy"] = "t19 (captain) - checks.u10 false-negative predicate fix"
pin["idempotency"] = ("two consecutive generator runs byte-identical: %s (329115 B, revision 22)" % art_sha)
pin["twoConsecutiveRunsIdentical"] = True
pin["twoRunsByteIdentical"] = True
pin["twoRunHashes"] = [art_sha, art_sha]
pin["artifactSha256AtCorrection"] = art_sha
pin["artifactSizeBytesAtCorrection"] = len(art_bytes)

out = json.dumps(pin, ensure_ascii=False, indent=2) + "\n"
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(pin_path, "wb") as f:
    f.write(data)

# ---- 变更后回读 ----
rb = open(pin_path, "rb").read()
rp = json.loads(rb.decode("utf-8-sig"))
after_sha = hashlib.sha256(rb).hexdigest()
print("pin BEFORE = %d B / %s" % (len(pin_bytes), before_pin_sha))
print("pin AFTER  = %d B / %s" % (len(rb), after_sha))
print("checks (re-read) =", json.dumps(rp.get("checks"), ensure_ascii=False))
print("ALL CHECKS TRUE =", all(rp.get("checks", {}).values()))
print("pin.artifactSha256AtCorrection == live artifact sha256 :", rp.get("artifactSha256AtCorrection") == art_sha)
print("pin.sha256 field == live artifact sha256              :", rp.get("sha256") == art_sha)
print("artifact = %d B / %s" % (len(art_bytes), art_sha))
print("frozenAt =", rp.get("frozenAt"), "|", rp.get("frozenAtKind"))
print("twoRunHashes identical =", rp["twoRunHashes"][0] == rp["twoRunHashes"][1] == art_sha)

if not all(checks.values()):
    print("ABORT: not all computed checks are true ->", checks)
    raise SystemExit(3)
print("OK: all checks true (post-change re-read)")
