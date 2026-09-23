# -*- coding: utf-8 -*-
"""Final integrity self-audit of my own artifacts: chain check, FROZEN accuracy, stale-claim sweep, pointer sanity, name check."""
import json, hashlib, os, re, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
dep = r"D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp"

def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

findings = []

# 1) ledger chain integrity
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
bad_chain = []
for i, e in enumerate(lg["entries"], 1):
    sa = e.get("selfAnchor") or {}
    if sa and sa.get("entriesBeforeThisWrite") != i - 1:
        bad_chain.append((i, sa.get("entriesBeforeThisWrite")))
manifest = None
for e in lg["entries"]:
    if isinstance(e.get("chainManifest"), dict):
        manifest = e["chainManifest"]["entries"]
mismatch = []
if manifest:
    for m in manifest:
        idx = m["snapshotIndex"]
        e = lg["entries"][idx - 1]
        if canon(e) != m["entryCanonicalSha256"]:
            mismatch.append(idx)
print("ledger entries:", len(lg["entries"]), "| chain breaks:", bad_chain, "| manifest mismatches:", mismatch)
if bad_chain or mismatch:
    findings.append("ledger chain problem")

# 2) name check derived from source
src = open(dep, encoding="utf-8", errors="replace").read()
names = re.findall(r"DUT_API\s+int\s+(TM643\w+)", src)
carrier = os.path.join(A, "acceptance-report.json")
ctext = open(carrier, encoding="utf-8").read()
name_ok = True
for n in names:
    v = n.replace("VBAT", "VAT")
    if ctext.count(v) != 0 or ctext.count(n) < 1:
        name_ok = False
        findings.append("name check failed for %s" % n)
print("source-derived names:", names, "| carrier contains correct/derives-no-variant:", name_ok)

# 3) FROZEN accuracy: the four marked-frozen artifacts must be unchanged since their recorded time
anchors = json.load(open(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"), encoding="utf-8"))
frozen_ok = True
for k, v in anchors["anchors"].items():
    if v.get("writesStopped"):
        cur = rec(os.path.join(A, k)) if os.path.exists(os.path.join(A, k)) else rec(k)
        same = cur["sha256"] == v["sha256"]
        print("  FROZEN %-42s recorded=%s current=%s identical=%s" % (k, v["sha256"][:12], cur["sha256"][:12], same))
        if not same:
            frozen_ok = False
            findings.append("FROZEN marker stale for %s" % k)
print("FROZEN markers accurate:", frozen_ok)

# 4) stale-claim sweep inside the carrier
stale = []
for pat in ("The live workspace payload is 39,457", "2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9 (566 lines)",
            "K109 x1 / K110 x1 executable"):
    hits = ctext.count(pat)
    if hits:
        stale.append((pat[:40], hits))
print("stale-claim hits in carrier:", stale)
if any(h for _, h in stale if "K109 x1" in _):
    findings.append("carrier still asserts the old executable K109/K110 counts")

# 5) pointer sanity: pointers must record that their embedded values are snapshots
ptr = json.load(open(os.path.join(A, "t34-carrier-pointer.json"), encoding="utf-8"))
ptr_note = "snapshot" in json.dumps(ptr).lower() or "recompute" in json.dumps(ptr).lower()
print("pointer warns that recorded values are snapshots:", ptr_note)
if not ptr_note:
    ptr["recordedValuesAreSnapshots"] = "the size/sha256 in this pointer were true at 2026-09-16 22:40:03; the carrier is a live file - recompute before citing"
    json.dump(ptr, open(os.path.join(A, "t34-carrier-pointer.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("  -> pointer note added")

print("\nAUDIT FINDINGS:", findings if findings else "none")
LOG_ENTRY = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "final integrity self-audit of my own artifacts (chain, name derived from source, FROZEN accuracy, stale-claim sweep, pointer sanity)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(open(LOG, "rb").read()), "ledgerSha256BeforeThisWrite": hashlib.sha256(open(LOG, "rb").read()).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "audit": {"chainBreaks": bad_chain, "manifestMismatches": mismatch, "sourceDerivedNameCheckPassed": name_ok,
              "frozenMarkersAccurate": frozen_ok, "staleClaimHits": stale, "findings": findings or ["none"]},
    "artifacts": {"acceptance-report.json": rec(carrier), "gate-logs-t28/setupArchitect-anchors.json": rec(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")),
                  "t34-carrier-pointer.json": rec(os.path.join(A, "t34-carrier-pointer.json")), "scripts/gate_baseline.json": rec("scripts/gate_baseline.json")},
}
LOG_ENTRY["prevEntryCanonicalSha256"] = canon(lg["entries"][-1])
LOG_ENTRY["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon({k: v for k, v in LOG_ENTRY.items() if k != "ledgerSelfProof"})}
lg["entries"].append(LOG_ENTRY)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
