# -*- coding: utf-8 -*-
"""t34: replace T32-F1 with the captain's verbatim wording + two-cause split; t35/t41 conclusion lines; contract pendingOwnerRuling update (add-only)."""
import json, hashlib, os, datetime, subprocess, sys

A = r"team/artifacts/acceptance-20260916-dali10"

# ---------------- t34: L1 verbatim + two-cause split + runRules ----------------
f34 = os.path.join(A, "acceptance-report.json")
d = json.load(open(f34, encoding="utf-8"))
VERBATIM = (
    "T32-F1（blocker，部署态，活危害）：部署态 test.cpp（15c7d2b8…，469,714 B / 18:53:33）的 TM600 段在驱动 ACM200 ch5 源（.Set 10 次、RELAY_ON 9 次、含 5/10/15/20 V 阶梯），"
    "而 K48/K76 未闭 ⇒ 按 SCH:774/775 改道机制，该激励被送到 SW1_F/SW2_F、未到 BST ⇒ 活危害；bst-sw 门禁因此应报红（t30 阳性对照即此）。"
    "与 t29 的 verdict=pass 不矛盾（t29 判工作区 payload 合规；未落盘属流程状态）。"
)
CAUSES = (
    " 归因拆分（两因不得合并记账）：真因 = 缺 K48/K76 ⇒ 源改道 SW1/SW2（活危害）；旁因 = 契约决策字段曾未切换（假红）⇒ 已由 rev 29/33 解除。"
)
MEAS_NOTE = (
    " [setup-architect measurement note, appended - not a change to the quoted text: an independent re-measurement of the same deployed block (test.cpp:9057-9216) confirms .Set = 10 and K48 = K76 = K49 = K109 = K110 = 0 in that block; "
    "the RELAY_ON/RELAY_OFF counters differ from the quoted 9 because that block also contains other instruments' calls (measured 25 / 7 over the whole block), so the quoted '9' should be read as the ACM-source-only count.]"
)
newL1 = VERBATIM + CAUSES + MEAS_NOTE
d["limitations"] = [newL1 if x.startswith("L1 (") else x for x in d["limitations"]]
d.setdefault("runRules", {})
d["runRules"]["bstDriveRuling"] = ("TM600 MUST be driven from the ACM200 channel-5 route (t43 final: ch5; in-service code + netlist + IR agree). Substituting the channel-18 route with [110] is NOT permitted - "
                                   "it would change the declared instrument and break the contract/plan/in-service consistency (criterion: reversibility + consistency).")
json.dump(d, open(f34, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
b34 = open(f34, "rb").read()
print("t34:", len(b34), "B /", hashlib.sha256(b34).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(f34).st_mtime).strftime("%H:%M:%S"), "| limitations:", len(d["limitations"]))

# ---------------- t35 appendix L conclusion line ----------------
p35 = os.path.join(A, "t35-contract-reconciliation.md")
s = open(p35, encoding="utf-8").read()
anchor35 = "## 附录 L（Captain 授权的**定点更正**，v1.15）— ch5 口径定案；D/E/F 的\"K110 必需\"前提作废"
add35 = ("\n\n> **结论行（v1.22，Captain 采信 addendum 后定点更新）**：`t43` **终局判定 = (a) ch5**（原 UNKNOWN 与并集建议已由其作者撤回；依据在役生产代码 `:7000/7087/7170/7513` 闭 `K48+K76`、`:6997/7598/7621` 同句写仪器与引脚、全文件 `K110_ACM18_BST`=0／`K109_BUSL1_PB0`=0；`t42` 独立 pass）。"
           "⇒ **本仪器 `SW12_U1REF_BST_ACM` 的 BST 腿 = `[48,76]`、SW 侧 `[60,61]`、闭集 `[48,60,61,76]`**；`K110` 属 `PB0_BST_ACM`（ch18），**本项不闭**。契约 `pendingOwnerRuling` 已更新为“t43 终局：判 (a) ch5（已生效）”（只增不翻、原文保留）。")
if anchor35 in s and "结论行（v1.22" not in s:
    s = s.replace(anchor35, anchor35 + add35, 1)
    print("t35 appendix L conclusion updated")
else:
    print("t35 anchor missing or already updated")
open(p35, "w", encoding="utf-8").write(s)
b35 = open(p35, "rb").read()
print("t35:", len(b35), "B /", hashlib.sha256(b35).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(p35).st_mtime).strftime("%H:%M:%S"))

