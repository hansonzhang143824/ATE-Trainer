# -*- coding: utf-8 -*-
"""Record a wayfinding pointer (names only, no paraphrase) to the rules whose authoritative carrier is the plan-side note."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

PEER = {
    "name": "peer rule registry (wayfinding pointer only - names, no paraphrased content)",
    "carrier": "review-handoff-note-plan-side.md, owned by test-strategy-architect (the note's own section listing its authoritative rules)",
    "rule": ("Rules that a peer has NAMED are cited BY NAME from their carrier; this file records only WHERE they live, never a second wording. The per-rule single-authoritative-carrier principle exists because two wordings drift independently, "
             "and copying a rule is not reinforcement but an extra object that must be kept true."),
    "names": ["macro expansion rather than token search", "strip method", "enumerate then classify", "four carrier forms (including the imperative sub-key)",
              "locator stability plus the claim-absence criterion", "review then report", "attribution must be measured", "in-band annotation criterion",
              "citation stability", "a criterion must carry its command and expected output", "count citations before touching", "deploy byte copies",
              "annotate only, never rearrange", "wayfinding versus measurement plus the third class (deliberate record)",
              "zero-spill two-part statement", "a checker carries its own projectionSpec", "ordinal identity",
              "trade-offs about one's own measurements", "the three-layer query discipline: name, read path, filtered view"],
    "note": "this list is deliberately names-only; any reader who needs the content reads the carrier and recomputes it there",
    "declinedDuplication": "I offered to add a second copy of one of these rules on my side; the peer declined, because requesting the copy is itself what produces the drift the principle guards against - recorded so the decision is not re-litigated",
}

doc["peerRuleRegistry"] = PEER
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "recorded a wayfinding pointer to the peer's authoritative rules (names only) and the declined-duplication decision",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "peerRuleRegistry": PEER,
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
