# t13 patch — setup-contract-build.py：范围更正 + 编号统一 + DV-01 旧名残留
# 运行：python team/artifacts/acceptance-20260916-dali10/apply_t13_patch.py
import io
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "setup-contract-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
crlf = raw.count(b"\r\n")
t = raw.decode("utf-8-sig")
orig = t

# ---- 1) BD-08 范围更正：四项（TM102/103/108/109）的归属改为"各自 DFT.csv 行" ----
old_attr = 'delta["ateStimulus"] = {"vbat": s["ateVbat"], "source": "BD-08 \'standby/supply = 4.2 V\' as declared by the DFT.csv row"}'
new_attr = ('delta["ateStimulus"] = {"vbat": s["ateVbat"], "source": "THIS item\'s OWN DFT.csv row declares vset[vbat," + str(s["ateVbat"]) + ",100e-6,0] '
            '- BD-08\'s \'standby/supply = 4.2 V\' clause applies to TM600/TM601 ONLY and is NOT the basis for this item"}')
n1 = t.count(old_attr)
t = t.replace(old_attr, new_attr)

old_note = ('delta["stimuliSourceNote"] = ("ATE stimulus VBAT = " + s["ateVbat"] + " (BD-08). The IR text below cites reg_config .sv as its source; per BD-08 that is a "\n'
            '                                      "simulation-domain reference only and does not govern the ATE stimulus. Registered divergence: " + s["divergence"])')
new_note = ('delta["stimuliSourceNote"] = ("ATE stimulus VBAT = " + str(s["ateVbat"]) + " taken from THIS item\'s OWN DFT.csv row. SCOPE NOTE: BD-08\'s "\n'
            '                                      "\'standby/supply = 4.2 V\' ruling covers TM600/TM601 ONLY and is NOT cited for this item. The IR text below "\n'
            '                                      "cites reg_config .sv as its source, which is a simulation-domain reference only and does not govern the "\n'
            '                                      "ATE stimulus. Registered divergence: " + s["divergence"])')
n2 = t.count(old_note)
t = t.replace(old_note, new_note)

old_stim = 'delta["stimuli"] = ["(revised per BD-08) ATE VBAT = " + s["ateVbat"] +'
new_stim = 'delta["stimuli"] = ["(revised per this item\'s OWN DFT.csv row; BD-08 covers TM600/TM601 only) ATE VBAT = " + str(s["ateVbat"]) +'
n3 = t.count(old_stim)
t = t.replace(old_stim, new_stim)

# ---- 2) DV-01 旧键名残留（lookup/emit 处）----
n4 = t.count('"voltageDifferentialPreferred"')
t = t.replace('"voltageDifferentialPreferred"', '"voltageDifferentialCandidateDisputed"')
n4b = t.count("voltageDifferentialPreferred")  # 可能还有不带引号的用法

# ---- 3) U10 -> U11（仅 SIGN-CONVENTION / command-sign / bring-up 语境）----
out = []
n5 = 0
for line in t.split("\n"):
    if ("U10" in line) and any(k in line for k in ("SIGN-CONVENTION", "command-sign", "command sign", "bring-up", "FI command", "commandSign")):
        n5 += line.count("U10")
        line = line.replace("U10", "U11")
    out.append(line)
t = "\n".join(out)

# 新增 U10 = QVM ch0 并发性（插入到 U11 条目之前）
anchor = '    {"id": "U11", "topic": "FI command-sign convention'
new_u10 = ('    {"id": "U10", "topic": "QVM channel 0 concurrency with the floating channel forcing the same nodes", '
           '"status": "OPEN - undocumented, NOT assumed", '
           '"detail": "The two-wire sense meter\'s channel 0 and the floating channel can be forced onto the same nodes concurrently; the instrument documentation does not state whether that is permitted. '
           'The relay sets are compatible (the force relays are shared, not exclusive) but instrument-level concurrency needs confirmation. QVM channel 0 is additionally recorded as NOT A KELVIN PAIR (one lead lands on a force net = mixed F/S landing). To be settled by the relay-trace gate / independent review."},\n')
n6 = t.count(anchor)
t = t.replace(anchor, new_u10 + anchor, 1)

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)

print("scope-attribution replacements:", n1, n2, n3)
print("old DV-01 key renames:", n4, "| remaining unquoted:", n4b)
print("U10->U11 token replacements:", n5)
print("U10 QVM entry inserted:", n6)
print("file changed:", t != orig)
print("written bytes:", len(data), "| BOM:", bom, "| original CRLF count:", crlf)
