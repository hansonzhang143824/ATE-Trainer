# -*- coding: utf-8 -*-
"""Locate chainManifest precisely, and build/test a cwd-independent, invariant-only verification command."""
import json, hashlib, os, subprocess, sys, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
LOG = os.path.join(A, "gate-logs-t28", "setupArchitect-freeze-snapshots.json")
lg = json.load(open(LOG, encoding="utf-8"))

found = []
for i, e in enumerate(lg["entries"]):
    if isinstance(e, dict) and "chainManifest" in e:
        cm = e["chainManifest"]
        found.append((i, e.get("snapshotIndex"), e.get("entryCanonicalSha256") is not None, len((cm or {}).get("entries") or [])))
print("entries carrying chainManifest (0-based idx, snapshotIndex, hasSelfProof, frozenEntries):")
for f in found:
    print("   ", f)
print("=> exact JSON path of the first one: entries[%d].chainManifest (1-based snapshotIndex %s)" % (found[0][0], found[0][1]) if found else "=> NOT FOUND")

# also check whether prevEntryCanonicalSha256 chain is present
with_prev = [i for i, e in enumerate(lg["entries"]) if isinstance(e, dict) and e.get("prevEntryCanonicalSha256")]
print("entries with prevEntryCanonicalSha256: %d (indices %s ... %s)" % (len(with_prev), with_prev[:3], with_prev[-3:]))

# build a cwd-independent, invariant-only command and test it from a different working directory
CMD = (
    "python -c \""
    "import re,hashlib,os;"
    "src=r'D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp';"
    "carrier=r'__CARRIER__';"
    "s=open(src,encoding='utf-8',errors='replace').read();"
    "names=re.findall(r'DUT_API\\s+int\\s+(TM643\\w+)',s);"
    "t=open(carrier,encoding='utf-8').read();"
    "print('derived:',names);"
    "[print('ASSERT name=%s hits=%d variant_hits=%d'%(n,t.count(n),t.count(n.replace('VBAT','VAT')))) for n in names];"
    "print('recomputed size/sha (NOT assertions):',os.path.getsize(carrier),hashlib.sha256(open(carrier,'rb').read()).hexdigest()[:16]);"
    "assert all(t.count(n)>=1 and t.count(n.replace('VBAT','VAT'))==0 for n in names), 'NAME ASSERTION FAILED'"
    "\""
).replace("__CARRIER__", os.path.abspath(os.path.join(A, "acceptance-report.json")).replace("\\", "/"))
print("\ncorrected command (cwd-independent, invariant-only assertions):")
print(CMD)
# run it from a DIFFERENT cwd to prove cwd-independence
probe_cwd = os.path.abspath(os.path.join(A, "backups"))
r = subprocess.run(CMD, shell=True, capture_output=True, text=True, cwd=probe_cwd, encoding="utf-8", errors="replace")
print("\n--- run from cwd:", probe_cwd, "---")
print("exit:", r.returncode)
print((r.stdout or "").strip()[:600])
if r.stderr:
    print("stderr:", r.stderr.strip()[:300])

# record
entry = {"snapshotIndex": len(lg["entries"]) + 1, "takenAt": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "kind": "full",
         "reason": "reviewer's three technical points: chainManifest path given, verification command made cwd-independent, expected output reduced to invariants",
         "contractRevision": 39,
         "gateReadField": {"where": "aliasResolution[bst2sw].resolution.closedRelayNumbers", "value": [48, 60, 61, 76], "expectedForTM600": [48, 60, 61, 76, 83]},
         "selfAnchor": {"ledgerSizeBytesBeforeThisWrite": len(open(LOG, "rb").read()), "ledgerSha256BeforeThisWrite": hashlib.sha256(open(LOG, "rb").read()).hexdigest(), "entriesBeforeThisWrite": len(lg["entries"])},
         "prevEntryCanonicalSha256": hashlib.sha256(json.dumps(lg["entries"][-1], ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest(),
         "commandQualityFix": {"chainManifestPath": ("entries[%d].chainManifest - frozen entries: %d" % (found[0][0], found[0][3])) if found else "NOT FOUND",
                               "cwdDependence": "the earlier command used a relative carrier path and therefore only worked from the repository root; the corrected command embeds the absolute path",
                               "invariantOnlyExpectation": "the expected output now asserts only the invariants (derived-name hits >= 1 and algorithmic-variant hits == 0); size and sha are printed as recomputed values and are explicitly NOT assertions",
                               "verifiedFromCwd": probe_cwd, "exit": r.returncode},
         "artifacts": {"gate-logs-t28/setupArchitect-freeze-snapshots.json": {"path": LOG.replace("\\", "/"), "sizeBytes": os.path.getsize(LOG),
                                                                             "sha256": hashlib.sha256(open(LOG, "rb").read()).hexdigest()}}}
entry["ledgerSelfProof"] = {"rule": "chain + self anchors", "entryCanonicalSha256": hashlib.sha256(json.dumps(entry, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()}
lg["entries"].append(entry)
json.dump(lg, open(LOG, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
nb = open(LOG, "rb").read()
print("\nledger:", len(lg["entries"]), "entries |", len(nb), "B /", hashlib.sha256(nb).hexdigest())
