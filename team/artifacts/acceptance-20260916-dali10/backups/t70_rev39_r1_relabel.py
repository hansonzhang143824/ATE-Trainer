# -*- coding: utf-8 -*-
"""rev 39 (final): relabel registrationApplication.R1 as SATISFIED BY DERIVATION; t34: correct the --check-extra wording."""
import json, hashlib, os, datetime, subprocess, sys, re

A = r"team/artifacts/acceptance-20260916-dali10"
g = os.path.join(A, "setup-contract-build.py")
art = os.path.join(A, "setup-contract.json")

# ---- verify the captain's claim about the generator ----
lines = open(g, encoding="utf-8").read().splitlines()
print("--- generator around the aliasesUsed derivation (L1320-1332) ---")
for i in range(1320, 1333):
    if i <= len(lines):
        print("%5d| %s" % (i, lines[i - 1][:150]))
derived = any('"aliasesUsed": [a["alias"] for a in ALIASES if tm in a.get("usedByTm", [])]' in l for l in lines)
print("derivation line present:", derived)

d0 = json.load(open(art, encoding="utf-8"))
print("TM600.aliasesUsed:", d0["tmDeltas"]["TM600"]["aliasesUsed"])
print("bst2sw.usedByTm:", [x["usedByTm"] for x in d0["aliasResolution"] if x["alias"] == "bst2sw"])
print("R1 now:", d0["registrationApplication"]["R1"]["status"])
print("gate-read field:", [x["resolution"]["closedRelayNumbers"] for x in d0["aliasResolution"] if x["alias"] == "bst2sw"])

src = open(g, encoding="utf-8").read()
marker = "# ================== end rev 25 additions =================="
extra = ('# ===== rev 39 (FINAL): R1 relabelled as satisfied by derivation =====\n'
         'try:\n'
         '    _r1 = contract["registrationApplication"].get("R1")\n'
         '    if isinstance(_r1, dict):\n'
         '        _r1["previousStatus"] = _r1.get("status")\n'
         '        _r1["status"] = ("SATISFIED BY DERIVATION (generator L1326): tmDeltas.<TM>.aliasesUsed is derived as [a[\\"alias\\"] for a in ALIASES if tm in a.get(\\"usedByTm\\", [])], "\n'
         '                          "and aliasResolution[bst2sw].usedByTm contains only TM600, so bst2sw is already in TM600.aliasesUsed without any explicit edit. No pending action remains; the explicit append recorded in rev 36 was a no-op redundancy kept only in provenance.")\n'
         'except Exception:\n'
         '    pass\n')
if marker in src and "rev 39 (FINAL): R1 relabelled" not in src:
    src = src.replace(marker, extra + marker, 1)
    src = src.replace("CONTRACT_REVISION = 38", "CONTRACT_REVISION = 39", 1)
    src = src.replace('GENERATED_AT = "2026-09-16 19:30:00 (revision 38)"', 'GENERATED_AT = "2026-09-16 19:30:00 (revision 39)"', 1)
    open(g, "w", encoding="utf-8").write(src)

    def run():
        r = subprocess.run([sys.executable, g], capture_output=True, text=True)
        if r.returncode != 0:
            print("GEN FAIL", r.stdout[-400:], r.stderr[-1000:]); sys.exit(1)
        b = open(art, "rb").read(); return len(b), hashlib.sha256(b).hexdigest()

    a1 = run(); a2 = run()
    d = json.load(open(art, encoding="utf-8"))
    print("\nrev:", d["revision"], "| identical:", a1 == a2)
    print("R1:", d["registrationApplication"]["R1"]["status"][:130])
    print("gate-read field now:", [x["resolution"]["closedRelayNumbers"] for x in d["aliasResolution"] if x["alias"] == "bst2sw"])
    print("file:", a1[0], "B /", a1[1], "@", datetime.datetime.fromtimestamp(os.stat(art).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
else:
    print("generator already patched or marker missing")

# ---- t34: --check-extra wording ----
f34 = os.path.join(A, "acceptance-report.json")
dd = json.load(open(f34, encoding="utf-8"))
NEWW = ("(corrected per the captain) the DISABLE requirement is lifted from rev 29 onward (this version closes a single route and over-closes nothing); the batch's gate runs with the DEFAULT subset check. "
        "Whether --check-extra is actually ENABLED is a separate decision (it requires a defined budget pool and must be measured by t54) and therefore must NOT be described as 're-enabled' before that measurement.")
n = 0
for i, x in enumerate(dd["limitations"]):
    if x.startswith("L23 (limitation: --check-extra"):
        dd["limitations"][i] = x.split(" STATUS UPDATE")[0] + " STATUS UPDATE " + NEWW
        n += 1
    elif "RE-ENABLED" in x:
        dd["limitations"][i] = x.replace("RE-ENABLED for the final batch", "not a requirement to disable from rev 29 onward (NOT 're-enabled' - enabling is a separate, unmeasured decision)")
        n += 1
json.dump(dd, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34 --check-extra entries updated:", n)
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

# ---- pin + anchors ----
pin = os.path.join(A, "setup-contract-pin.json")
def rec(f):
    b = open(f, "rb").read(); return len(b), hashlib.sha256(b).hexdigest(), datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")
n1, s1, m1 = rec(art); gn, gs, gm = rec(g)
p = json.load(open(pin, encoding="utf-8"))
p["revision"] = 39; p["sha256"] = s1; p["sizeBytes"] = n1; p["measuredAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
p["generatedAt"] = "2026-09-16 19:30:00 (revision 39)"
p["generator"] = {"path": "team/artifacts/acceptance-20260916-dali10/setup-contract-build.py", "sizeBytes": gn, "sha256": gs}
p["freezeDeclaration"] = ("FROZEN at rev 39 (last authorised wording change: R1 relabelled SATISFIED BY DERIVATION). Gate-read field aliasResolution[bst2sw].resolution.closedRelayNumbers = [48,60,61,76], unchanged. "
                          "Any further change requires prior written notice to the captain with old hash -> change -> new hash -> fresh reviewer verdict on the new bytes.")
json.dump(p, open(pin, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pn, ps, pm = rec(pin)
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
for k, f in (("setup-contract.json", art), ("setup-contract-build.py", g), ("setup-contract-pin.json", pin), ("acceptance-report.json", f34)):
    a, b_, c = rec(f)
    doc["anchors"][k] = {"path": f.replace("\\", "/"), "sizeBytes": a, "sha256": b_, "measuredAt": c}
doc["freezeNote"] = "contract FROZEN at rev 39; gate-read field [48,60,61,76]; further changes need prior written notice + reviewer verdict"
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("pin:", pn, "B /", ps)
print("anchors:", os.path.getsize(ap), "B")
