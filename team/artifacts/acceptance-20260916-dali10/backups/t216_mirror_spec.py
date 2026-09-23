# -*- coding: utf-8 -*-
"""Name the mirror-record identity spec (per t4's suggestion) and register it; the field itself belongs to the owner."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

SPEC = {
    "name": "mirrorRecordIdentitySpec (named so later parties can cite it; relayed from schematic-expert via test-strategy-architect)",
    "statement": ("A record that points at another party's live file may hard-code ONLY wayfinding facts - path, owner, permission and version requirements. The target's MEASUREMENTS (size, hash) must not be hard-coded without declaring them a snapshot of a moment. "
                  "Identity, when needed, is answered by a content hash taken AT the mirroring moment (`mirroredContentSha256` + `mirroredAt`), which never expires because it names a revision rather than a current state; any recorded measurement carries an expiry note."),
    "evidenceThatSizeCannotIdentify": ("four measurements of the same recorded value `mirrorSize = 97,636` against its target gave errors -2,775, +42,516, +54,861 and +61,730 - the error CHANGES SIGN, so on an append-only target the value is neither an upper nor a lower bound and cannot support even 'at least / at most'. "
                                       "This is not an accuracy problem but a structural failure as a comparison basis. It matches the run's earlier 'same size, three different hashes' finding."),
    "whyContentHashAndNotSize": "size cannot identify content (the same size recurred with three different hashes in this run), whereas a content hash names a specific revision and therefore never expires",
    "minimalForm": {"add": ["mirroredContentSha256 = <hash of the mirrored content at mirror time>", "mirroredAt = <timestamp>"],
                    "keep": "the existing size field, with an in-place note: 'mirror-time value; must be recomputed (error changes sign)'",
                    "never": "delete the original value - the R1 convention still applies"},
    "ownerStatus": ("the owner had ALREADY remediated the field further than this minimal form: it is now `mirrorSizeAtMirrorTime` (time baked into the name) with `mirrorSizeNote: 'value expires; recompute'` and `mirrorAt`. "
                    "The one element still missing there is the content hash, which I forwarded to the owner as an addition."),
    "mySideStatus": "my artifacts hold no mirror record of another party's size: all occurrences of that field name in my files are references to the owner's field, inside my snapshot-value convention and audit records",
}

doc["mirrorRecordIdentitySpec"] = SPEC
reg = doc.get("knownSpecsRegister") or {}
inst = reg.get("instances") or []
if "mirrorRecordIdentitySpec" not in inst:
    inst.append("mirrorRecordIdentitySpec")
reg["instances"] = inst
doc["knownSpecsRegister"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
print("spec register:", inst)

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "named and registered the mirror-record identity spec; verified that my own artifacts hold no mirror-size record of a peer file; forwarded the content-hash addition to the owner",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "mirrorRecordIdentitySpec": SPEC,
         "mySideEvidence": "all 16 occurrences of the field name across my anchors file, ledger and carrier are references to the owner's field (inside the snapshot-value convention and audit records), not records of a peer file's size; the earlier audit also found zero peer-size records lacking a timestamp",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
