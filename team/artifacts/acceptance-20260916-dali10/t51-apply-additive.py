# t51 (owner: test-strategy-architect) - apply the captain-ordered ADDITIVE revision to the generator.
# Keeps every prior value in place (nothing deleted) and ADDS the union disposition + the ch5 route,
# so the plan stops "flipping" [110,61] and instead carries both routes with [110,61] marked contested.
import pathlib

p = pathlib.Path("test-plan-build.py")
t = p.read_text(encoding="utf-8")
original = t

# (a) high-current item assumption: append the additive/union clause
old_a = ("which mixed the FPVIe[L] family's BST relay (110, StdAfx.h:452) with the ACM200 family's SW relay "
         "(61, StdAfx.h:638)), and the floating-channel-1 route is recorded as INTENDED BUT CURRENTLY UNREALISABLE.")
new_a = ("which mixed the FPVIe[L] family's BST relay (110, StdAfx.h:452) with the ACM200 family's SW relay "
         "(61, StdAfx.h:638)) - **v24 (t51, ADDITIVE, captain-ordered): the operative closure for this batch is "
         "the UNION of that ch5 route with the contract-literal pair [110,61] (K110_ACM18_BST + K61_ACM8_SW), "
         "which rev 24 requires literally and which is retained and marked CONTESTED here rather than deleted; "
         "removing K109/K110 is deferred to a later minimal cleanup revision pending owner and bench confirmation, "
         "and --check-extra must not be enabled.**), and the floating-channel-1 route is recorded as "
         "INTENDED BUT CURRENTLY UNREALISABLE.")
assert old_a in t, "item-assumption anchor not found"
t = t.replace(old_a, new_a, 1)

# (b) R-BST-SW rule: same additive statement
old_b = ("closed set [48,60,61,76] - CORRECTED in v22; superseded: [110,61] = K110_ACM18_BST / K61_ACM8_SW, "
         "a cross-family mixture).")
new_b = ("closed set [48,60,61,76] - CORRECTED in v22; [110,61] = K110_ACM18_BST / K61_ACM8_SW is a "
         "cross-family mixture and is retained CONTESTED, not deleted). v24 additive disposition: close the "
         "UNION - the ch5 route above together with the contract-literal [110,61] - and do not enable "
         "--check-extra.")
assert old_b in t, "R-BST-SW anchor not found"
t = t.replace(old_b, new_b, 1)

# (c) top-level revision head -> v24
old_c = ('"revision": "v23 (captain\'s correction to v22, minimal): the ACM200 bootstrap-to-switched baseline\'s '
         'closed relay set is [48,60,61,76], stated per side')
new_c = ('"revision": "v24 (t51, captain-ordered ADDITIVE change): the ACM200 bootstrap-to-switched baseline '
         'keeps the ch5 route [48,60,61,76] AND retains the contract-literal pair [110,61] marked contested - '
         'the operative closure for this batch is their UNION, with removal of K109/K110 deferred and '
         '--check-extra not enabled; it also carries forward v23\'s value [48,60,61,76], stated per side')
assert old_c in t, "revision head anchor not found"
t = t.replace(old_c, new_c, 1)

# (d) append the v24 history entry
marker = ('              "The v22 value is retained in place and marked, not deleted. No engineering constraint '
          'added or removed beyond this correction.")},\n]')
entry = ('              "The v22 value is retained in place and marked, not deleted. No engineering constraint '
         'added or removed beyond this correction.")},\n'
         '    {"revision": "v24", "bytes": None, "sha256": None,\n'
         '     "note": ("v24 (t51, captain-ordered ADDITIVE change; it replaces a flip with an addition): the '
         "high-current item's baseline now carries BOTH routes - the ch5 route [48,60,61,76] (BST [48,76] from "
         "the ACM200 family per StdAfx.h:620 K_BST_ACM; SW [60,61] from the FPVIe[L] family per StdAfx.h:490 "
         "K_FPVIL_TO_SW_A) AND the contract-literal pair [110,61] (StdAfx.h:452 K_FPVIL_TO_BST_B, the "
         "channel-18 route) - the latter retained and marked CONTESTED rather than deleted. "
         "The operative closure for this batch is therefore the UNION, because the contract revision in force is "
         "additive and its expectation set still contains 110, so removing K109/K110 would turn the bst-sw check "
         "red; removal is deferred to a later minimal cleanup revision, to be batched with lifting the "
         "--check-extra prohibition and with the contract marking [110,61] superseded. "
         "The union is also what the t43 outcome prescribes (add K48/K76, retain K109/K110), and the coupling "
         "cost of retaining K109/K110 is registered: closing K109 joins FPVIe1_FL_BUS_S1 / FPVIe1_SL_BUS_S1 onto "
         "the BST node, and K110 attaches the channel-18 source pin there. "
         "Evidence layering: the family macros are documentation/intent-layer evidence (zero call sites in the "
         "deployed executable), while the behaviour layer is the four explicit closures of K48/K76 at "
         "source/test.cpp L7000/L7087/L7170/L7513. Nothing is deleted: [110,61], [48,61,76] and [48,60,61,76] "
         'all remain present and annotated.")},\n]')
assert marker in t, "history marker not found"
t = t.replace(marker, entry, 1)

p.write_text(t, encoding="utf-8")
print("edits applied:", t != original, "| generator bytes:", len(t.encode("utf-8")))
