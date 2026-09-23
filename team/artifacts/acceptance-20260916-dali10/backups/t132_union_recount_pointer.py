# -*- coding: utf-8 -*-
"""Recount 'union' occurrences (enumerate then classify) and create the append-only supersession pointer file recommended by t4 ((甲)+pointer)."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
CONTRACT = os.path.join(A, "setup-contract.json")
raw = open(CONTRACT, "rb").read()
text = raw.decode("utf-8")

# raw-byte count vs JSON-value count
raw_hits = [m.start() for m in re.finditer(r"union", text, re.I)]
print("contract:", len(raw), "B /", hashlib.sha256(raw).hexdigest()[:24])
print("raw 'union' occurrences (case-insensitive, raw text):", len(raw_hits))

d = json.loads(text)
classified = []
def walk(node, path):
    if isinstance(node, dict):
        for k, v in node.items():
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
    elif isinstance(node, str) and re.search(r"union", node, re.I):
        n = len(re.findall(r"union", node, re.I))
        classified.append((n, ".".join(path), node[:110].replace("\n", " ")))
    if isinstance(node, dict):
        for k in node.keys():
            if re.search(r"union", str(k), re.I):
                classified.append((1, "KEY:" + ".".join(path + [str(k)]), "key name contains 'union'"))
walk(d, [])
total_values = sum(n for n, _, _ in classified)
print("JSON string values containing 'union':", len(classified), "| total occurrences:", total_values)
for n, p, s in classified:
    print("  x%d %-72s %s" % (n, p[:72], s[:80]))

# append-only supersession pointer file
PTR = os.path.join(A, "gate-logs-t28", "supersession-pointers.json")
entry = {
    "recordedAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "purpose": ("POINTER/RECORD ONLY - this file does not change any contract byte. It records that a specific nested key inside the contract is superseded by its parent's marker, so that a reader who opens the sub-key alone does not mistakenly read it as the operative rule. "
                "Recommended shape: (a) treat the parent SUPERSEDED marker as covering the child, PLUS (b) name the child path here in an append-only file - which invalidates no existing hash and requires no re-anchoring."),
    "pointers": [{
        "artifact": CONTRACT.replace("\\", "/"),
        "artifactSha256AtRecording": hashlib.sha256(raw).hexdigest(),
        "artifactRevisionAtRecording": d.get("revision"),
        "supersededPath": "revision29Bindings.completenessUnderBothReadings.why_the_union_and_not_either_single_form.union_form",
        "supersededValue": d["revision29Bindings"]["completenessUnderBothReadings"]["why_the_union_and_not_either_single_form"]["union_form"],
        "coveredBy": "the parent block revision29Bindings.completenessUnderBothReadings carries SUPERSEDED, and the disposition is the captain's: add K48/K76 and REMOVE K109/K110 on the single channel-5 route",
        "gateImpact": "none - the bst-sw gate reads only aliasResolution[*].resolution.closedRelayNumbers (= [48,60,61,76])",
        "evidenceNote": "my earlier separate observation of the parent-level marker and the child-level text is recorded in t34 L47",
    }],
}
if os.path.exists(PTR):
    doc = json.load(open(PTR, encoding="utf-8"))
    doc.setdefault("entries", []).append(entry)
else:
    doc = {"owner": "setup-architect", "rule": "append-only; records point at superseded nested keys without touching the referenced artifact", "entries": [entry]}
json.dump(doc, open(PTR, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
pb = open(PTR, "rb").read()
print("\nsupersession pointer file:", len(pb), "B /", hashlib.sha256(pb).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
e = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
     "reason": "recounted the contract's 'union' occurrences (enumerate then classify) and created the append-only supersession pointer file per t4's (甲)+pointer recommendation",
     "contractRevision": d.get("revision"),
     "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
     "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
     "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
     "unionRecount": {"rawTextOccurrences": len(raw_hits), "stringValuesContainingUnion": len(classified), "totalInValues": total_values,
                      "classifiedPaths": [p for _, p, _ in classified]},
     "artifacts": {"setup-contract.json": {"path": CONTRACT.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest(),
                                            "measuredAt": datetime.datetime.fromtimestamp(os.stat(CONTRACT).st_mtime).strftime("%Y-%m-%d %H:%M:%S")},
                   "gate-logs-t28/supersession-pointers.json": {"path": PTR.replace("\\", "/"), "sizeBytes": len(pb), "sha256": hashlib.sha256(pb).hexdigest()}}}
e["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(e)}
lg["entries"].append(e)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
