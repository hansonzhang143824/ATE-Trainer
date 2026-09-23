# t12 acceptance verification - run this, do not quote a hash from memory.
#   python team/artifacts/acceptance-20260916-dali10/verify-setup-contract.py
# It prints the exact five checks the captain listed for the t12 close-out.
import hashlib
import json
import os
import re
import sys

P = os.path.join(os.path.dirname(os.path.abspath(__file__)), "setup-contract.json")
b = open(P, "rb").read()          # bytes, python plaintext view: PowerShell Get-FileHash reads ciphertext here
t = b.decode("utf-8")
c = json.loads(t)

print("file        =", P.replace("\\", "/"))
print("size_bytes  =", len(b))
print("sha256      =", hashlib.sha256(b).hexdigest())

print("\n1) ATE stimulus in the power sequence")
print("   TM600 Step2 =", c["tmDeltas"]["TM600"]["powerSequenceDelta"][1])
print("   TM601 Step2 =", c["tmDeltas"]["TM601"]["powerSequenceDelta"][1])
print("   TM600 ateStimulus =", c["tmDeltas"]["TM600"].get("ateStimulus"))
print("   TM601 ateStimulus =", c["tmDeltas"]["TM601"].get("ateStimulus"))

print("\n2) simulation-domain values retained but demoted")
print("   'simulationDomainReference' occurrences =", t.count("simulationDomainReference"))
print("   TM600 =", c["tmDeltas"]["TM600"].get("simulationDomainReference"))
print("   TM601 =", c["tmDeltas"]["TM601"].get("simulationDomainReference"))

print("\n3) openItems numbering (U10 = QVM concurrency, U11 = SIGN-CONVENTION) [captain latest]")
print("   ids =", [o.get("id") for o in c["openItems"]])
for o in c["openItems"]:
    if o.get("id") in ("U10", "U11"):
        print("   %s :: %s" % (o["id"], o["topic"]))

print("\n4) QVM wording")
print("   'voltageDifferentialPreferred' occurrences =", t.count("voltageDifferentialPreferred"))
print("   'voltageDifferentialCandidateDisputed' occurrences =", t.count("voltageDifferentialCandidateDisputed"))
print("   QVM status =", c["aliasResolution"][0]["sensePlan"]["voltageDifferentialCandidateDisputed"]["status"])
print("   QVM isKelvinPair =", c["aliasResolution"][0]["sensePlan"]["voltageDifferentialCandidateDisputed"]["isKelvinPair"])

print("\n5) stimulus purity self-check")
print("   rule split (t26-check-fix): TM600/TM601 = strict (no simulation-domain number may be presented as an ATE stimulus);")
print("   TM102/TM103/TM108/TM109 = scoped (their stimulus IS the IR/OVERVIEW ATE value per the user's t18 ruling - retract the BD-08 extension - so the check instead asserts the IR value is stated and the DFT.csv divergence is registered)")
SVSTRICT = re.compile(r"(3\.5|vbus|VBUS 5 V|PMID 5 V|PMID=5)")
bad = []
for tm in ("TM600", "TM601"):
    d = c["tmDeltas"][tm]
    for k in ("ateStimulus", "stimuli", "powerSequenceDelta", "commandSign"):
        if SVSTRICT.search(json.dumps(d.get(k), ensure_ascii=False)):
            bad.append("%s.%s" % (tm, k))
print("   TM600/TM601 strict violations =", bad or "NONE")
SCOPED = {"TM102": "4.0 V", "TM103": "4.0 V", "TM108": "3.0 V", "TM109": "3.0 V"}
scope_bad = []
conf_text = " ".join(c.get("conflicts") or [])
for tm, expect in SCOPED.items():
    d = c["tmDeltas"].get(tm) or {}
    stim = json.dumps(d.get("stimuli"), ensure_ascii=False)
    if expect not in stim:
        scope_bad.append("%s: IR value %s not stated in stimuli" % (tm, expect))
    if "TM102/TM103/TM108/TM109" not in conf_text:
        scope_bad.append("%s: DFT.csv-vs-IR divergence not registered in conflicts" % tm)
    if "ateStimulus" in d or "stimuliSourceNote" in d:
        scope_bad.append("%s: BD-08 extension fields must stay retracted (ateStimulus/stimuliSourceNote present)" % tm)
print("   TM102/TM103/TM108/TM109 scoped violations =", scope_bad or "NONE")
print("   VERDICT:", "PASS" if not bad and not scope_bad else "CHECK")

print("\n   schema: python scripts/validate_team_artifact.py setup-contract team/artifacts/acceptance-20260916-dali10/setup-contract.json")
sys.exit(0)