# ---------------- t41 appendix L2 conclusion line ----------------
p41 = os.path.join(A, "t41-tm601-bst-path-determination.md")
s2 = open(p41, encoding="utf-8").read()
anchor41 = "## 附录 L2（Captain 授权的**定点更正**，v1.6）— ch5 定案对 §1/§H.2/附录 J 的结论更正"
add41 = ("\n\n> **结论行（v1.8，Captain 采信 addendum 后定点更新）**：`t43` **终局 = ch5**（并集撤回）⇒ 本附录的“ch5 路径”表述为现行口径；**`K109/K110` 归 ch18、本项不闭**；"
          "TM601 侧结论不变（其 `SetOn` 中 `K48/K76` 与 `109/110` 四者皆无 ⇒ **两读法下都到不了 BST ⇒ 移除正确**，不依赖引脚归属裁定）。")
if anchor41 in s2 and "结论行（v1.8" not in s2:
    s2 = s2.replace(anchor41, anchor41 + add41, 1)
    print("t41 appendix L2 conclusion updated")
else:
    print("t41 anchor missing or already updated")
open(p41, "w", encoding="utf-8").write(s2)
b41 = open(p41, "rb").read()
print("t41:", len(b41), "B /", hashlib.sha256(b41).hexdigest(), "@", datetime.datetime.fromtimestamp(os.stat(p41).st_mtime).strftime("%H:%M:%S"))

# ---------------- contract: pendingOwnerRuling (add-only) -> rev 37 ----------------
g = os.path.join(A, "setup-contract-build.py")
src = open(g, encoding="utf-8").read()
marker = "# ================== end rev 25 additions =================="
extra = ('# ===== rev 37: pendingOwnerRuling closed (add-only, original text retained) =====\n'
         'for _a in contract.get("aliasResolution", []):\n'
         '    if _a.get("alias") == "bst2sw":\n'
         '        _ca = _a.get("contestedAttribution")\n'
         '        if isinstance(_ca, dict):\n'
         '            _ca["previousPendingOwnerRuling"] = _ca.get("pendingOwnerRuling")\n'
         '            _ca["pendingOwnerRuling"] = ("t43 FINAL: ruled (a) channel 5 (its earlier UNKNOWN ruling and its union suggestion were withdrawn by their author on production-tree behavioural evidence; t42 passed independently). "\n'
         '                                         "Applied in the contract from rev 33 (closedRelayNumbers switched to the channel-5 route) and in force through rev 37. The earlier UNKNOWN text is retained in previousPendingOwnerRuling.")\n'
         '        _a["usedByTm"] = ["TM600 (BST must lead PMID)"]\n')
if marker in src and "rev 37: pendingOwnerRuling closed" not in src:
    src = src.replace(marker, extra + marker, 1)
    src = src.replace("CONTRACT_REVISION = 36", "CONTRACT_REVISION = 37", 1)
    src = src.replace('GENERATED_AT = "2026-09-16 19:30:00 (revision 36)"', 'GENERATED_AT = "2026-09-16 19:30:00 (revision 37)"', 1)
    open(g, "w", encoding="utf-8").write(src)
    def run():
        r = subprocess.run([sys.executable, g], capture_output=True, text=True)
        if r.returncode != 0:
            print("GENERATOR FAILED", r.stdout[-500:], r.stderr[-1200:]); sys.exit(1)
        b = open(os.path.join(A, "setup-contract.json"), "rb").read(); return len(b), hashlib.sha256(b).hexdigest()
    a1 = run(); a2 = run()
    print("contract rev37:", a1, "identical:", a1 == a2)
else:
    print("generator anchor missing or already updated")
