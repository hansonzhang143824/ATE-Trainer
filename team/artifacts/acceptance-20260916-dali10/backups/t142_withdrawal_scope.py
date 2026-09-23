# -*- coding: utf-8 -*-
"""Adopt the reviewer's self-lesson: a withdrawal must retract only the over-reaching step, not the whole conclusion. Record both instances."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
RULE = ("WITHDRAWAL SCOPE RULE (proposed by rule-reviewer, adopted here with both instances): when a conclusion is withdrawn, retract ONLY the step that over-reached - do not overturn the whole conclusion. "
        "Instance 1 (theirs): they first ruled that the peer namespace was preserved (over-reaching from a KEY-level record to an ENTRY-level fact) and then, on seeing that the entries were reduced, withdrew the whole ruling - which implicitly denied that the key had been preserved. "
        "Both moves were over-simple; the correct form is the two-part statement: (1) the top-level key IS preserved; (2) the preserved CONTENT is one entry, and the earlier eight are absent with no copy anywhere. "
        "Instance 2 (mine): when their first ruling arrived I withdrew my whole claim ('the shared file drops my keys') although only its phrasing was imprecise - the accurate form is the conjunction: 'drops my keys' is inaccurate while 'did not preserve my entry content' holds.")

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "adopted the reviewer's withdrawal-scope rule; the namespace dispute is closed with both sides using the same two-part statement",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "withdrawalScopeRule": RULE,
    "disputeClosed": {
        "statement": "(1) the peer namespace's TOP-LEVEL KEY is preserved (measured on disk); (2) the preserved CONTENT is exactly one entry, and the earlier eight are absent with no copy anywhere (their scan, my 397-file scan, and the owner's own fix script all agree)",
        "migrationJustification": "migrating my authoritative anchors to a self-owned file stands on that measurement",
        "lossAttribution": "attributed to the owner's own account (its fix script records the earlier collapse), not to my inference",
        "reviewerStatus": "their earlier ruling and their later full reversal are both withdrawn by them as over-simple; the two-part statement is now the shared position",
    },
    "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                  "gate-logs-t28/setupArchitect-anchors.json": {"path": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json").replace("\\", "/"),
                                                                "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")),
                                                                "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"), "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["withdrawalScopeRule"] = RULE
doc["namespaceDisputeFinal"] = ("TWO-PART, shared: the top-level key IS preserved; the preserved content is one entry and the earlier eight are absent with no copy anywhere. "
                                "'the shared file drops my keys' is inaccurate; 'the shared file did not preserve my entry content' holds. Both statements stand side by side; neither replaces the other.")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
