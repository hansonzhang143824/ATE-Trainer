import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t50-payload-k76-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
add=('## 1d. FINAL EDIT (captain-authorised, second and last write) + POST-CHANGE VERIFICATION\n\n'
 '**Hash trail for this instruction:** `c03632d9…` / 42,998 B (**recorded before the edit**) → **`66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4` / 43,806 B** (+808 B).\n'
 'Parts (i) removal of `K109/K110` and (ii) withdrawal of the `--check-extra` disable were already in `c03632d9…`;\n'
 'this edit added (iii) the two-case operational fact and marked the two superseded comment blocks.\n\n'
 '### FACT — measured after this edit, on `66abc088…`\n\n'
 '| Item | Value |\n| --- | --- |\n'
 '| TM600 `SetOn` (the authorised 9-item target) | `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);` |\n'
 '| `SetOn` calls in TM600 | **1** |\n'
 '| Content keys (comments stripped) | `K48_ACM5_AMP_REF` 1 · `K76_ACM_BST` 1 · `K109_BUSL1_PB0` **0** · `K110_ACM18_BST` **0** · `K46` 0 |\n'
 '| Invariants | `delay_ms(1)` 6 · `delay_ms(2)` 0 · `SetClamp(50,50)` 2 · `MeasureVI(200,5,FPVIe_MV_X10)` 2 · bare `126` 0 · `K126_V1P5_CAP` 2 · `ERROR_RES` 2 · `K57_CAP_BST_SW` 2 · `K5+K44+K45` 0 |\n'
 '| `PMID_HG2` 10 V step | `FXVIe_PLUS_20V` |\n'
 '| Encoding | BOM · CRLF · **0 lone LF** |\n'
 '| ACM Sets | TM600 10 · TM601 0 |\n'
 '| Two-case operational fact present | yes — *UN-ENERGISED: `S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F/SW1_S` (or `K49(Relay-ON) -> SW2_F/SW2_S`) `:775`/`:778`; K48 ENERGISED: `-> K48(Relay-ON) -> K76(Relay-ON) -> BST_F/BST_S` `:673`/`:674`* |\n'
 '| `relays.md` L31 mnemonic referenced | **0** (prohibition held) |\n'
 '| Superseded blocks marked | 2 — the `t29` block and the `t43` union block now carry `[SUPERSEDED BY t50 … retained as history, NOT the operative rule]`, so the file no longer contains a standing instruction that contradicts the code |\n'
 '| **`relay-trace`** | **PASS exit 0** — FR-001 reverse 2; warnings = only the two `TM643_VBAT_LOOP_INDICTOR` entries |\n'
 '| **`awg`** | **PASS exit 0** — `FAIL=0 WARN=0` |\n'
 '| **`bst-sw`** | **FAIL exit 1** — `[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] … 缺失=[110]`; `[scan] targets=4 FAIL=1`; contract source `setup-contract.json rev=26` |\n'
 '| Sandbox rebuilt from these bytes | `478,429 B` / `3039e926…`; its TM600 `SetOn` is the 9-item line above |\n\n'
 '### Why I also marked the superseded blocks (a truthfulness fix, inside the authorised comment work)\n\n'
 'Before this edit the file contained **two comment blocks that flatly contradicted the code**: the `t29` block said the\n'
 'BST path requires `K109`/`K110` closed (*"Without K110 the ACM source reaches PB0, not BST, so ruling (ii)\'s\n'
 'ground-referenced drive of BST-SW would not hold electrically"*), and the `t43` block said the payload implements the\n'
 '**union** including `K109/K110`. After the authorised removal both were false as standing instructions. Since the\n'
 'authorisation was precisely to replace that comment content with a **removal note + rationale**, marking them is\n'
 'within scope; I did **not** delete them — they are retained as history, which also preserves the audit trail for the\n'
 'reviewer. Flagged explicitly because a reviewer reading `667…`/`66abc088…` side by side will see the comment body change.\n\n'
 '### INFERENCE / UNKNOWN (post-change)\n\n'
 '- **INFERENCE:** `bst-sw` remains red for the same reason as before this edit — rev 26 still lists `110` for TM600 in\n'
 '  `aliasResolution[3].closedRelayNumbers`, the criterion the gate declares it uses. This edit is comment-only and did\n'
 '  not change that. Nothing on disk closes both `109/110` and `48/76`, so no payload satisfies rev 26 as written.\n'
 '- **UNKNOWN:** whether rev 26 intended to drop `110` (field missed) or the requirement stands; whether `bst-sw` is the\n'
 '  gate to bind on versus a frozen rev-24 baseline (I hold no rev-24 copy); and any electrical consequence. No bench\n'
 '  measurement is claimed anywhere in this document.\n\n')
if 'FINAL EDIT (captain-authorised' not in t:
    t=t.replace('## 1c. POST-CHANGE RE-VERIFICATION', add+'## 1c. POST-CHANGE RE-VERIFICATION')
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('section present:','FINAL EDIT (captain-authorised' in r.decode('utf-8'))