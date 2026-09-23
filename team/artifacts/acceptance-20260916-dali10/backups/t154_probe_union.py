# -*- coding: utf-8 -*-
"""Independent reproduction of the union-accumulation probe.

The owner's generator hardcodes its output to gate-logs-t28/t28-anchors.json (its own live artifact),
so I must NOT run it as-is. I copy it verbatim to my own scratch, patch EXACTLY TWO lines
(the workspace root and the output path) and run it against an OFFLINE copy of the shared file
with three foreign-prefix entries injected. The union logic itself is untouched.
"""
import json, hashlib, os, re, shutil, subprocess, sys, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
PROBE = os.path.join(A, "backups", "probe-union")
os.makedirs(PROBE, exist_ok=True)
SRC = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
src_text = open(SRC, encoding="utf-8").read()
print("owner generator:", os.path.getsize(SRC), "B /", hashlib.sha256(open(SRC, "rb").read()).hexdigest())

WS = os.path.abspath(".")
patched = src_text
patched = re.sub(r"WS = os\.path\.abspath\(os\.path\.join\(HERE, '\.\.', '\.\.', '\.\.', '\.\.'\)\)",
                 lambda m: "WS = r'%s'  # PATCHED FOR OFFLINE PROBE" % WS, patched)
offline_out = os.path.join(PROBE, "offline-t28-anchors.json")
patched = patched.replace("out = os.path.join(HERE, 't28-anchors.json')",
                          "out = r'%s'  # PATCHED FOR OFFLINE PROBE" % offline_out)
diff_lines = [i + 1 for i, (a, b) in enumerate(zip(src_text.splitlines(), patched.splitlines())) if a != b]
print("patched line numbers:", diff_lines, "(expected exactly 2)")
assert len(diff_lines) == 2, "expected exactly two patched lines"
probe_py = os.path.join(PROBE, "t28_make_anchors_offline.py")
open(probe_py, "w", encoding="utf-8").write(patched)
print("probe copy:", os.path.getsize(probe_py), "B /", hashlib.sha256(open(probe_py, "rb").read()).hexdigest())

# build the offline copy of the shared file with foreign entries injected
shared = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
sh = json.load(open(shared, encoding="utf-8"))
ppn = sh.setdefault("preservedPeerNamespaces", {})
ppn["qaProbeAnchors"] = {"anchors": {("PROBE%d.json" % i): {"note": "injected offline by setup-architect"} for i in (1, 2, 3)},
                         "injectedBy": "setup-architect (independent probe)", "at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
before_probe = len(ppn["qaProbeAnchors"]["anchors"])
before_peer = len((ppn.get("setupArchitectFreezeAnchors") or {}).get("anchors") or {})
json.dump(sh, open(offline_out, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("\nOFFLINE copy built (live file untouched):", os.path.getsize(offline_out), "B")
print("  before run: probe entries =", before_probe, "| foreign(setupArchitect) entries =", before_peer)

# run the patched generator against the offline copy
r = subprocess.run([sys.executable, probe_py], capture_output=True, text=True, cwd=WS)
print("\n--- probe run ---")
print("exit:", r.returncode)
print((r.stdout or "")[-600:])
if r.stderr:
    print("stderr:", r.stderr[-400:])

after = json.load(open(offline_out, encoding="utf-8"))
ap_ = after.get("preservedPeerNamespaces", {})
after_probe = len((ap_.get("qaProbeAnchors") or {}).get("anchors") or {})
after_peer = len((ap_.get("setupArchitectFreezeAnchors") or {}).get("anchors") or {})
print("\n=== RESULT ===")
print("probe entries before/after:", before_probe, "->", after_probe)
print("foreign(setupArchitect) entries before/after:", before_peer, "->", after_peer)
print("probe namespaces kept:", sorted(ap_.keys()))
print("(ii) no-loss of current content:", "REPRODUCED" if after_probe >= before_probe else "NOT reproduced")

# live file must be untouched
live_b = open(shared, "rb").read()
print("\nlive shared file after probe:", len(live_b), "B /", hashlib.sha256(live_b).hexdigest())
print("live file contains PROBE:", "PROBE" in live_b.decode("utf-8", "replace") or "qaProbeAnchors" in live_b.decode("utf-8", "replace"))
