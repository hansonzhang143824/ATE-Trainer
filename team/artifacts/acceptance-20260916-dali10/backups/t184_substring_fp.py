# -*- coding: utf-8 -*-
"""Correct a substring false positive in my own check: the child value contains the token 'superseded' only in a different sense."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
d = json.loads(open(C, encoding="utf-8").read())
v = d["revision29Bindings"]["completenessUnderBothReadings"]["disposition"]
pos = v.upper().find("SUPERSEDED")
print("token position in the child value:", pos, "| length:", len(v))

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "corrected a substring false positive in my own check of the child key (the token 'superseded' occurs there only in a different sense)",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "correctionOfMyOwnCheck": {
             "whatIComputed": "a boolean 'does the child value contain SUPERSEDED or WITHDRAWN' returned True, which would have suggested the child carries its own marker",
             "whatIsTrue": ("the token appears only at character %d of the value and in a DIFFERENT sense: 'downgrading the contract's [110,61] from contested to superseded' - a statement about another field's status, not a marker on this value. The child therefore carries NO self-marker, "
                            "and schematic-expert's analysis stands." % pos),
             "lesson": "presence of a token is not the fact asserted - this is the stale-token criterion applied to my own check; substring matching had to be replaced by semantic classification",
             "impact": "none on the contract or the gate; the correction only removes a wrong supporting observation from my earlier entry",
         },
         "markerCoLocationConfirmed": {"insertionOrder": list(d["revision29Bindings"]["completenessUnderBothReadings"].keys()),
                                       "imperativePosition": list(d["revision29Bindings"]["completenessUnderBothReadings"].keys()).index("disposition") + 1,
                                       "siblingMarkerPosition": list(d["revision29Bindings"]["completenessUnderBothReadings"].keys()).index("SUPERSEDED") + 1,
                                       "sortedOrderPutsMarkerFirst": sorted(d["revision29Bindings"]["completenessUnderBothReadings"].keys())[0] == "SUPERSEDED",
                                       "parentMarkerPresent": bool(d["revision29Bindings"].get("SUPERSEDED"))},
         "artifacts": {"setup-contract.json": {"path": C.replace("\\", "/"), "sizeBytes": os.path.getsize(C), "sha256": hashlib.sha256(open(C, "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
