# -*- coding: utf-8 -*-
"""Upgrade the deferred-items register to the reviewer's three-sentence form (carrier + explicit fallback)."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))

reg = doc.get("deferredItemsRegister") or {}
reg["threeSentenceProtocol"] = {
    "form": [
        "1. adopt the item but do not write it this round",
        "2. name WHOSE carrier holds it temporarily, including where it will be folded in",
        "3. state the FALLBACK explicitly: if no natural write occurs before the run ends, the carrier remains where it is and that is not a loss",
    ],
    "criterion": "a deferral is acceptable only when the carrier AND the fallback are both specified; with only the first half, a deferral becomes a loss",
    "why": ("the only failure mode of the temporarily-held-elsewhere form is both sides assuming the other has it; naming the carrier removes one half of that risk and stating the fallback removes the other, so the optimisation 'one fewer write is one fewer drift' no longer risks losing the rule"),
    "raisedBy": "rule-reviewer, who formalised the protocol after I added the fallback sentence",
}
reg["fallbackForAllItems"] = ("For every item above: the named carrier keeps the rule until the fold-in happens. If the run ends first, that carrier is still the record and the item is NOT considered lost - a deferred rule is never silently dropped, only relocated.")
reg["myRule"] = ("No deferral without a named carrier; when folding an item in, state which carrier held it until then; and state the fallback (where the rule lives if the fold-in never happens).")
doc["deferredItemsRegister"] = reg
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "upgraded the deferred-items register to the reviewer's three-sentence protocol (adopt-but-don't-write; named carrier; explicit fallback)",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "threeSentenceProtocol": reg["threeSentenceProtocol"],
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
