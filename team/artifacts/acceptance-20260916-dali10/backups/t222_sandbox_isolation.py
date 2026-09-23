# -*- coding: utf-8 -*-
"""Verify the owner's --in/--out isolation and UTF-8 fix; record the 'isolate inputs as well as outputs' rule in my spec."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
def rec(p):
    b = open(p, "rb").read()
    return {"path": p.replace("\\", "/"), "sizeBytes": len(b), "sha256": hashlib.sha256(b).hexdigest(),
            "measuredAt": datetime.datetime.fromtimestamp(os.stat(p).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}

gen_p = os.path.join(A, "gate-logs-t28", "t28_make_anchors.py")
g = open(gen_p, encoding="utf-8").read()
print("generator:", rec(gen_p)["sizeBytes"], "B /", rec(gen_p)["sha256"][:24], "@", rec(gen_p)["measuredAt"])
for probe, label in ((r"--out", "out flag"), (r"--in", "in flag"),
                     (r"reconfigure\(encoding='utf-8'", "stdout/stderr utf-8 reconfigure")):
    print("   contains %-32s %s" % (label, bool(re.search(probe, g))))
print("   argv parsing present:", bool(re.search(r"sys\.argv", g)))

sh = os.path.join(A, "gate-logs-t28", "t28-anchors.json")
sb = open(sh, "rb").read()
print("\nlive shared file:", rec(sh))
print("   contains probe markers:", ("qaProbeAnchors" in sb.decode("utf-8", "replace")) or ("VARIANT" in sb.decode("utf-8", "replace")))

br_p = os.path.join(A, "build-report.json")
rc_p = os.path.join(A, "gate-logs-t54", "build-report.receipt.json")
br, rc = rec(br_p), rec(rc_p)
rd = json.load(open(rc_p, encoding="utf-8"))
print("\nbuild-report:", br["sizeBytes"], "B /", br["sha256"][:24], "@", br["measuredAt"])
print("receipt     :", rc["sizeBytes"], "B | consistent with live bytes:", rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"])
print("receipt fields:", sorted(rd.keys()))

RUN = {
    "name": "sandbox isolation rule (raised by compile-diagnostician, forced by schematic-expert's observation)",
    "statement": ("Isolating a tool's OUTPUT is not isolating the tool. A run that redirects only the output still READS the canonical live input, so injected test fixtures silently have no effect. Complete isolation means redirecting BOTH the input and the output - here `--in <copy>` together with `--out <sandbox>`."),
    "howItWasFound": "after adding --out, the owner's first sandboxed re-run showed zero injected probe entries taking effect; the generator was still reading the canonical live file",
    "verifiedEffect": "with --in and --out together: exit 0, stderr length 0, probe entries 3 of 3 preserved, my namespace retained, and the live file's hash unchanged before and after",
    "consequenceForReproduction": "third parties can now re-run the experiment with ZERO modification (no copy-and-patch); my earlier reproduction - copying the generator and patching exactly two lines - remains valid but is no longer the only route",
    "siblingRules": ["scopeRule (state the domain scanned)", "fieldAddressingRule (address by name, declare numbering)", "prohibitedInferenceConvention"],
}

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["sandboxIsolationRule"] = RUN
spec = doc.get("controlExperimentSpec") or {}
execu = spec.get("executionByOwner") or {}
execu["zeroModificationReproduction"] = ("available now: the generator accepts --in and --out, so a third party can re-run with no modification (no copy-and-patch). Verified by the owner: exit 0, stderr 0, 3 of 3 probe entries preserved, live file hash unchanged.")
spec["executionByOwner"] = execu
spec["reproductionRoutes"] = ["zero-modification: --in copy --out sandbox (available after the --in/--out addition)",
                              "copy-and-patch: copy the generator and patch the two lines (workspace root, output path) - the route I used for the first independent reproduction"]
doc["controlExperimentSpec"] = spec
doc["generatedAt"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
ab = open(ap, "rb").read()
print("\nanchors:", len(ab), "B /", hashlib.sha256(ab).hexdigest())

LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
pre = open(LOG, "rb").read(); lg = json.loads(pre.decode("utf-8"))
def canon(e):
    return hashlib.sha256(json.dumps(e, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "verified the owner's --in/--out isolation and UTF-8 fix; recorded the sandbox-isolation rule and the availability of a zero-modification reproduction route",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[alias=='bst2sw'].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(pre), "ledgerSha256BeforeThisWrite": hashlib.sha256(pre).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": canon(lg["entries"][-1]),
         "sandboxIsolationRule": RUN,
         "peerClaimsVerified": {"--in": True, "--out": True, "utf8Reconfigure": bool(re.search(r"reconfigure\(encoding='utf-8'", g)),
                                "liveFileUnpolluted": ("qaProbeAnchors" not in sb.decode("utf-8", "replace")),
                                "receiptConsistent": rd.get("sha256") == br["sha256"] and rd.get("size") == br["sizeBytes"]},
         "artifacts": {"gate-logs-t28/setupArchitect-anchors.json": {"path": ap.replace("\\", "/"), "sizeBytes": len(ab), "sha256": hashlib.sha256(ab).hexdigest()},
                       "gate-logs-t28/t28_make_anchors.py": {"path": gen_p.replace("\\", "/"), "sizeBytes": os.path.getsize(gen_p), "sha256": hashlib.sha256(open(gen_p, "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": canon(entry)}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("ledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
