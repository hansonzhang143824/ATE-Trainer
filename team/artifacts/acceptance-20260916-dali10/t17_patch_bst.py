# t17_patch_bst.py — 计划冻结修复：BST−SW 对齐裁定 (ii) + 生成器幂等
# 运行：python team/artifacts/acceptance-20260916-dali10/t17_patch_bst.py
import os
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
D = os.path.join(os.path.dirname(os.path.abspath(__file__))) + os.sep
P = D + "test-plan-build.py"

raw = open(P, "rb").read()
bom = raw[:3] == b"\xef\xbb\xbf"
t = raw.decode("utf-8-sig")
orig = t

# ---- 1) assumptions 的 BST−SW 仲裁文本 → 裁定 (ii) ----
old1 = ('"Resource arbitration — DECIDED: the bootstrap-to-switched loop is driven from the floating channel 1 '
        '(high terminal to the bootstrap node, low terminal to the switched node). This is the baseline and it means the high-side item consumes both floating channels '
        '(channel 0 for the 1 A Check-pair loop, channel 1 for the 5 V bootstrap loop) while the low-side item needs only channel 0, i.e. the high-side item is the binding constraint.')
new1 = ('"Resource arbitration — DECIDED (ruling (ii), captain; supersedes the earlier floating-channel-1 baseline): the bootstrap-to-switched rail is driven by the '
        'GROUND-REFERENCED ACM200 pair SW12_U1REF_BST_ACM (closed set [110,61] = K110_ACM18_BST / K61_ACM8_SW), and the floating-channel-1 route is recorded as '
        'INTENDED BUT CURRENTLY UNREALISABLE. Evidence: (1) channel 1 has NO minimal endpoint macro - only the composite K_FPVIH_TO_BST_B = 131,132,134,135 and '
        'K_FPVIL_TO_SW_B = 132,133,134,135, whereas channel 0 has K_FPVIH_TO_PMID_A = 83 and K_FPVIL_TO_SW_A = 60,61; (2) those four relays are channel 1 sense-float / '
        'local-sense / PC-route relays (StdAfx.h:303-309), i.e. the same class the negative list 87/88/89/90/91 forbids actuating, so the ch1 route could only be closed '
        'through composite macros and/or forbidden relays; (3) no live TM drives the bootstrap rail through FPVIe1 (FPVI1 appears only in zero-value initialisations and in '
        'teardown). Precondition to restart the ch1 variant: provide a minimal channel-1 endpoint relay set with evidence. Consequence for the channel budget: with (ii) the '
        'high-side item uses floating channel 0 only, but the two high-current items must STILL be separate functions, because the 0x59/0x5A HS/LS side-bit mutual exclusion '
        'and their differing PMID setpoints (15 V vs 9 V) forbid merging them.')
n1 = t.count(old1)
t = t.replace(old1, new1)

# ---- 2) globalRulesApplied 的 R-BST-SW 文本 ----
old2 = ('"R-BST-SW: bootstrap >= switched node at all times; the large-current loop takes the floating bus first and the bootstrap rail degrades to independent sources."')
new2 = ('"R-BST-SW: bootstrap >= switched node at all times; the bootstrap-to-switched rail is driven by the GROUND-REFERENCED SW12_U1REF_BST_ACM pair '
        '(ruling (ii); closed set [110,61]). The floating-channel-1 variant is intended but currently unrealisable - channel 1 has no minimal endpoint macro and its '
        '131/132/134/135 relays belong to the sense-float / PC-route class the negative list forbids actuating."')
n2 = t.count(old2)
t = t.replace(old2, new2)

# ---- 3) generatedAt 改为 revision 派生（幂等前提）----
old3 = '    "generatedAt": datetime.now(CST).isoformat(timespec="seconds"),'
new3 = ('    # Idempotency: generatedAt is a revision-derived CONSTANT, never a wall clock.\n'
        '    # A wall-clock stamp makes two consecutive runs byte-different, so "the artifact carries generatedAt"\n'
        '    # and "two runs are byte-identical" can only hold together if the timestamp is content, not time.\n'
        '    "generatedAt": "revision-derived constant (NOT a wall clock) - see hashPolicy; the real measurement time is recorded by the verifier",')
n3 = t.count(old3)
t = t.replace(old3, new3)

# ---- 4) revision 串升级为 v20（保留 v19 说明作为历史）----
old4 = '"revision": "v19 (naming-policy accuracy + reader discipline):'
new4 = ('"revision": "v20 (t17 closure - BST-SW ruling (ii) + idempotent generatedAt): the bootstrap-to-switched baseline is the ground-referenced '
        'SW12_U1REF_BST_ACM pair ([110,61]) and the floating-channel-1 variant is recorded as intended-but-currently-unrealisable with its three evidence points; '
        'the R-BST-SW global rule is aligned to the same ruling; and generatedAt is now a revision-derived constant so two consecutive generator runs are byte-identical. '
        'Carried forward unchanged: v19 (naming-policy accuracy + reader discipline):')
n4 = t.count(old4)
t = t.replace(old4, new4)

data = t.encode("utf-8")
if bom:
    data = b"\xef\xbb\xbf" + data
with open(P, "wb") as f:
    f.write(data)

print("assumptions BST text replaced:", n1)
print("R-BST-SW rule replaced:", n2)
print("generatedAt made idempotent:", n3)
print("revision bumped to v20:", n4)
print("file changed:", t != orig, "| bytes:", len(data))
