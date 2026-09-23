import sys,io,os,re,hashlib
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
p=os.path.join(d,'t50-payload-k76-evidence.md')
t=open(p,'rb').read().decode('utf-8-sig')
add=('## 1c. POST-CHANGE RE-VERIFICATION (performed after the CRLF repair, on the final bytes)\n\n'
 'This section exists because my first gate run was made **before** the CRLF repair and therefore graded the\n'
 'LF-broken intermediate (`72d7bc3a…`). Everything below was re-run against the **final** bytes.\n\n'
 '**Sandbox provenance — checked rather than assumed:** the gate prints `payload locator: test.cpp:9133`, and I\n'
 'verified what sits at that line: in my **sandbox** it is exactly the TM600 `SetOn`, whereas in the **deployed**\n'
 'tree line 9133 is an unrelated `SetClamp` comment. The line number therefore confirms the gate read **my sandbox**\n'
 'and that `--src` was honoured. (I state it because I had earlier mis-attributed a result to the wrong file, and a\n'
 'locator that matches the wrong tree is exactly how that happens.)\n\n'
 '### FACT — measured, with the command that produced it\n\n'
 '| Item | Value |\n'
 '| --- | --- |\n'
 '| Payload bytes | `42,998 B` / **`c03632d93e0d4cc594ed4045bf6d52e6d3f897e61ed183e0475d556c45db26e0`** |\n'
 '| Encoding | BOM present · CRLF 558 · **0 lone LF** |\n'
 '| Content keys (comments stripped) | `K48_ACM5_AMP_REF` 1 · `K76_ACM_BST` 1 · `K109_BUSL1_PB0` **0** · `K110_ACM18_BST` **0** · `K46` 0 |\n'
 '| Invariants | `delay_ms(1)` 6 · `delay_ms(2)` 0 · `SetClamp(50,50)` 2 · `MeasureVI(200,5,FPVIe_MV_X10)` 2 · bare `126` 0 · `K126_V1P5_CAP` 2 · `ERROR_RES` 2 · `K57_CAP_BST_SW` 2 · `K5+K44+K45` 0 |\n'
 '| `PMID_HG2` 10 V step | `FXVIe_PLUS_20V` |\n'
 '| TM600 `SetOn` calls | **1** |\n'
 '| ACM Sets | TM600 10 · TM601 0 |\n'
 '| `--check-extra` disable statement | withdrawn (replaced by the single-route rationale) |\n'
 '| **`relay-trace`** | **PASS, exit 0** — FR-001 reverse 2; complete warning list = the two `TM643_VBAT_LOOP_INDICTOR` entries; no TM600/TM601 finding |\n'
 '| **`awg`** | **PASS, exit 0** — `FAIL=0 WARN=0`, 42 AWG functions |\n'
 '| **`bst-sw`** | **FAIL, exit 1** — `[t30] TM600_HS_RDSON: 契约声明必需 [60, 61, 83, 110] … 缺失=[110]`, `[scan] targets=4 FAIL=1` |\n'
 '| Contract source reported by the gate | `setup-contract.json rev=26` |\n'
 '| Target tree | `469,714 B` / `15c7d2b8…` @18:53:33 — **unchanged**, TM600 `SetOn` at L9081 still closes neither `109/110` nor `48/76` |\n\n'
 '### INFERENCE — reasoning over those facts\n\n'
 '- **The rev-26/rev-25 narrowing has not removed `110` from TM600\'s expectation.** `setup-contract.json` declares\n'
 '  `revision: 26` and its `aliasResolution[3].closedRelayNumbers` is still `[110, 61]` with `usedByTm` including TM600 —\n'
 '  the criterion the gate states it uses ("route enumerations and the relaySet pool are **locators only**").\n'
 '- **The failure is not caused by this edit.** The same gate fails against the deployed tree too; and no\n'
 '  currently-deployed implementation closes both `109/110` and `48/76`, so **no payload on disk satisfies rev 26\'s\n'
 '  stated TM600 expectation**. My change makes the payload match deployed reality and thereby exposes the mismatch.\n'
 '- Therefore the unfreeze\'s premise ("rev 25 narrowed ⇒ the `110` expectation is cancelled") is, at this moment,\n'
 '  **not true of the bytes on disk**, regardless of the revision number having advanced.\n\n'
 '### UNKNOWN — not established by anything I hold\n\n'
 '- Whether the rev-26 drafting intended to drop `110` for TM600 and the field was simply missed, or whether the\n'
 '  intent is genuinely to keep requiring it. Only the contract owner can say.\n'
 '- Whether `bst-sw` is the gate the captain intends to bind on for this decision, or whether a frozen rev-24\n'
 '  snapshot is the correct baseline — I hold **no frozen rev-24 copy**, so I cannot produce that column.\n'
 '- Any electrical consequence of closing only the ch5 route. No bench measurement exists.\n\n')
if 'POST-CHANGE RE-VERIFICATION' not in t:
    t=t.replace('## 2. The change applied', add+'## 2. The change applied')
    open(p,'wb').write(t.encode('utf-8'))
r=open(p,'rb').read()
print('evidence %d B / %s'%(len(r),hashlib.sha256(r).hexdigest()))
print('section present:','POST-CHANGE RE-VERIFICATION' in r.decode('utf-8'))