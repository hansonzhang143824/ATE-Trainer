# -*- coding: utf-8 -*-
"""Adopt the name-class fact rule (derive first, then assert) and keep the byte-delta cross-check as an instance."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
RULES = {
    "nameFactRule": {
        "name": "name-class facts: derive first, then assert (proposed by rule-reviewer after independently reproducing my check)",
        "statement": ("Facts of the name class - function, relay, pin, macro names - are always produced by DERIVING them from a source (the deployed source file or the contract) and then ASSERTING against the artefact (hit / no hit). "
                      "Copying a name from a message, from memory, or from another artefact's prose is forbidden."),
        "why": ("an assertion that carries its derivation is reproducible by any third party; an assertion that carries a quoted token is only as good as the quote. This run's four misspelling reminders all traced to quoting rather than deriving."),
        "siblingRules": ["hashes are recomputed on citation", "counts carry their domain", "line-number locators are not cited as identity"],
        "independentReproduction": "rule-reviewer reproduced it without copying any token: derived TM643_VBAT_LOOP_INDICTOR from DUT_API int (TM643_\\w+), generated the variant by replacing VBAT with VAT, and measured 1 hit / 0 variant hits on the carrier - PASS",
    },
    "byteDeltaCrossCheck": {
        "name": "byte-delta cross-check (instance, kept per the reviewer's request)",
        "statement": ("The pre-fix carrier measured 68,163 B and the post-fix carrier 68,164 B - a delta of exactly one byte, which matches inserting the missing 'V' in VAT -> VBAT. "
                      "The increment of the file equals the increment of the edit, so the change is causally consistent without relying on anyone's self-report."),
        "why": "this is byte-level evidence whose granularity matches the claim, i.e. a positive instance inside the same family as R2's granularity rule",
    },
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the name-class fact rule (derive first, then assert) and kept the one-byte causal cross-check as an instance",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "nameFactRules": RULES,
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "gate-logs-t28/setupArchitect-anchors.json": {"path": os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json").replace("\\", "/"),
                                                                     "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")),
                                                                     "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["nameFactRule"] = RULES["nameFactRule"]
doc["byteDeltaCrossCheck"] = RULES["byteDeltaCrossCheck"]
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
