# -*- coding: utf-8 -*-
"""Group the sibling evidence rules into one 'evidence strength' register and give byteDeltaCrossCheck its usage rule (both suggested by rule-reviewer)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

present = {k: (k in doc) for k in ("nameFactRule", "identityRule", "granularityRule", "scopeRule", "structuralVerificationRule", "certaintyTieringPattern")}
print("rules present in the anchors file:", present)

REG = {
    "name": "evidence strength register (grouping suggested by rule-reviewer; canonical criterion sentence mine)",
    "canonicalCriterion": "An assertion that carries its derivation is reproducible by any third party; an assertion that carries a quotation is only as strong as the quoted text.",
    "whyItIsATheoremNotAProhibition": ("'Do not copy names' is a prohibition someone must remember. The sentence above is a STRENGTH THEOREM: the evidentiary strength of a quotation equals the strength of the quoted text, so it implies WHY derivation is required - an assertion not reproducible by a third party rests on somebody's credibility. "
                                      "Empirical attribution: all four misspelling reminders in this run came from quoting rather than deriving."),
    "members": [
        {"rule": "nameFactRule", "oneLiner": "name-class facts are derived from a source and asserted, never copied from a message or memory", "locator": "this file: nameFactRule"},
        {"rule": "hashOnCitation", "oneLiner": "hashes are recomputed at citation time, never carried over"},
        {"rule": "countsCarryDomain", "oneLiner": "a count is meaningless without its domain or unit"},
        {"rule": "lineNumbersAreNotIdentity", "oneLiner": "line-number locators are not an identity for content"},
        {"rule": "scopeRule", "oneLiner": "whole-tree or non-existence claims state their scan scope, including sub-directories", "locator": "this file: scopeRule"},
        {"rule": "byteDeltaCrossCheck", "oneLiner": "when an edit claims a character-level change and the byte delta is recomputable, prefer the byte delta as corroboration", "locator": "this file: byteDeltaCrossCheck"},
    ],
    "reviewerInstance": "rule-reviewer applied the same shape when it measured the number of citations of its own t57 before editing it - a derived assertion any third party can reproduce with one command",
}
doc["evidenceStrengthRegister"] = REG

bdc = doc.get("byteDeltaCrossCheck") or {}
bdc["usageRule"] = ("Whenever an edit claims 'changed N characters' or 'changed one place', and the file's byte delta is recomputable, use the delta as corroboration: it is stronger than a self-report, and weaker than a direct source comparison. "
                    "Instance: 68,163 -> 68,164 B for inserting one 'V'.")
doc["byteDeltaCrossCheck"] = bdc
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "one write covering two suggestions: the evidence-strength register (with my criterion sentence adopted as canonical) and the byte-delta usage rule",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "evidenceStrengthRegister": REG,
         "pendingItemClosed": "the criterion sentence the reviewer adopted as canonical is now recorded with its group, in one write rather than two",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
