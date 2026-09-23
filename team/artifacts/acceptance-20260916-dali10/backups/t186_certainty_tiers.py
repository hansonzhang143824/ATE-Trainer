# -*- coding: utf-8 -*-
"""Promote the three-tier certainty pattern (proven / approximate / measured) to a reusable, named form, with its existing instances."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
PATTERN = {
    "name": "certainty tiering: proven / approximate / measured (recommended form, promoted by rule-reviewer)",
    "statement": ("State the same fact in three separately-graded tiers instead of one blanket caveat: what is PROVEN (with its evidence), what is APPROXIMATE (with its interval and why it cannot be exact), and what is MEASURED (the current, recomputable reading). "
                  "This is stronger than a single 'residual caveat' because a caveat only flags that evidence is limited, whereas tiering says how certain each layer is."),
    "whenToUse": "any claim whose certainty differs between layers - a loss whose existence is proven but whose magnitude is not, an attribution supported by self-report plus interval compatibility, a value read at one moment and quoted later",
    "instances": [
        {"where": "ledger entry[32].namespaceLossPrecision (and the anchors field of the same name)",
         "proven": "a collapse occurred - evidenced by the owner's own fix script (gate-logs-t54/t54_fix_preservation_union.py, 4,012 B / 915f989e...)",
         "approximate": "how many entries were lost - the owner wrote '6~8', because the exact count was never captured; must not be quoted as exactly 8",
         "measured": "the preserved content is exactly one entry - measured independently by both sides"},
        {"where": "t34 L48 (the rev-32 attribution caveat)",
         "proven": "nothing beyond the log's self-report",
         "approximate": "the gate's input was rev 32 - supported only by the log's self-report plus interval compatibility (rev=32 falls inside (rev28, current])",
         "measured": "the current contract revision and the channel-5 expectation are measured, but the rev-32 bytes no longer exist and cannot be examined",
         "note": "this instance shows the pattern also serves to say that one tier is EMPTY - 'no byte-level proof exists' becomes explicit rather than implied"},
    ],
    "whyItPropagates": "the same three tiers already appear, unnamed, in the rev-32 caveat and in the namespace precision block; naming the pattern lets either be cited and reproduced without restating the reasoning",
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "promoted the three-tier certainty pattern to a named reusable form at the reviewer's recommendation, with both existing instances",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "certaintyTieringPattern": PATTERN,
         "noteOnMyCarrier": "t34's L48 already reads in two tiers (self-report plus interval compatibility) and distinguishes what is measured; if the carrier is next written for another reason, L48 can be re-expressed in the three named tiers. No write is made for that alone.",
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "gate-logs-t54/t54_fix_preservation_union.py": {"path": os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py").replace("\\", "/"),
                                                                       "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py")),
                                                                       "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["certaintyTieringPattern"] = PATTERN
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

# verify the owner's fix script hash matches what both sides recorded
fxp = os.path.join(A, "gate-logs-t54", "t54_fix_preservation_union.py")
print("owner fix script:", os.path.getsize(fxp), "B /", hashlib.sha256(open(fxp, "rb").read()).hexdigest())
