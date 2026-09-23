# -*- coding: utf-8 -*-
"""Reviewer has withdrawn their namespace ruling; mark every site in my artifacts whose premise was that ruling, and add the granularity rule."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
PATTERNS = ["drops my keys", "drops peer", "reviewer's empirical finding", "only 1 of 8", "1 of 8"]
hits = {}
for rel in ("acceptance-report.json", "gate-logs-t28/setupArchitect-anchors.json", "gate-logs-t28/setupArchitect-freeze-snapshots.json"):
    p = os.path.join(A, rel)
    t = open(p, encoding="utf-8").read()
    for pat in PATTERNS:
        for m in re.finditer(re.escape(pat), t, re.I):
            hits.setdefault(rel, []).append((pat, t[max(0, m.start() - 120):m.end() + 120].replace("\n", " ")))
for rel, lst in hits.items():
    print("== %s ==" % rel)
    for pat, ctx in lst:
        print("   [%s] %s" % (pat, ctx[:220]))

# marker for the ledger site(s) - append a corrective entry (ledger is append-only)
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {
    "snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
    "reason": "the reviewer has withdrawn their namespace ruling, which was the premise of my entry 5 (my withdrawal of the strong claim); marking that and restating the corrected position",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
    "premiseWithdrawn": {
        "entryAffected": 5,
        "whatItSaid": "entry 5 recorded my withdrawal of the claim 'the shared anchors file drops my keys', on the basis of the reviewer's finding that preservedPeerKeys showed the namespace present",
        "statusNow": ("the reviewer has WITHDRAWN that finding: preservedPeerKeys evidences the KEY being preserved, not the ENTRIES inside it. Measured: the namespace sub-keys are ['anchors','ledgerNote','mirrorOf','mirrorSize'] and anchors holds exactly ONE entry. "
                      "Entry 5 is therefore historical with a withdrawn premise; the corrected position is the two-part statement in entry 15 - keys preserved / content reduced to one entry and unrecoverable - and my migration to a self-owned anchors file stands on that measurement."),
        "ruleAdopted": "granularity rule: when citing a record as evidence, check that the record's granularity covers the fact being asserted (a key-level record cannot support an entry-level claim). Same family as: revision present but content changed; size equal but version different; mtime present but no ordering; a log self-reporting rev=32 while its content was already ch5."},
    "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

# anchors: add the granularity rule next to scopeRule
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["granularityRule"] = ("When citing a record as evidence, verify that the record's granularity covers the fact you assert. A key-level record (e.g. preservedPeerKeys) cannot support an entry-level claim; a revision string cannot support a content claim; "
                          "an equal size cannot support identity; an mtime cannot support ordering. Counterparties in this run have both made and withdrawn such inferences, so the rule applies symmetrically.")
doc["namespaceDisputeFinal"] = ("FINAL, both sides: the shared file preserves the peer namespace KEY but its anchors map holds ONE entry; the earlier eight entries are not present and are unrecoverable (no byte copy anywhere). "
                                "My migration to a self-owned anchors file rests on that measurement; the earlier 'the shared file drops my keys' phrasing is imprecise and the reviewer's counter-ruling is withdrawn.")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B /", hashlib.sha256(open(ap, "rb").read()).hexdigest())
