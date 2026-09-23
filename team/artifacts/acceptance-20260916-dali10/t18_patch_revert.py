# t18_patch_revert.py — 撤回 t12 对 TM102/103/108/109 的 BD-08 激励扩展（用户阻塞性指令）
# 运行：python team/artifacts/acceptance-20260916-dali10/t18_patch_revert.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "setup-contract-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")

old = '''    if tm in ATE_STIMULUS_RULING["supplyRailItems"]:
        s = ATE_STIMULUS_RULING["supplyRailItems"][tm]
        delta["ateStimulus"] = {"vbat": s["ateVbat"], "source": "THIS item's OWN DFT.csv row declares vset[vbat," + str(s["ateVbat"]) + ",100e-6,0] - BD-08's 'standby/supply = 4.2 V' clause applies to TM600/TM601 ONLY and is NOT the basis for this item"}
        delta["simulationDomainReference"] = {"vbat": s["irVbat"], "status": "retained, NOT adopted as an ATE stimulus (reg_config .sv / OVERVIEW Code1 value)"}
        delta["stimuliSourceNote"] = ("ATE stimulus VBAT = " + s["ateVbat"] + " taken from THIS item's OWN DFT.csv row (BD-08's 'standby/supply = 4.2 V' clause covers TM600/TM601 ONLY and is NOT the basis here). The IR text below cites reg_config .sv as its source, which per the stimulus-layer rule is a "
                                      "simulation-domain reference only and does not govern the ATE stimulus. Registered divergence: " + s["divergence"])
        if delta.get("stimuli"):
            delta["stimuli"] = ["(revised per this item's OWN DFT.csv row; BD-08 covers TM600/TM601 only) ATE VBAT = " + str(s["ateVbat"]) +
                                "; the IR-derived entry read: " + str(delta["stimuli"][0])] + list(delta["stimuli"][1:])'''

new = '''    if tm in ATE_STIMULUS_RULING["supplyRailItems"]:
        s = ATE_STIMULUS_RULING["supplyRailItems"][tm]
        # t18 (USER BLOCKING INSTRUCTION): the BD-08 excitation extension that t12 added to this
        # non-TM600/TM601 supply-rail item is RETRACTED. No ateStimulus field and no supersede wording is
        # emitted, and the item's ORIGINAL IR-derived stimulus text stands unchanged. The simulation-domain
        # (.sv / OVERVIEW Code1) value is kept as a reference, and the DFT.csv row value is registered as a
        # CONFLICT - both sides retained, neither deleted nor averaged.
        delta["simulationDomainReference"] = {"vbat": s["irVbat"], "status": "retained, NOT adopted as an ATE stimulus (reg_config .sv / OVERVIEW Code1 value)"}
        delta["stimulusScopeNote"] = ("BD-08 (ATE excitation per DFT/OVERVIEW) applies to TM600/TM601 ONLY. The t12 change that "
                                      "extended an ateStimulus VBAT to this item is RETRACTED per the user's blocking correction; the "
                                      "IR-derived stimulus text is left as originally built and must not be read as a BD-08 extension. "
                                      "REGISTERED CONFLICT (both sides retained, neither deleted nor averaged): this item's DFT.csv row "
                                      "declares vset[vbat,4.2,100e-6,0] while the IR/OVERVIEW Code1 value is " + str(s["irVbat"]) +
                                      ". Registered divergence: " + s["divergence"])'''

n = t.count(old)
if n != 1:
    print("ABORT: expected exactly 1 match of the t12 block, got %d" % n)
    raise SystemExit(2)
t = t.replace(old, new)

# 冲突登记：确保在 conflicts 列表里有一条记录（若尚未存在）
marker = "t18-retraction of the BD-08 extension on TM102/TM103/TM108/TM109"
if marker not in t:
    anchor = "conflicts = ["
    i = t.find(anchor)
    if i == -1:
        print("WARN: could not find the conflicts list anchor; conflict entry not appended")
    else:
        j = t.find("\n", i) + 1
        entry = ('    {"id": "BD08-SCOPE-01", "topic": "' + marker + '", '
                 '"status": "closed - retracted", '
                 '"detail": "BD-08 governs TM600/TM601 only. The t12 extension of an ateStimulus VBAT = 4.2 V to TM102/TM103/TM108/TM109 is retracted (t18, user blocking instruction). '
                 'Both sides retained: the DFT.csv rows 12 (TM103), 25 (TM108) and 30 (TM109) declare vset[vbat,4.2,100e-6,0], while the IR/OVERVIEW Code1 value is 4.0 V (TM108/TM109 3.0 V); '
                 'neither is deleted and they are not averaged. The simulation-domain values stay under simulationDomainReference."},\n')
        t = t[:j] + entry + t[j:]
        print("conflict entry appended")
else:
    print("conflict entry already present")

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)
print("patch applied; file bytes:", len(data))
