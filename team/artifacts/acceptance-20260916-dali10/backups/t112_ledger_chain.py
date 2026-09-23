# -*- coding: utf-8 -*-
"""Ledger hardening per the reviewer: document the legacy-entry approach in schema.rule, and start a verifiable hash chain (prev entry canonical sha) with a manifest for existing entries."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read()
lg = json.loads(pre.decode("utf-8"))

def canon(entry):
    return hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()

# 1) document the legacy-entry approach (append-only: we do NOT rewrite entries 1-6)
lg["schema"]["legacyEntries"] = {
    "entriesWithoutKindField": list(range(1, 7)),
    "policy": ("Entries 1-6 predate the schema declaration and therefore carry no 'kind' field. They are NOT rewritten (this file is append-only). Instead: the entries that carried no value set are classified in later full entries "
               "(idx2-5 in entry[7], idx6 in entry[8]); and their canonical JSON hashes are frozen in the chainManifest of entry[%d]. This is the documented alternative to back-filling metadata into historical entries." % (len(lg["entries"]) + 1)),
}
lg["schema"]["rule"] = (lg["schema"]["rule"] + " NOTE: a value-less entry must self-declare kind='tick'; for entries written before the schema existed, the documentation alternative recorded in schema.legacyEntries applies (classification in a later entry + hash freeze), not retroactive editing.")

# 2) freeze the canonical hashes of all existing entries, and build a forward chain
manifest = [{"snapshotIndex": e.get("snapshotIndex"), "takenAt": e.get("takenAt"), "kind": e.get("kind"), "entryCanonicalSha256": canon(e)} for e in lg["entries"]]
prev = manifest[-1]["entryCanonicalSha256"] if manifest else None

entry = {
    "snapshotIndex": len(lg["entries"]) + 1,
    "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    "kind": "full",
    "reason": "ledger hardening on the reviewer's advice: document the legacy-entry policy, freeze existing entries' canonical hashes, and start a forward hash chain (prevEntryCanonicalSha256)",
    "contractRevision": 39,
    "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
    "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
    "chainManifest": {"frozenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "entries": manifest,
                      "rule": ("An auditor can recompute each entry's canonical JSON hash and compare it with this manifest: any later edit to an archived entry changes its hash and is therefore detectable, even though the ledger's own file hash changes with every append. "
                               "Entries appended from this one onward also carry prevEntryCanonicalSha256, so the chain is verifiable going forward without relying on this manifest.")},
    "prevEntryCanonicalSha256": prev,
    "chainCheck": {"entriesFrozen": len(manifest), "lastEntryCanonicalSha256": prev},
    "artifacts": {"acceptance-report.json": {"path": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json",
                                             "sizeBytes": os.path.getsize(os.path.join(A, "acceptance-report.json")),
                                             "sha256": hashlib.sha256(open(os.path.join(A, "acceptance-report.json"), "rb").read()).hexdigest(),
                                             "measuredAt": datetime.datetime.fromtimestamp(os.stat(os.path.join(A, "acceptance-report.json")).st_mtime).strftime("%Y-%m-%d %H:%M:%S")},
                  "scripts/gate_baseline.json": {"path": "scripts/gate_baseline.json",
                                                 "sizeBytes": os.path.getsize("scripts/gate_baseline.json"),
                                                 "sha256": hashlib.sha256(open("scripts/gate_baseline.json", "rb").read()).hexdigest()}},
}
entry["ledgerSelfProof"] = {
    "rule": "this entry records the ledger sha256 before its write, its own canonical hash, and the previous entry's canonical hash (chain)",
    "entryCanonicalSha256": canon(entry),
}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
post = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(post), "B /", hashlib.sha256(post).hexdigest())
print("frozen canonical hashes:", len(manifest))
print("chain start (prev):", prev[:32])
print("this entry canonical:", entry["ledgerSelfProof"]["entryCanonicalSha256"][:32])
