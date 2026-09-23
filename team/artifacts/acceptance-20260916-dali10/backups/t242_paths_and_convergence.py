# -*- coding: utf-8 -*-
"""Answer the reviewer's nested-path request by deep search, and register the third independent-convergence instance."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
lp = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
TARGETS = ["optionalStrongerVariantWithdrawn", "optionalStrongerVariant", "proposer", "variantPrecision"]

def paths(node, path, acc):
    if isinstance(node, dict):
        for k, v in node.items():
            if k in TARGETS:
                acc.append(".".join(path + [k]))
            paths(v, path + [k], acc)
    elif isinstance(node, list):
        for i, v in enumerate(node):
            paths(v, path + ["[%d]" % i], acc)

found = {}
for name, p in (("anchors", ap), ("ledger", lp)):
    doc = json.load(open(p, encoding="utf-8"))
    acc = []
    paths(doc, [], acc)
    found[name] = acc
    print("==", name, "==")
    for a in acc:
        print("   ", a)
    if not acc:
        print("    (none by key walk)")

# text search too, to explain the earlier 0-by-key result
for name, p in (("anchors", ap), ("ledger", lp)):
    t = open(p, encoding="utf-8").read()
    print("%s: text 'optionalStrongerVariantWithdrawn' occurrences = %d | 'WITHDRAWN'/'withdrawn' = %d" % (
        name, t.count("optionalStrongerVariantWithdrawn"), t.lower().count("withdrawn")))

doc = json.load(open(ap, encoding="utf-8"))
doc["independentConvergenceRegister"] = {
    "statement": "Instances where both sides independently established the SAME rule for the same reason on the same day; two independent arrivals are evidence that the mechanism is needed, not merely convenient.",
    "instances": [
        "an append-only snapshot ledger for the authoritative source (each side converged on its own ledger format)",
        "chain self-proof inside the ledger (each side recorded a pre/post anchor or a previous-line hash)",
        "addressing by NAME rather than by position/index - I established fieldAddressingRule after misreading aliasResolution[1]; the reviewer established the same practice as its tenth self-correction after an index mix-up on its own ledger",
    ],
    "criterion": "positions change with appends and reordering; names do not - so contract fields, ledger entries and array elements are addressed by name",
    "raisedBy": "rule-reviewer identified this as the third convergence instance",
}
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("\nanchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

pre = open(lp, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "answered the reviewer's nested-path request and registered the third independent-convergence instance",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "nestedPathsForWithdrawalText": found,
         "independentConvergenceRegister": doc["independentConvergenceRegister"],
         "whyTheKeyWalkAndTextSearchDiffer": "the withdrawal text lives inside a nested object, so a walk restricted to entry top-level keys finds nothing while a text search finds it - the same domain/method distinction the reviewer reported",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(lp, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(lp, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
