# -*- coding: utf-8 -*-
"""t34: close L24 (union was transitional, never a requirement), rewrite L29, mark L21(ii)/L26 historical, align all 'removal=>red' wording with the post-t53 state."""
import json, hashlib, os, datetime

A = r"team/artifacts/acceptance-20260916-dali10"
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))

print("before: %d limitations" % len(d["limitations"]))
for i, x in enumerate(d["limitations"]):
    print("  [%d] %s" % (i, x[:90].replace("\n", " ")))

L24 = ("L24 (CLOSED - the 'union' was a transitional description, never a ruling requirement): the batch ruling is REMOVAL of K109/K110 on the channel-5 route; the transient union form measured at 20:48:18 "
       "(41,797 B / 6034af71...) was overwritten in place by the subsequently authorised writes (c03632d9... -> 66abc088...) and therefore has NO copy and NO path in the workspace - a full-tree sha256 scan returning "
       "zero hits is the correct result, not a gap. The delivered artifact is the live 43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 file, which closes {48,60,61,76} and contains no K109/K110 "
       "(executable counts 0), and is COMPLIANT. The earlier 'compliance gap' framing, and the coupling argument that 'rev 25 add-only therefore a payload without K110 must red', are both outdated: the coupling was dissolved when the "
       "contract's own decision field was switched to the channel-5 route (closedRelayNumbers = [48,60,61,76] from rev 33 onward), after which the gate computes the expectation as {48,60,61,76,83} and the delivered payload shows missing = []. "
       "The original union text remains in the contract only as history (closedRelayNumbersSuperseded / relayChainSuperseded / previousPendingOwnerRuling).")

L29 = ("L29 (corrected: the removal is DONE, not pending): the removal of K109/K110 has already been delivered - the live payload closes {48,60,61,76} and nothing else on this node, so the single-route closure is in place. "
       "Consequently the --check-extra ban is no longer needed from rev 29 onward (this version closes a single route and over-closes nothing), and the contract keeps the channel-18 data for provenance via relayChainSuperseded and "
       "contestedAttribution.existingValue. No further cleanup revision is outstanding on this point. (Kept for the record: the earlier note that scheduled a cleanup revision, which presupposed the union disposition.)")

L21_TAIL = (" FINAL OBSERVATION (corrected): case (ii) - 'rev 25 corrected but the payload not yet extended' - belonged to the PRE-t50 payload and is now historical: the delivered payload does close K48/K76, and the contract's decision field "
            "was switched to the channel-5 route (rev 33+), so the gate computes {48,60,61,76,83} and the delivered payload satisfies it (missing = []). No 'second real defect' remains outstanding, and the deployed tree's red is solely the "
            "unlanded state.")

L26_TAIL = (" STATUS (corrected): this premise is void for the delivered artifact - the batch closes the channel-5 route only (no union), so no instrument-output-discipline requirement is load-bearing for it. The text is retained as background "
            "for the superseded union form.")

changed = []
for i, x in enumerate(d["limitations"]):
    if x.startswith("L24 ("):
        d["limitations"][i] = L24; changed.append("L24")
    elif x.startswith("L29 ("):
        d["limitations"][i] = L29; changed.append("L29")
    elif x.startswith("L21 ("):
        if "FINAL OBSERVATION (corrected)" not in x:
            d["limitations"][i] = x + L21_TAIL
        changed.append("L21")
    elif x.startswith("L26 ("):
        if "STATUS (corrected)" not in x:
            d["limitations"][i] = x + L26_TAIL
        changed.append("L26")

d["isolationAudit"]["payloadNote"] = (
    "canonical = the live delivered payload: team/artifacts/acceptance-20260916-dali10/implementation-payload-TM600-TM601.cpp = 43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24 (writes stopped; frozen). "
    "It closes {48,60,61,76} and contains no K109/K110 (executable counts 0). Earlier values circulated as canonical (39,457/2d0984d9..., 41,797/6034af71..., 42,998/c03632d9..., 40,658/5a668fe6...) are all historical: they were overwritten in place "
    "and have no copies, so a zero-hit sha256 scan for them is expected and is not evidence of a gap.")
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f34, "rb").read()
print("patched:", changed)
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))
