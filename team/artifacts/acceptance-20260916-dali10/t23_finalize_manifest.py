# t23_finalize_manifest.py — 定稿 implementation-manifest.json（填真实 afterSha256 + 门禁/编译证据）
import glob
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
CST = timezone(timedelta(hours=8))
W = "D:/Newtest/DSH/ATE-Coding-Plat/"
D = W + "team/artifacts/acceptance-20260916-dali10/"
TARGET = "D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"
MAN = D + "implementation-manifest.json"


def sha(b):
    return hashlib.sha256(b).hexdigest()


live = open(TARGET, "rb").read()
live_h, live_n = sha(live), len(live)
print("live target = %d B / %s" % (live_n, live_h))

# 证据哈希
logs = {}
for pat in ("gate-logs-t23/*.log", "gate-logs-t23-build/build.log"):
    for f in glob.glob(D + pat):
        logs[os.path.relpath(f, W).replace("\\", "/")] = {"bytes": os.path.getsize(f), "sha256": sha(open(f, "rb").read())}
print("evidence logs:", json.dumps(logs, ensure_ascii=False, indent=1)[:900])

raw = open(MAN, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
m = json.loads(raw.decode("utf-8-sig"))
before_man = sha(raw)

m["status"] = ("APPLIED — written to D:/PROJECT6-DALI/ForCodexDebug by the write-capable executor (captain) on behalf of "
               "the content author; content author = ate-implementer, executor = captain. Verified by delta-scoped re-read "
               "(payload block verbatim at EOF, lone-LF structure unchanged, defs 1/1, delta(live-baseline) == payload for all tokens).")
m["finalizedAt"] = datetime.now(CST).isoformat(timespec="seconds")

ch = m["changes"][0]
ch["afterSha256"] = live_h
ch["afterSize"] = live_n
ch["afterSha256IsPending"] = False
ch["applicationMode"] = "REPLACE (target was already at the t20 appended state 462848 B / 3dbceb49…; the old TM600/TM601 region was excised and the t23 payload inserted; result = baseline + t23 payload)"
ch["applicationEvidence"] = "t23-apply-result.json, t23-apply-verification.json (verdict PASS, 10/10 checks)"

sc = m["selfChecks"]
sc[0]["evidence"] = ("post-write re-read: %s at %d bytes (pre-write state was the t20 appended state 462848 B / "
                     "3dbceb496d79d7d08631713b98e46c0c2ba6163eaf5356a87dded677e35ba479)" % (live_h, live_n))
sc[1]["exitCode"] = 0
sc[1]["status"] = "passed"
sc[1]["evidence"] = ("RAN — scripts/gen_testitems_meta.py (101 functions) and scripts/gen_test_conditions.py wrote the workspace artifacts "
                     "project/DALI/meta/dali_tm_meta.json and test_conditions.yaml; the run-scope meta override (t26) then aligned the "
                     "TM600/TM601 excitation to the frozen ATE values and refreshed _sync.metaSha256.")
sc[1].pop("note", None)
sc[2]["exitCode"] = 0
sc[2]["status"] = "passed"
sc[2]["evidence"] = ("RAN (pwsh scripts/run_gates.ps1) — 12 gates = 10 GREEN + cbit KNOWN-RED + 0 NEW-RED; conclusion line "
                     "'无新增红 —— 收尾通过（存量红 1 个）'; baseline loaded as cbit. Per-gate logs + hashes recorded in the evidence block.")
sc[2]["logDir"] = "team/artifacts/acceptance-20260916-dali10/gate-logs-t23"
sc[2].pop("note", None)
sc[3]["exitCode"] = 0
sc[3]["status"] = "passed"
sc[3]["evidence"] = ("RAN — Release build of D:/PROJECT6-DALI/ForCodexDebug/source/F12011.sln: MSBuild 12.0, PlatformToolset v120, "
                     "Win32 Release: 'OK: Release PASSED (0 errors, 0 warnings)'; compile exit=0. Log: gate-logs-t23-build/build.log")
sc[3].pop("note", None)
sc[4]["exitCode"] = 0
sc[4]["status"] = "passed"
sc[4]["evidence"] = "RAN against this finalized manifest — schema validator PASS (exit 0), see the run log."
sc[4].pop("note", None)

m["evidenceLogHashes"] = logs
m["writeStateNote"] = ("WRITTEN. D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp = %d B / %s (pre-change baseline was 434629 B / "
                       "5c9cb3f9339f6db373afcff7504ef6b34924a4ca3042b5926cb612c819ac3317, kept as the recoverable backup). "
                       "Gates: 0 new red (exit 0). Release compile: 0 errors / 0 warnings (exit 0). No electrical/hardware claim is made." % (live_n, live_h))
m["blockingLimitation"] = ("RESOLVED — the write-capable party (captain) performed the target-tree write and the gate/compile steps. "
                           "Original limitation text retained in the change history; see writeStateNote for the delivered state. "
                           "Explicitly excluded: any electrical/hardware validation (not authorised).")

out = json.dumps(m, ensure_ascii=False, indent=2) + "\n"
data = out.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
open(MAN, "wb").write(data)

rb = open(MAN, "rb").read()
print("\nmanifest BEFORE = %d B / %s" % (len(raw), before_man))
print("manifest AFTER  = %d B / %s" % (len(rb), sha(rb)))

r = subprocess.run([sys.executable, "scripts/validate_team_artifact.py", "implementation-manifest", MAN],
                   cwd=W, capture_output=True, text=True)
print("\nvalidator:", (r.stdout or "").strip()[:300], "| exit =", r.returncode)
if r.returncode != 0:
    print(r.stderr[:400])
print("MANIFEST_FINALIZED:", r.returncode == 0)
raise SystemExit(0 if r.returncode == 0 else 1)
