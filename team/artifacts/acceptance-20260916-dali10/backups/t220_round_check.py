# -*- coding: utf-8 -*-
"""Read-only re-verification for this round: chain integrity, the four FROZEN artifacts, and current named-field presence."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# chain: every entry with selfAnchor should have entriesBeforeThisWrite == index-1 (0-based)
breaks = []
for i, e in enumerate(lg["entries"]):
    sa = e.get("selfAnchor") or {}
    if sa and sa.get("entriesBeforeThisWrite") not in (None, i):
        breaks.append((i, sa.get("entriesBeforeThisWrite")))
manifest = None
for e in lg["entries"]:
    if isinstance(e.get("chainManifest"), dict):
        manifest = e["chainManifest"]["entries"]
mm = []
if manifest:
    for m in manifest:
        idx = m["snapshotIndex"]
        if canon(lg["entries"][idx - 1]) != m["entryCanonicalSha256"]:
            mm.append(idx)
print("entries:", len(lg["entries"]), "| chain breaks:", breaks or 0, "| manifest mismatches:", mm or 0)
print("entries with prevEntryCanonicalSha256:", sum(1 for e in lg['entries'] if isinstance(e, dict) and e.get('prevEntryCanonicalSha256')))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
for k in ("nameFactRule", "byteDeltaCrossCheck", "evidenceStrengthRegister", "structuralVerificationRule", "staleTokenCriterion",
          "citationFormRule", "fieldAddressingRule", "mirrorRecordIdentitySpec", "knownSpecsRegister", "reproducibleCriterion"):
    print("  field present:", k, bool(doc.get(k)))

# FROZEN four
anchors_marks = doc.get("anchors") or {}
print("\nFROZEN-marked artifacts recorded by me:")
for k, v in anchors_marks.items():
    if isinstance(v, dict) and v.get("writesStopped"):
        p = os.path.join(A, k) if os.path.exists(os.path.join(A, k)) else k
        cur = rec(p) if os.path.exists(p) else None
        same = cur and cur["sha256"] == v.get("sha256")
        print("   %-46s recorded=%s current-identical=%s" % (k, str(v.get("sha256"))[:12], same))
