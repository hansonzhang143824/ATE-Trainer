# -*- coding: utf-8 -*-
"""Structure-based verification that every old-hash site is labelled historical; log the audit outcome."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
f = os.path.join(A, "acceptance-report.json")
d = json.load(open(f, encoding="utf-8"))
OLD = "2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9"

unlabeled = []
def walk(node, path):
    if isinstance(node, dict):
        if node.get("artifactSha256") == OLD:
            ok = bool(node.get("artifactSha256IsHistorical")) and isinstance(node.get("currentCanonicalArtifact"), dict)
            print("  %-24s labelled=%s (currentCanonical=%s)" % (".".join(path), ok, node.get("currentCanonicalArtifact", {}).get("sha256", "")[:12]))
            if not ok:
                unlabeled.append(".".join(path))
        for k, v in node.items():
            walk(v, path + [str(k)])
    elif isinstance(node, list):
        for i, v in enumerate(node):
            walk(v, path + ["[%d]" % i])
walk(d, [])
print("structure-based check: unlabeled old-hash sites =", unlabeled)

# assertions of the old executable counts (must only survive inside withdrawal/history text)
bad = []
for i, x in enumerate(d["limitations"]):
    if "K109 x1 / K110 x1 executable" in x and not any(k in x for k in ("WITHDRAWN", "older revision", "earlier statement", "previously asserted")):
        bad.append(("limitations[%d]" % i, x[:120]))
for i, c in enumerate(d.get("coverage", [])):
    ev = c.get("evidence", "") if isinstance(c, dict) else ""
    if "K109 x1 / K110 x1 executable" in ev and not any(k in ev for k in ("WITHDRAWN", "older revision", "earlier statement", "previously asserted", "CURRENT canonical")):
        bad.append(("coverage[%d].evidence" % i, ev[:120]))
print("unqualified assertions of the old counts:", bad)

b = open(f, "rb").read()
print("\nt34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S"))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "final integrity self-audit found and fixed a genuine stale assertion in my own deliverable; verification switched from text-window matching to structure-based checking",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "auditResult": {
        "found": ["coverage[9].evidence still asserted the older payload revision as current (39,457 B / 2d0984d9... with executable K109/K110 = 1) - replaced in place",
                  "coverage[2].artifactSha256 and coverage[9].artifactSha256 carried the superseded hash without a historical label - both now labelled with currentCanonicalArtifact alongside"],
        "fixed": True,
        "methodNote": "my first sweep used a text window and produced one false positive (the label sits in a sibling key, outside the window); the check is now structure-based (walk the JSON and require sibling labels), which is the same lesson as the rest of this run: verify structure, not proximity",
        "structureBasedCheck": {"unlabeledOldHashSites": unlabeled, "unqualifiedOldCountAssertions": [x[0] for x in bad]},
    },
    "artifacts": {"acceptance-report.json": {"path": f.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
                                              "measuredAt": datetime.datetime.fromtimestamp(os.stat(f).st_mtime).strftime("%Y-%m-%d %H:%M:%S")},
                  "scripts/gate_baseline.json": {"path": "scripts/gate_baseline.json", "sizeBytes": os.path.getsize("scripts/gate_baseline.json"),
                                                  "sha256": hashlib.sha256(open("scripts/gate_baseline.json", "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
