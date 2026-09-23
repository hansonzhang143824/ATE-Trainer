# -*- coding: utf-8 -*-
"""t34 corrections: L19/L20 to the live payload (43,806/66abc088, K109/K110=0); pinRouteTable ACM200 row note; t29-pass scope note."""
import json, hashlib, os, datetime, re

A = r"team/artifacts/acceptance-20260916-dali10"
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))

# --- report what currently mentions the stale values ---
for i, x in enumerate(d["limitations"]):
    if "39,457" in x or "2d0984d9" in x or "K109 x1" in x:
        print("[%d] %s" % (i, x[:230].replace("\n", " ")))
print("----")

LIVE = "43,806 B / 66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4 @2026-09-16 21:09:24"

for i, x in enumerate(d["limitations"]):
    y = x
    # L19: live payload value + content keys
    if y.startswith("L19 "):
        y = y.replace("The live workspace payload is 39,457 B / 2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9",
                      "The live workspace payload is " + LIVE + " (566 lines)")
        y = y.replace("39,457 B / 2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9",
                      LIVE)
        y = y.replace("live 39,457", "live 43,806")
        y = y.replace("the live payload is 39,457 B", "the live payload is 43,806 B")
        y = y.replace("39,457", "43,806").replace("2d0984d992d5d8cb11868660b29cf2c7786ff27367bd7b24b80df4ccf48997f9",
                                                  "66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4")
        y = y + (" CONTENT KEYS RE-VERIFIED against the live bytes (correcting an earlier stale claim): the live TM600 SetOn is [13, 48, 57, 60, 61, 76, 83, 85, 126] - it CONTAINS K48/K76 and its executable K109/K110 counts are ZERO. "
                 "The earlier note that the payload carried 'K109 x1 / K110 x1 executable' described an older revision and is withdrawn. DELIVERED != DEPLOYED still holds, with DELIVERED = 43,806 B.")
    # L20: T32-F1 wording
    if y.startswith("L20 "):
        y = ("L20 (T32-F1, corrected to the captain's post-ch5 wording - the two deployment differences): the deployed revision 15c7d2b8... differs from the LIVE DELIVERED payload (" + LIVE + ") as follows. "
             "(1) The deployed TM600 SetOn at test.cpp:9081 = [83,60,61,13,85,57,126] does NOT close the BST-side K48/K76 - and that same function IS still driving the channel-5 ACM source (SW12_U1REF_BST_ACM: .Set called 10 times, RELAY_ON 9 times), "
             "so per the re-routing mechanism (SCH-Connect-Map.txt:774/775) the excitation is steered to SW1_F / SW2_F and never reaches BST: a LIVE HAZARD, not a benign 'missing closure'. "
             "It must NOT be phrased as 'the deployed tree lacks K109/K110' - under the channel-5 ruling those relays are not supposed to be closed at all (their zero count is correct). "
             "(2) The deployed revision still carries TM601's SW12_U1REF_BST_ACM drive (3 occurrences) which t38 removed, because TM601 has no BST requirement. "
             "DELIVERED != DEPLOYED therefore still holds, with DELIVERED = 43,806 B / 66abc088... and DEPLOYED = 469,714 B / 15c7d2b8... .")
    if y != x:
        d["limitations"][i] = y
        print("updated entry %d (%s)" % (i, x[:24]))

L38 = ("L38 (pinRouteTable ACM200 row - VALUE IS CORRECT, what is missing is grouping and labelling; recorded so nobody 'fixes' the number): the row pinRouteTable[BST]['.6: ACM200 -> PIN (Share relay)'] carries needsClosed=[48,76] sourced from S5_ACM200_FH5/SH5 "
       "(SCH-Connect-Map.txt:672-674) and that VALUE is right. The defect is that the row mixes channels: the FH18/SH18 entry ([110], belonging to PB0_BST_ACM / channel 18) sits in the same aggregation, so a reader cannot tell which pins belong to which instrument. "
       "Remedy = split/label per channel (tracked as a documentation follow-up; the per-channel split VIEW already exists in closedRelayNumbersByRoute.acm200_ch5_bst/acm200_ch5_sw/acm200_ch18_pb0_bst and routeClosureMapping.acm200ChannelSplit). Do NOT change the numeric value.")
L39 = ("L39 (scope of t29's verdict=pass, per the reviewer): the pass holds ONLY against the rev-24 contract LITERAL (tmDeltas.TM600.relaySet contains 109 and pinRouteTable.BST['CH0 Low'].needsClosed contains 109), and that literal's BST half was CROSS-FAMILY (110 from the channel-18 route plus 61 on the SW side). "
       "It therefore must NOT be cited as evidence that the BST path was correct - it only records that the revision conformed to the then-current contract text. Same for the removed/replaced literal after rev 33.")
for x in (L38, L39):
    if x not in d["limitations"]:
        d["limitations"].append(x)

json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b = open(f34, "rb").read()
print("t34:", len(b), "B /", hashlib.sha256(b).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S"), "| limitations:", len(d["limitations"]))
# residual stale-value scan
s = json.dumps(d, ensure_ascii=False)
print("residual '39,457' occurrences:", s.count("39,457"), "| residual '2d0984d9':", s.count("2d0984d9"), "| residual 'K109 x1':", s.count("K109 x1"))

ap = os.path.join(A, "gate-logs-t28", "setupArchitect-anchors.json")
doc = json.load(open(ap, encoding="utf-8"))
doc["anchors"]["acceptance-report.json"] = {"path": "team/artifacts/acceptance-20260916-dali10/acceptance-report.json", "sizeBytes": len(b),
                                            "sha256": hashlib.sha256(b).hexdigest(),
                                            "measuredAt": datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%Y-%m-%d %H:%M:%S")}
json.dump(doc, open(ap, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("anchors:", os.path.getsize(ap), "B")
