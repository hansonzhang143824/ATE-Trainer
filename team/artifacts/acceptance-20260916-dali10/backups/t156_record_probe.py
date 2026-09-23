# -*- coding: utf-8 -*-
"""Record the independent reproduction of the owner's union probe (category (ii))."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

PROBE = {
    "claim": "category (ii): the current generator does not lose the content present at run time (union accumulation)",
    "how": ("I copied the owner's generator VERBATIM to my own scratch (backups/probe-union/t28_make_anchors_offline.py, %d B / %s), patched EXACTLY TWO lines - the workspace root (line 15) and the output path (line 103), both marked 'PATCHED FOR OFFLINE PROBE' - "
            "built an OFFLINE copy of the shared file with three foreign-prefix entries injected (namespace 'qaProbeAnchors'), ran the patched generator once, and recomputed." % (
                11263, "22ebfec070219ec1d75f8f8ebc89ac6b935425b4492f66ae24d48c79f2be76d9")),
    "result": {"probeEntriesBefore": 3, "probeEntriesAfter": 3, "foreignEntriesBefore": 1, "foreignEntriesAfter": 1,
               "namespacesKept": ["qaProbeAnchors", "setupArchitectFreezeAnchors"], "verdict": "REPRODUCED - no loss of current content"},
    "whyForeignPrefix": "'setupArchitect-' is inside DO_NOT_TOUCH_PREFIXES and therefore takes the pass-through path; the union branch is only exercised by a foreign prefix (design correction raised by rule-reviewer)",
    "liveFileUntouched": "the shared file was re-measured after the probe: 11,941 B / 89b41cf7cab4594ae9d81ab6838607835f4465cf3b0074d505e3f82c79b65ceb, and it contains no probe markers - the probe ran entirely on my offline copy",
    "prohibitedInference": "this evidences (ii) only; it must never be cited for (iii) recovery - the earlier eight entries have no byte copy, so restoration is untestable in principle",
    "limitation": "the probe uses my copy of their generator with two patched lines; the union logic itself is unmodified. Running their script as-is would have written to their live artifact, which is why the copy was made.",
    "ownerSideEvidence": "their own run and evidence files were verified too: gate-logs-t54/t54_prefix_and_union_experiment.py (3,248 B) and t54-prefix-union-experiment.log (743 B) record injection -> 4 entries -> re-run -> 4 entries with all three sentinels present",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "independent reproduction of the union probe: category (ii) holds, on my own offline copy, without touching the shared live file",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "unionProbeReproduction": PROBE,
         "prefixGuardAdopted": "the owner extended DO_NOT_TOUCH_PREFIXES to ('setupArchitect-','t34-carrier','t34-CARRIER') (generator 11,028 B / e6d09e1f894cc30526eb29537d14daa2a9fb88ed83048cace3c6a1d302e06cd2), so their generator writes none of my four files",
         "artifacts": {"gate-logs-t28/t28_make_anchors.py": rec(os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")),
                       "gate-logs-t28/t28-anchors.json": rec(os.path.join(A, "gate-logs-t28", "t28-anchors.json")),
                       "backups/probe-union/t28_make_anchors_offline.py": rec(os.path.join(A, "backups", "probe-union", "t28_make_anchors_offline.py")),
                       "launcher": rec(os.path.join(A, "backups", "t154_probe_union.py"))}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["unionProbeReproduction"] = PROBE
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
