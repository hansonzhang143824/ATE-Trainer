# -*- coding: utf-8 -*-
"""Final contract wording fix (rev 38): mark revision29Bindings.completenessUnderBothReadings superseded + correct its disposition; align pendingOwnerRuling to the captain's wording.
The gate-read field aliasResolution[bst2sw].resolution.closedRelayNumbers must remain [48,60,61,76]."""
import json, hashlib, os, datetime, subprocess, sys, re

A = r"team/artifacts/acceptance-20260916-dali10"
g = os.path.join(A, "setup-contract-build.py")
art = os.path.join(A, "setup-contract.json")
src = open(g, encoding="utf-8").read()
before_field = None
try:
    d0 = json.load(open(art, encoding="utf-8"))
    before_field = [x for x in d0["aliasResolution"] if x["alias"] == "bst2sw"][0]["resolution"]["closedRelayNumbers"]
except Exception as e:
    print("pre-read failed:", e)
print("gate-read field BEFORE:", before_field)

marker = "# ================== end rev 25 additions =================="
extra = '''# ===== rev 38 (FINAL wording pass; captain-ordered): mark the union paragraph superseded and close the pending ruling in the captain's words =====
_r29 = contract.get("revision29Bindings")
if isinstance(_r29, dict):
    _cbr = _r29.get("completenessUnderBothReadings")
    if isinstance(_cbr, dict):
        _cbr["SUPERSEDED"] = ("The union reading below was WITHDRAWN after the t43 final adjudication (production-tree behaviour fixes the channel-5 route: every in-service implementation driving "
                              "SW12_U1REF_BST_ACM closes K48+K76; file-wide K110_ACM18_BST = 0 and K109_BUSL1_PB0 = 0). Disposition for this batch: ADD K48/K76 and REMOVE K109/K110. "
                              "This paragraph is retained as history only and is NOT the operative rule.")
for _a in contract.get("aliasResolution", []):
    if _a.get("alias") == "bst2sw":
        _ca = _a.setdefault("contestedAttribution", {})
        _ca["pendingOwnerRuling"] = ("CLOSED - t43 final adjudication: ruled (a) CHANNEL 5; the decision field was switched to [48,60,61,76] by t53 (captain takeover). "
                                     "Original channel-18 text, relayChainSuperseded and BST_original_t49 are retained verbatim for provenance.")
'''
if marker in src and "rev 38 (FINAL wording pass" not in src:
    src = src.replace(marker, extra + marker, 1)
    src = src.replace("CONTRACT_REVISION = 37", "CONTRACT_REVISION = 38", 1)
    src = src.replace('GENERATED_AT = "2026-09-16 19:30:00 (revision 37)"', 'GENERATED_AT = "2026-09-16 19:30:00 (revision 38)"', 1)
    open(g, "w", encoding="utf-8").write(src)

    def run():
        r = subprocess.run([sys.executable, g], capture_output=True, text=True)
        if r.returncode != 0:
            print("GENERATOR FAILED", r.stdout[-500:], r.stderr[-1200:]); sys.exit(1)
        b = open(art, "rb").read(); return len(b), hashlib.sha256(b).hexdigest()

    a1 = run(); a2 = run()
    print("rev38 run1:", a1, "| run2:", a2, "| identical:", a1 == a2)
    d = json.load(open(art, encoding="utf-8"))
    f = [x for x in d["aliasResolution"] if x["alias"] == "bst2sw"][0]["resolution"]["closedRelayNumbers"]
    ca = [x for x in d["aliasResolution"] if x["alias"] == "bst2sw"][0]["contestedAttribution"]
    print("revision:", d["revision"], "| gate-read field AFTER:", f, "| unchanged:", f == before_field)
    print("union paragraph SUPERSEDED:", "SUPERSEDED" in (d["revision29Bindings"]["completenessUnderBothReadings"] or {}))
    print("pendingOwnerRuling:", ca["pendingOwnerRuling"][:100])
    print("file:", a1[0], "B /", a1[1], "@", datetime.datetime.fromtimestamp(os.stat(art).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))
else:
    print("generator already patched or marker missing")
