# -*- coding: utf-8 -*-
"""Record two verified cross-checks: the owner's mirror hash names a real revision of my ledger; and the CRLF chain definition reproduces - including my own instrument failure."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")

FINDING = {
    "mirrorHashNamesARealRevision": {
        "recordedByOwner": "preservedPeerNamespaces.setupArchitectFreezeAnchors.mirroredContentSha256",
        "valuePrefix": "acee857ed8501427357579a0bb03def2",
        "whereIITFindIt": "entries[78].selfAnchor.ledgerSha256BeforeThisWrite - exactly one occurrence inside my ledger",
        "meaning": ("the hash the owner recorded as 'the mirrored content' is the state of my ledger immediately before my write 78, so the mirror names a GENUINE revision rather than making a self-declared claim. "
                    "A third party can therefore locate the exact revision referenced, using my own chain-of-custody. This is the payoff of append-only self-anchoring: the two artefacts cross-confirm."),
        "note": "by construction the recorded hash no longer equals the ledger's CURRENT hash - that is the point of naming a revision instead of a state",
    },
    "crlfChainDefinitionVerified": {
        "claim": "the owner's executable definition prevLineSha256 = sha256(prev.rstrip(b'\\r\\n')) is correct; the naive rstrip(b'\\n') would produce a false-mismatch storm",
        "myMeasurement": {"rows": 54, "allRowsEndWithCR": True,
                          "mismatchesWith_CRLF_strip": "0 / 54", "mismatchesWith_LF_strip": "53 / 54"},
        "conclusion": "the file is CRLF and their definition reproduces exactly; the wrong convention yields 53 of 54 rows flagged",
    },
    "myInstrumentFailedFirst": {
        "whatIDid": "I first split the bytes with bytes.splitlines() and then applied both strip variants",
        "whyItCouldNotDiscriminate": "splitlines() removes the line terminator entirely, so both rstrip(b'\\r\\n') and rstrip(b'\\n') became no-ops and BOTH gave 0 of 54 - an instrument that erases the very property under test",
        "correction": "re-ran with raw.split(b'\\n') so the carriage return stays attached; then the two conventions separate cleanly (0/54 vs 53/54)",
        "ruleWorthKeeping": "when comparing line-ending conventions, the reader must preserve the terminator until the comparison happens; a convenience splitter that consumes it destroys the evidence",
    },
}
doc = json.load(open(ap, encoding="utf-8"))
doc["crossArtifactVerifications"] = FINDING
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("anchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "recorded two cross-artifact verifications (mirror hash names a real revision; CRLF chain definition reproduces) and my own instrument failure while testing the latter",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "crossArtifactVerifications": FINDING,
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "gate-logs-t54/build-report.receipts.jsonl": {"path": os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl").replace("\\", "/"),
                                                                     "sizeBytes": os.path.getsize(os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl")),
                                                                     "sha256": hashlib.sha256(open(os.path.join(A, "gate-logs-t54", "build-report.receipts.jsonl"), "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
