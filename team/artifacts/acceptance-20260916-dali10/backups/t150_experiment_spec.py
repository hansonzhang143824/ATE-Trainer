# -*- coding: utf-8 -*-
"""Record the corrected design of the control experiment (foreign prefix required) and log it."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
SPEC = {
    "purpose": "turn category (ii) - 'the current generator does not lose current content' - from the owner's self-statement into a reproducible positive result",
    "designCorrection": ("the injected peer entries MUST use a prefix OTHER than 'setupArchitect-'. Reason (raised by rule-reviewer): 'setupArchitect-' sits inside DO_NOT_TOUCH_PREFIXES and therefore takes the pass-through preservation path, "
                         "so an experiment conducted inside my own namespace would never execute the union-accumulation branch. A foreign prefix (e.g. 'qaProbeAnchors') is what exercises the code path under test."),
    "steps": [
        "take an OFFLINE copy of gate-logs-t28/t28-anchors.json (never the live shared file)",
        "inject 3 entries under a foreign namespace, e.g. qaProbeAnchors.anchors = {a,b,c}, keeping the existing setupArchitectFreezeAnchors in place",
        "run the generator once against that offline copy",
        "recompute: qaProbeAnchors.anchors should still contain all 3 entries (union accumulation), and setupArchitectFreezeAnchors should still be present",
    ],
    "optionalStrongerVariant": "inject exactly ONE entry under the probe namespace and re-run: it must survive (this is the direct contrast with the old collapse-to-one behaviour, i.e. it shows the old bug would not recur)",
    "expectedOutcome": "3 of 3 probe entries preserved plus my namespace preserved (or 1 of 1 for the variant)",
    "prohibitedInference": "this can only evidence category (ii) - no loss of current content. It must NEVER be cited as evidence for category (iii) recovery: the earlier eight entries have no byte copy, so restoration is untestable in principle.",
    "cost": "one offline run by the owner plus one recomputation by each side",
    "status": "design fixed here; execution is the owner's (compile-diagnostician); relayed at the reviewer's authorisation",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "the reviewer authorised the control experiment and corrected its design (foreign prefix required to reach the union-accumulation branch); spec recorded and relayed to the owner",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "controlExperimentSpec": SPEC,
         "classificationAccepted": "(i) old loss irreversible; (ii) new mechanism conservative for the current input; (iii) no restoration capability - the reviewer withdrew the two-way reading as inaccurate",
         "descriptiveTextStaleness": "the peer's anchor description still says '(rev 24)' while the contract is rev 39 - same family as R2: descriptive text and revision fields can lag the content, so the only identity is the recomputed hash",
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "gate-logs-t28/t28-anchors.json": {"path": os.path.join(A, "gate-logs-t28", "t28-anchors.json").replace("\\", "/"),
                                                          "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t28", "t28-anchors.json")),
                                                          "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t28", "t28-anchors.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["controlExperimentSpec"] = SPEC
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
