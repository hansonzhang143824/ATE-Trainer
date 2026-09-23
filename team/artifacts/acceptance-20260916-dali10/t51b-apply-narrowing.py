# Follow-up to t51: apply the captain's NARROWING ruling (ch5/ch18 conflict closed in favour of ch5).
# v24's additive/union form is superseded; the operative closure becomes the ch5 set [48,60,61,76],
# with [110,61] retained and marked SUPERSEDED (never deleted).
import pathlib

p = pathlib.Path("test-plan-build.py")
t = p.read_text(encoding="utf-8")
original = t
NARROW = (" - **v25 (t51 follow-up, CAPTAIN-ORDERED NARROWING, superseding v24's additive/union clause): the "
          "operative closure is the ch5 set ALONE - [48,60,61,76], i.e. BST [48,76] in the ACM200 family "
          "(StdAfx.h:620 K_BST_ACM) and SW [60,61] in the FPVIe[L] family (StdAfx.h:490 K_FPVIL_TO_SW_A) - "
          "because the ch5/ch18 conflict is CLOSED in favour of ch5: every in-service implementation that drives "
          "SW12_U1REF_BST_ACM closes K48+K76 (comment: (FH5->BST)), t42 independently passed, the contract owner "
          "withdrew the bst2sw mapping, and contract revision 35 already carries [48,60,61,76]. The final batch "
          "removes K109/K110 from the payload and lifts the --check-extra prohibition; v24's union clause is "
          "therefore superseded, and [110,61] remains present only as SUPERSEDED history.**")

# (a) item assumption: replace the v24 union clause with the narrowing clause
old_a = (" - **v24 (t51, ADDITIVE, captain-ordered): the operative closure for this batch is "
         "the UNION of that ch5 route with the contract-literal pair [110,61] (K110_ACM18_BST + K61_ACM8_SW), "
         "which rev 24 requires literally and which is retained and marked CONTESTED here rather than deleted; "
         "removing K109/K110 is deferred to a later minimal cleanup revision pending owner and bench confirmation, "
         "and --check-extra must not be enabled.**")
assert old_a in t, "v24 item clause not found"
t = t.replace(old_a, NARROW, 1)

# (b) R-BST-SW rule: same narrowing
old_b = (" v24 additive disposition: close the "
         "UNION - the ch5 route above together with the contract-literal [110,61] - and do not enable "
         "--check-extra.")
assert old_b in t, "v24 R-BST-SW clause not found"
t = t.replace(old_b, " v25 narrowing disposition: close the ch5 set alone; [110,61] stays in the file only as "
                     "superseded history and the check-extra prohibition is lifted with the final batch.", 1)

# (c) top-level revision head -> v25
old_c = ('"revision": "v24 (t51, captain-ordered ADDITIVE change): the ACM200 bootstrap-to-switched baseline '
         'keeps the ch5 route [48,60,61,76] AND retains the contract-literal pair [110,61] marked contested - '
         'the operative closure for this batch is their UNION, with removal of K109/K110 deferred and '
         '--check-extra not enabled; it also carries forward v23\'s value [48,60,61,76], stated per side')
new_c = ('"revision": "v25 (t51 follow-up, captain-ordered NARROWING; the ch5/ch18 conflict is CLOSED in favour '
         'of ch5): the operative closure is the ch5 set [48,60,61,76] alone - BST [48,76] in the ACM200 family '
         '(StdAfx.h:620) and SW [60,61] in the FPVIe[L] family (StdAfx.h:490) - with [110,61] retained only as '
         'SUPERSEDED history (it is incomplete under either reading: the ACM200 reading lacks 48/76, the '
         'FPVIe[L] reading lacks K109), the final batch removing K109/K110 from the payload and lifting the '
         '--check-extra prohibition; it also carries forward v23\'s value [48,60,61,76], stated per side')
assert old_c in t, "v24 revision head not found"
t = t.replace(old_c, new_c, 1)

# (d) append the v25 history entry right after the v24 entry (located structurally, not by prose match)
i = t.find('"revision": "v24"')
assert i > 0, "v24 history entry not found"
j = t.find('")},\n]', i)
assert j > 0, "REVISION_HISTORY tail after v24 not found"
note_v25 = ('         "NOTE: the union disposition stated here was SUPERSEDED by v25 (narrowing). ")},\n'
            '    {"revision": "v25", "bytes": None, "sha256": None,\n'
            '     "note": ("v25 (t51 follow-up, captain-ordered NARROWING): the ch5/ch18 conflict is closed in '
            'favour of ch5, so the operative closure is the ch5 set alone - [48,60,61,76], stated per side (BST '
            '[48,76] in the ACM200 family per StdAfx.h:620 K_BST_ACM; SW [60,61] in the FPVIe[L] family per '
            'StdAfx.h:490 K_FPVIL_TO_SW_A). '
            'Grounds, in the order the t43 review now ranks them: (1) production behaviour - every in-service '
            'implementation that drives SW12_U1REF_BST_ACM closes K48+K76, with the comment text \\"(FH5->BST)\\", '
            'and the whole file contains K110_ACM18_BST = 0 and K109_BUSL1_PB0 = 0; (2) the t42 independent '
            'review passed on ch5; (3) the contract owner withdrew the erroneous bst2sw mapping; (4) contract '
            'revision 35 already carries [48,60,61,76] with [110,61] retained as superseded history; (5) the '
            'deployed-code locators L6997 (comment) and L7000/L7085/L7087/L7170/L7513 (SetOn), with '
            'SCH-Connect-Map.txt L672-674 versus L42/L268 and StdAfx.h L620/L638/L452/L490. '
            'Naming: Pin_Channel_define.h:20 spells the instrument SW12_U1REF_BST_ACM at channel 5, while :33 '
            'PB0_BST_ACM is channel 18 - a different function, so the two are NOT the same instrument. '
            '[110,61] is incomplete under either reading (ACM200 reading: lacks 48/76; FPVIe[L] reading: lacks '
            'K109, the selector that brings the FPVIe1 low-domain bus onto the node), and it remains in this file '
            'only as superseded history - never deleted. The final batch removes K109/K110 from the payload and '
            'lifts the --check-extra prohibition, and the t30 green condition becomes the high-current item '
            'closing BST [48,76] plus SW [60,61], i.e. the expectation set {48,60,61,76,83}. '
            'This entry supersedes the v24 union/contested disposition.")},\n')
t = t[:j + 4] + note_v25 + t[j + 5:]

p.write_text(t, encoding="utf-8")
print("edits applied:", t != original, "| generator bytes:", len(t.encode("utf-8")))
