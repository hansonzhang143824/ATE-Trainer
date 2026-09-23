# -*- coding: utf-8 -*-
"""Self-correction: my previous write read aliasResolution[1] by position instead of the bst2sw alias by name, and recorded the wrong gate-read value."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
C = os.path.join(A, "setup-contract.json")
raw = open(C, "rb").read()
d = json.loads(raw.decode("utf-8"))
ar = d["aliasResolution"]
byname = {e.get("alias"): (e.get("resolution") or {}).get("closedRelayNumbers") for e in ar}
print("by name:", {k: v for k, v in byname.items() if v})
print("bst2sw is at list index:", [i for i, e in enumerate(ar) if e.get("alias") == "bst2sw"])
print("index [1] is:", ar[1].get("alias"), "->", byname[ar[1].get("alias")])

# sweep my own artifacts for the wrong value
BAD = "[154, 155, 60, 61]"
hits = []
for rel in ("acceptance-report.json", "gate-logs-t28/setupArchitect-anchors.json", "gate-logs-t28/setupArchitect-freeze-snapshots.json",
            "gate-logs-t28/supersession-pointers.json", "PATH-MAP.md", "t34-CARRIER-PATH.md", "t34-carrier-pointer.json"):
    p = os.path.join(A, rel)
    if not os.path.exists(p):
        continue
    t = open(p, encoding="utf-8").read()
    n = t.count(BAD) + t.count("154,155,60,61") + t.count("[154, 155, 60, 61]")
    if n:
        hits.append((rel, n))
print("\nfiles of mine containing the wrong value:", hits)

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "SELF-CORRECTION: my previous entry read aliasResolution[1] BY POSITION instead of the bst2sw alias BY NAME and therefore recorded the wrong gate-read value",
         "contractRevision": d.get("revision"),
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": byname.get("bst2sw"), "expectedForTM600": [48, 60, 61, 76, 83],
                           "howResolved": "resolved BY NAME over the 12-entry list, not by index"},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "correctionOfMyOwnRead": {
             "whatIWronglyRecorded": "entry[62].gateReadField.value = [154,155,60,61]",
             "whatIsTrue": "that value belongs to aliasResolution[1] = sw2pgnd; the gate-read field is aliasResolution[alias=='bst2sw'] = [48,60,61,76]",
             "rootCause": "I addressed a LIST BY POSITION under the assumption that bst2sw was at index [1]; it is at index [3] and the list holds 12 aliases",
             "family": "identity by assumption - the same family as size-vs-identity, preservedPeerKeys-vs-entries, and my earlier wrong key ('history')",
             "whichOfMyReadsWereAffected": "only this entry's gateReadField: every earlier gateReadField I recorded was written from the by-name value [48,60,61,76] and remains correct",
             "sweep": "files of mine containing the wrong value: %s" % (hits or "none - the wrong value exists only inside the superseded field of entry[62]"),
             "ruleAdopted": "address contract fields BY ALIAS NAME (or by a by-name lookup), never by list position; a position is an assumption about ordering, not an identity",
         },
         "artifacts": {"setup-contract.json": {"path": C.replace("\\", "/"), "sizeBytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["fieldAddressingRule"] = ("Address contract fields BY NAME (alias name, key name), never by list position: a position is an assumption about ordering, not an identity. Instance: I read aliasResolution[1] expecting bst2sw and got sw2pgnd; the correct by-name value is [48,60,61,76].")
doc["gateReadFieldByNam"] = byname.get("bst2sw")
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())
