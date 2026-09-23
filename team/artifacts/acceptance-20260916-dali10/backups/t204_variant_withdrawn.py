# -*- coding: utf-8 -*-
"""Record the withdrawal of the optional stronger variant (as the reviewer confirmed) inside the stored experiment spec."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
spec = doc.get("controlExperimentSpec") or {}
print("current optionalStrongerVariant:", str(spec.get("optionalStrongerVariant"))[:200])

spec["optionalStrongerVariantWithdrawn"] = ("WITHDRAWN by its proposer (rule-reviewer) after both the owner and I pointed out that testing the PRE-FIX collapse behaviour would require modifying code or building an old-version generator, i.e. it lies outside a pure offline probe. "
                                            "The pre-fix behaviour is therefore covered only by the owner's own fix script (product-level written evidence) and its output was never snapshotted, so it is not measurable. The original wording of this field is retained above rather than deleted.")
spec["status"] = "executed and independently reproduced; the optional stronger variant is withdrawn as unimplementable within the offline scope"
doc["controlExperimentSpec"] = spec
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "recorded the proposer's withdrawal of the optional stronger variant inside the stored spec (kept the original wording, added the withdrawal)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "evidenceLevel": {
             "categoryII": "third-party reproducible - I copied the owner's generator verbatim to my scratch, patched exactly two lines (workspace root, output path, both marked), left the union logic untouched, ran it on an offline copy and independently obtained 3 -> 3 probe entries and 1 -> 1 foreign entries",
             "categoryIII": "not measurable - the earlier eight entries have no byte copy, so recovery cannot be tested",
             "whyTheCopyWasNecessary": "the owner's generator hardcodes its output to its own live artefact, so running it unchanged would write another member's source",
             "reviewerAdoption": "rule-reviewer adopted this level: 'independent reproduction is the only form that is both independent and executable - stronger than a third party running it on the owner's behalf, and stronger than trusting the owner's log'",
         },
         "withdrawalOfTheOptionalVariant": "the proposer confirmed the withdrawal; nobody is asked to recreate pre-fix behaviour, since that would require an old generator and its output was never snapshotted",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
