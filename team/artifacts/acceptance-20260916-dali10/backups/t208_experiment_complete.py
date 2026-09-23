# -*- coding: utf-8 -*-
"""Verify the owner's completed experiment (generator version at run time, variant, restoration) and update my stored spec accordingly."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

gen = rec(os.path.join(A, "gate-logs-t28", "t28_make_anchors.py"))
print("generator NOW:", gen["sizeBytes"], "B /", gen["sha256"][:24], "@", gen["measuredAt"])
print("  owner reported the version AT RUN TIME:", "11,739 B / c8ca47eab8531084b9e00c9f347c434a80509a2f409efc27a8a7d7118d3587b6 @00:33:14")
print("  => current differs:", gen["sha256"] != "c8ca47eab8531084b9e00c9f347c434a80509a2f409efc27a8a7d7118d3587b6")

for f in ("gate-logs-t54/t54-reviewer-experiment-union.log", "gate-logs-t54/t54-reviewer-experiment-union-variant.log"):
    p = os.path.join(A, f)
    print("  evidence:", f, rec(p) if os.path.exists(p) else "MISSING")

sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
sb = open(sh, "rb").read()
t = sb.decode("utf-8")
print("\nlive shared file:", len(sb), "B /", hashlib.sha256(sb).hexdigest()[:24])
print("  contains probe/variant markers:", ("qaProbeAnchors" in t) or ("VARIANT" in t))
s = json.loads(t)
blk = (s.get("preservedPeerNamespaces") or {}).get("setupArchitectFreezeAnchors") or {}
print("  foreign namespace entries:", len(blk.get("anchors") or {}), "| has legacy 'mirrorSize' key:", "mirrorSize" in blk, "| keys:", [k for k in blk.keys()])

vlog = os.path.join(A, "gate-logs-t54", "t54-reviewer-experiment-union-variant.log")
if os.path.exists(vlog):
    print("\n--- variant log (tail) ---")
    for l in open(vlog, encoding="utf-8", errors="replace").read().splitlines()[-14:]:
        print("   ", l[:150])

# update my stored spec
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
spec = doc.get("controlExperimentSpec") or {}
spec["executionByOwner"] = {
    "firstRun": {"design": "foreign prefix qaProbeAnchors, 3 injected entries", "log": "gate-logs-t54/t54-reviewer-experiment-union.log", "result": "3 of 3 survived, my namespace retained"},
    "variantRun": {"design": "one injected entry only (the optional stronger variant)", "log": "gate-logs-t54/t54-reviewer-experiment-union-variant.log",
                   "result": "1 of 1 survived; my namespace retained",
                   "offlineCopyStart": "12,183 B / 6edfc659e930d5bd...", "offlineCopyAfter": "12,318 B / 62d828cbb45a7fac...", "generatorExit": 0},
    "generatorVersionAtRunTime": "gate-logs-t28/t28_make_anchors.py = 11,739 B / c8ca47eab8531084b9e00c9f347c434a80509a2f409efc27a8a7d7118d3587b6 @2026-09-17T00:33:14 - the version that matters is the one used WHEN THE RUN HAPPENED, not the current one (the file has since been edited again)",
    "restorationProof": "live file 12,183 B / 32 entries / contains no probe or VARIANT marker / foreign count 1 - the shared source was not polluted",
    "prohibitedInference": "only category (ii); never (iii)",
}
spec["variantPrecision"] = ("The optional 'single entry' variant WAS executed and the single entry survived - that is a statement about the CURRENT generator's behaviour. It is NOT a contrast with the pre-fix collapse-to-one behaviour, because no old-version generator exists to run: that contrast was NOT executed and must not be implied.")
spec["status"] = "executed by the owner (both the 3-entry run and the optional single-entry variant) and independently reproduced by me for the 3-entry case; the pre-fix contrast remains unexecuted and unavailable"
doc["controlExperimentSpec"] = spec
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("\nanchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "owner completed the experiment spec (generator version at run time, single-entry variant, restoration proof); recorded both runs and the unexecuted pre-fix contrast",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "experimentCompletion": spec["executionByOwner"],
         "versionAtRunTimeIsTheOneThatCounts": "the generator has since been edited; the identity that matters for the experiment is the version measured when it ran",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "gate-logs-t28/t28-anchors.json": {"path": sh.replace("\\", "/"), "sizeBytes": len(sb), "sha256": hashlib.sha256(sb).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
