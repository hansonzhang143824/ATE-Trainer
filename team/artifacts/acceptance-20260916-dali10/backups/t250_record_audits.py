# -*- coding: utf-8 -*-
"""Record my own addressing self-audit and the peer's independent audit, with the discriminative-power nuance."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

fa = doc.get("fieldAddressingRule") or {}
fa["selfAudit"] = {
    "scope": "870 python files under the workspace (excluding .git and node_modules)",
    "patterns": ["aliasResolution[<digit>]", "entries[<digit>]", "(resolutions|anchors|limitations|aliases)[<digit>]"],
    "results": {"contractPosition": 20, "ledgerPosition": 14, "genericListPosition": 0},
    "classification": ("no hit lies in an ACTIVE gate or verification script. The contract-position hits are my own backup/patch scripts plus one hit inside the owner's own audit script (its regex, i.e. a self-reference). The ledger-position hits are documentation scripts of mine that quote the numbering problem, plus an unrelated `entries[0]` in scripts/gen_cbit_defines.py which addresses a different structure. "
                      "Some of my historical patch scripts did use aliasResolution[3] - see the nuance below."),
    "nuanceThatMakesTheRuleNecessary": ("position addressing can be ACCIDENTALLY CORRECT: bst2sw happens to sit at index 3, so my older scripts addressing aliasResolution[3] were right, while my erroneous read used [1] and got sw2pgnd. A practice whose correctness depends on the current ordering is not a determination - which is precisely the hazard the rule names."),
}
fa["peerAudit"] = {
    "owner": "compile-diagnostician",
    "result": "their active directories show one contract-position occurrence, and it is their own audit script's regex; their 12 backups hits are other parties' historical scripts",
    "perScript": "three of their gate-field scripts address the field by name (position = False); one does not read the field directly because it goes through the gate function",
    "discriminativePower": ("measured with data: aliasResolution holds 12 entries; bst2sw is at index 3; by name the value is [48,60,61,76]; by position [1] it is sw2pgnd [154,155,60,61] - the two differ, so the rule has real discriminative power in this run"),
}
doc["fieldAddressingRule"] = fa
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "applied fieldAddressingRule to my own scripts and recorded the peer's independent audit plus the accidentally-correct-position nuance",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "addressingSelfAudit": fa["selfAudit"],
         "peerAudit": fa["peerAudit"],
         "auditScript": "backups/t248_selfaudit_addressing.py (mine, written for this check; offered to the peer for reuse)",
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "backups/t248_selfaudit_addressing.py": {"path": os.path.join(A, "backups", "t248_selfaudit_addressing.py").replace("\\", "/"),
                                                                "sizeBytes": os.path.getsize(os.path.join(A, "backups", "t248_selfaudit_addressing.py")),
                                                                "sha256": hashlib.sha256(open(os.path.join(A, "backups", "t248_selfaudit_addressing.py"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
