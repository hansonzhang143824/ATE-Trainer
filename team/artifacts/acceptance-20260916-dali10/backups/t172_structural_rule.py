# -*- coding: utf-8 -*-
"""Adopt the structural-verification rule (adjacent is not belongs) and the stale-token criterion; log the reviewer's structured re-verification."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
RULES = {
    "structuralVerificationRule": {
        "name": "verify annotations structurally, not by proximity (companion practice to R2(vi); proposed by rule-reviewer, adopted here)",
        "statement": "Any check of an annotation or companion field must be decided by STRUCTURE - which key owns it, which keys are its siblings - and never by TEXT PROXIMITY. 'Adjacent' is not 'belongs'.",
        "family": "same family as 'a filename string is not file existence' and 'a key is not an entry'",
        "instanceTruePositive": ("my first sweep looked for annotation words inside a text window and produced a false positive on coverage[9]; the switch to a structural walk (require the sibling key to exist) both removed the false positive AND is what surfaced the genuine stale assertion in coverage[9]. "
                                 "So the same check demonstrates the method works and that it catches real problems."),
        "evidence": "rule-reviewer independently re-ran the structural check: coverage has 12 items; exactly [2] and [9] carry artifactSha256IsHistorical: true, both with currentCanonicalArtifact.sha256 = 66abc088ae6bd5f9... (the canonical payload)",
    },
    "staleTokenCriterion": {
        "name": "the defect criterion for stale tokens (stated by rule-reviewer, adopted here)",
        "statement": "The defect is AN ASSERTION left in present-tense terms, not the mere PRESENCE of an old token. An old token is compliant when its context marks it as history, correction or withdrawal.",
        "workedCheck": ("old tokens in the carrier and their contexts: '39,457' appears 4 times - once inside a version-chain sentence (35,014 -> 36,381 -> 38,147 -> 39,457, a historical evolution) and three times already marked superseded/CORRECTED; '2d0984d9' appears 6 times - two unlabelled, one a historical fact statement ('was never applied') and one the value of coverage[2].artifactSha256 whose label is a SIBLING key; "
                        "'K109 x1' appears 4 times, all inside 'previously stated, now withdrawn' text. Conclusion: no present-tense assertion of an old value remains."),
        "why": "counting tokens over-reports; the criterion must be applied per occurrence, which mirrors the run's enumerate-then-classify rule",
    },
}

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "adopted the structural-verification rule and the stale-token criterion; reviewer independently reconfirmed the coverage[2]/[9] labelling",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "rules": RULES,
         "legacyEntriesDecision": "confirmed: do NOT back-fill a kind field into entries 1-6. Documenting the alternative (schema.legacyEntries + classification in later entries + hash freeze in the chain manifest) is preferable because back-filling would itself be a write to historical entries.",
         "artifacts": {"acceptance-report.json": {"path": os.path.join(A, "acceptance-report.json").replace("\\", "/"),
                                                  "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                                  "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest()},
                       "scripts/gate_baseline.json": {"path": "scripts/gate_baseline.json", "sizeBytes": os.path.getsize("scripts/gate_baseline.json"),
                                                      "sha256": hashlib.sha256(open("scripts/gate_baseline.json", "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["structuralVerificationRule"] = RULES["structuralVerificationRule"]
doc["staleTokenCriterion"] = RULES["staleTokenCriterion"]
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
