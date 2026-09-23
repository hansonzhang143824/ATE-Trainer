# t48 — BST node convergence and the ACM200→BST precedent

**Author:** schematic-expert · **Kind:** work (t48) · **Attempt:** 1
**Contents:** (1) the precedent-consistency argument with exact call-site counts; (2) the BST-node
convergence invariant, graded FACT/INFERENCE; (3) a refinement that materially changes how "released" must
be read; (4) the `K109/K110` statement with its exact file attribution; (5) the TM640 count, settled.

**Wording discipline applied throughout (adopted from the Captain):** the six functions below are
**implemented and deployed in the target tree** — *not* "running", because whether the test flow schedules
them is **not verified by me**. Call-site counts and total-mention counts are always **labelled separately**.

---

## 1. Precedent consistency — the ACM200→BST route is `K48+K76` in every existing implementation

Counted as **`SetOn(...)` operands** (not total mentions) in the deployed
`D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` (`15c7d2b8…`):

| macro | call sites | functions (line) |
|---|---|---|
| `K48_ACM5_AMP_REF` | **4** | `TM607_BUCK_LS_ZCD` (L7000), `TM608_BOOST_HS_ZCD` (L7087), `TM609_BOOST_HS_NEG` (L7170), `TM640_BOOST_HS_OCP` (L7513) |
| `K76_ACM_BST` | **4** | the same four functions, same lines |
| `K_FPVIH_TO_BST_A` (= `46,48,76`, `StdAfx.h:377`) | **2** | `TM641_BST_UV` (L7623), `TM643_VBAT_LOOP_INDICTOR` (L7734) |
| `K_BST_ACM` (the `ACM200[] -> BST` composite, `StdAfx.h:620`) | **0** | — |
| `K_FPVIL_TO_BST_B` (`FPVIe[L] -> BST`, `StdAfx.h:452`) | **0** | — |

Total mentions (a **different** quantity, which is why the earlier "8 each" figure is a mention count):
`K48_ACM5_AMP_REF` 8, `K76_ACM_BST` 8, `K_FPVIH_TO_BST_A` 6, `K_BST_ACM` 0.

**⇒ Six deployed functions route to the BST node, always via `K48+K76` (four explicitly, two through the
composite), and none of them uses `K110` to put an ACM200 source on BST.** Every function that carries a
`K110`-bearing BST macro is attributed to `FPVIe[L]` (`StdAfx.h:451/452`) or `QVM[L]` (`:557`).

**Consequence (adopted by the Captain):** TM600's missing `[48,76]` is **not a new requirement — it is an
inconsistency with the already implemented and deployed implementation**. That is a stronger argument than
"a macro exists", and it is the reason the `K_BST_ACM` composite carries no weight on its own (0 call sites).

---

## 2. BST node convergence invariant

### 2.1 The node is reachable from seven sources (FACT)

```
K76_ACM_BST_S1.pin4 = NetK76_ACM_BST_S1_4        K110_BST_S1.pin4 = NetK76_ACM_BST_S1_4
K76_ACM_BST_S1.pin5 = NetK57_CAP_BST_SW_S1S2_3   K110_BST_S1.pin5 = NetK57_CAP_BST_SW_S1S2_3
```

| # | source | route (relays) | locator |
|---|---|---|---|
| 1 | FPVIe0 CH0 high | `K46+K48+K76` | `SCH-Connect-Map.txt:39` |
| 2 | QTMU | `K141+K46+K48+K76` | `:461/462` |
| 3 | QVM high | `K137+K46+K48+K76` | `:536/537` |
| 4 | FPVIe[L] | `K109+K110+…` | `:42/43`, `:268/269` |
| 5 | QVM low | `K109+K110+K139` | `:538/539` |
| 6 | ACM200 ch5 (`SW12_U1REF_BST_ACM`) | `K48+K76` | `:672/673/674` |
| 7 | ACM200 ch18 (`PB0_BST_ACM`) | `K110` | `:724/725` |

### 2.2 FACT vs INFERENCE (the Captain asked for this grading; closure belongs to t43 / the contract owner)

**FACT** — closing `K48/K76` does **not select a source**; it **gathers whatever is enabled onto one node**.
Source selection is performed by *enablement* (which instrument outputs are driven, and which upstream relays
conduct), not by the relay pair itself.

**FACT** — the relay matrix and the instrument outputs are **different mechanisms with different scope**:
`cbite.SetOn(...)` is the tester relay matrix and is **exclusive per call**
(`knowledge/sources/cbite-qtmue.md:92-96`); an instrument's own output relay is set inside that item's body via
`.Set(FV, v, vRange, iRange, ACM200_RELAY_ON|RELAY_OFF)` and is **not** touched by any other instrument's or
item's `SetOn`.

**INFERENCE (for t43 / contract owner to close; not mine to settle)** — therefore a *"close 48/76 ⟹ every other
instrument sharing this node is explicitly `RELAY_OFF`"* pairing is **not enforced by the relay exclusivity**.
It must be stated explicitly if the owner wants it as an invariant. `TM641` is the in-repo precedent for the
practice: it closes `K_FPVIH_TO_BST_A` so FPVIe0 drives BST and keeps the ACM ch5 source off throughout —
`L7598` `// ⚠ K48/K76 与 ACM200_FH5(SW12_U1REF_BST_ACM) 共用接入 BST → 该源全程 RELAY_OFF 不驱动`.

> **Note on the case actually at hand:** for TM600 the pairing is **not load-bearing**, because the relays that
> would carry the other sources are themselves released — see §3, which shows `K46` (MOS) is open and `K110`
> leaves ch18 on its non-BST path. So TM600 does **not** acquire a `RELAY_OFF` obligation for this node; the
> pairing question remains open only as a general contract invariant, not as a TM600 blocker.

---

## 3. Refinement: "released" does **not** mean "non-conducting" — the semantics are class-dependent

This matters because a naive reading of `cbite-qtmue.md:92` ("未列出的全部释放（OFF）") as "unlisted ⇒ no
connection" would **predict a clean open circuit** where the hardware actually produces a **different
conductor** — and we do observe a landing, not an open.

Classes and parts measured from `project/DALI/Component-Statistic.txt` (`[BUS]`/`[Share]` sections) and
`project/DALI/Dali-SCH.csv` (`ComponentValue`):

| relay | class | part | released (de-energised) behaviour |
|---|---|---|---|
| `K48_AMP_REF` | **Share** | IM06DJR (G6K changeover) | **conducts its DEFAULT path** (`pin3↔2`, `pin6↔7`) |
| `K49_ACM_SW2` | Share | IM06DJR | conducts its default path (7 → SW1) |
| `K76_ACM_BST` | Share | IM06DJR | conducts its default path (2/7 → `U1_AMP_REF`) |
| `K110_BST` | Share | IM06DJR | conducts its default path (2/7 → PB0 side), so COM is **off** the BST node |
| `K43_BST2` | Share | IM06DJR | conducts its default path |
| `K46_BUS_FH_SW1` | **BUS** | **TLP3412 (MOS)** | **open** — no conduction |
| `K41_BUS_FL_BST` | BUS | TLP3412 (MOS) | open |
| `K109_BUSL_PB0` | BUS | IM06DJR (G6K) | per BUS semantics: **Pin ↛ BUS** (`relays.md:95`), i.e. the pin is taken off the bus |

Supporting rule text — `knowledge/hardware/relays.md`:

```
L95  | **BUS 继电器**   | … | pin3↔2/pin6↔7: Pin↛BUS | pin3↔4/pin6↔5: Pin↔BUS | 任何需要接 BUS 的测试 |
L96  | **Share 继电器** | … | pin3↔2/pin6↔7: 通默认通道 | pin3↔4/pin6↔5: 通备用通道 | 仅当目标=备用通道 |
L29  **记忆口诀: 默认 2-3 通、6-7 通；通电 3-4 通、6-5 通。**
```

⇒ **The correct rule is:** *released ⇒ (MOS: open) / (Share-changeover: conducts its DEFAULT destination) /
(BUS: the pin is disconnected from the BUS)*. "Unlisted" therefore always states an intent, but **what it
implements differs per class**.

**Why this matters for TM600 (ties §2 to the observed behaviour):**
* `K48` is a **changeover**, so TM600 not listing it does **not** open ch5 — it leaves ch5 on **`K48`'s default
  destination**, which is `K49`'s COM and hence `SW1` (`SCH:774/775`). Hence the **landing**, not an open.
* `K46` is **MOS**, so TM600 not listing it **does** open FPVIe0's high bus off ch5's node — the reason the
  node stays single-source for TM600.
* `K110` is a **changeover**, but its default destination is the **PB0** side (`:724/725`), so not listing it
  keeps **ch18 off** the BST node (whose nets are on `K110`'s other throw, pins 4/5).

This is a **FACT-level** refinement of t47 §1.1 and it does not change t47's verdict; it strengthens the
explanation of why the omission manifests as a reroute.

---

## 4. The `K109/K110` statement — with the exact file attribution

The Captain's ruling that *"TM600's `K109/K110` should be removed"* is **correct for the payload only**;
measured this run:

| artefact | sha256 | TM600 `SetOn` | contains `K109/K110`? | contains `K48/K76`? |
|---|---|---|---|---|
| **payload** `implementation-payload-TM600-TM601.cpp:219` | `2d0984d992d5d8cb…` | `K83, K60, K61, K109_BUSL1_PB0, K110_ACM18_BST, K13, K85, K57, K126` | **yes** | **no** |
| **deployed** `source/test.cpp:9081` | `15c7d2b8d37b1564…` | `K83, K60, K61, K13, K85, K57, K126` | **no** | **no** |

⇒ **payload = wrong leg + missing leg** (needs `K109/K110` removed **and** `K48/K76` added);
**deployed = missing leg only** (needs `K48/K76` added; nothing to remove). Stating "remove `K109/K110` from
TM600" without naming the artefact would send the deployed-tree repair after a relay set it does not contain.

---

## 5. TM640 count — settled; all four earlier figures retired

`TM640_BOOST_HS_OCP` body = **L7503–7590** (boundary = `DUT_API` line → first column-0 `}`; a comment block
immediately preceding a declaration belongs to the **next** function):

| quantity | value | locator |
|---|---|---|
| instrument mentions | **6** = 5 `.Set` + 1 comment | `L7521, L7526, L7566, L7570, L7578` + comment `L7512` |
| non-zero FV sets | **3** | `L7521` (5), `L7526` (10), `L7566` (5) |
| `K48` / `K76` tokens in body | **2** each | comment `L7512` (`(K48+K76)`) + `SetOn L7513` |
| `SetOn` calls closing the leg | **1** | `L7513` |

**Retired:** "3 mentions / 3 each" and "7 mentions / 3 each" (mine) and "4 lines / 4 tokens / 5 mentions"
(the implementer's). Root cause of both over-counts: bounding by *nearest preceding `DUT_API`* sweeps the next
function's header comment block into the previous one — falsified three times in this file (`L7598`→TM641,
`L7500`→TM640, and my own TM640 range). Token regex must be alias-inclusive (`K48(?![0-9])`); `\bK48\b`
silently misses `K48_ACM5_AMP_REF`.

Also settled for completeness: `TM600_HS_RDSON` `.Set` = **10 = 9 `RELAY_ON` + 1 `RELAY_OFF`** (`L9194`),
non-zero FV **7**.

---

## 6. FACT / INFERENCE / UNKNOWN

**FACT**
1. Call-site counts in §1 (4 / 4 / 2 / 0 / 0) and the six deployed functions; mention counts given separately.
2. The seven-source reachability of the BST node and the shared nets `NetK76_ACM_BST_S1_4` /
   `NetK57_CAP_BST_SW_S1S2_3` (§2.1).
3. Class + part per relay and the class-dependent released behaviour (§3), with `relays.md:29/95/96` rule text.
4. The payload/deployed `SetOn` contents for TM600 (§4).
5. The TM640 and TM600 counts (§5).
6. `cbite.SetOn` is exclusive per call (`cbite-qtmue.md:92-96`); instrument outputs are a separate mechanism
   (`.Set(..., RELAY_ON|RELAY_OFF)` in the item body).

**INFERENCE**
1. Closing `K48/K76` gathers enabled sources onto one node; selection is by enablement (§2.2).
2. TM600's omission manifests as a **reroute to SW1**, not an open, because `K48` is a changeover (§3).
3. For TM600 the node stays single-source because `K46` is MOS (opened by omission) and `K110`'s default
   throw keeps ch18 off the node (§3) — so TM600 acquires **no** `RELAY_OFF` obligation for this node.
4. The general "close 48/76 ⟹ explicit `RELAY_OFF` of co-node instruments" pairing is **not** enforced by relay
   exclusivity and must be stated explicitly if wanted; `TM641` (`L7598`) is the precedent practice.
5. TM600 without `K48/K76` leaves the BST rail undriven; the same defect appears as t32's BST-closure failure
   and the compile-side "missing `[48,76]`" — three expressions of one defect.

**UNKNOWN**
1. The electrical consequence at the DUT of the current TM600 state — owner / bench decision. **Not mine to
   characterise as harmless or as fatal.**
2. Whether TM600/TM601 must be driven from ACM200 at all; whether `PB0_BST_ACM` (ch18) + `[110]` is permitted.
3. Whether the deployed tree lags the payload by design or pending landing.
4. Whether the six functions are scheduled by the test flow (hence "implemented/deployed", not "running").

---

## 7. Boundary

This file is the only artefact written by t48. **No writes** to the contract (rev 24, `fd00a508…`), test plan,
payload (`2d0984d9…`), gate scripts, `devel`, or the target tree; `t42`/`t44`/`t45`/`t46`/`t47` artefacts are
untouched. Temporary scripts removed.

All evidence is **static connectivity + header/netlist/component-class/ in-service-call-site text**. It is
**not** machine-measured and **not** an electrical conclusion; a green gate or a closed compile is not
electrical sign-off.

**Reproduce:**
```bash
python -c "import re;from pathlib import Path;t=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();[print(n,sum(1 for l in t if 'SetOn' in l and m in l)) for n,m in (('K48_ACM5_AMP_REF','K48_ACM5_AMP_REF'),('K76_ACM_BST','K76_ACM_BST'),('K_FPVIH_TO_BST_A','K_FPVIH_TO_BST_A'),('K_BST_ACM','K_BST_ACM'))]"
python -c "import csv;r=list(csv.reader(open('project/DALI/Dali-SCH.csv',encoding='utf-8-sig',newline='')));H=r[0];d=H.index('Designator');v=H.index('ComponentValue');n=H.index('NetName');p=H.index('PinNumber');[print(x,[(y[p],y[n]) for y in r[1:] if y[d]==x]) for x in ('K46_BUS_FH_SW1_S1','K48_AMP_REF_S1','K49_ACM_SW2_S1','K76_ACM_BST_S1','K110_BST_S1')]"
python -c "s=open('knowledge/hardware/relays.md',encoding='utf-8',errors='replace').read().splitlines();[print(i,l.strip()[:150]) for i,l in enumerate(s,1) if i in (29,95,96)]"
```

---

# 8. Addendum — folded in on the Captain's explicit instruction

**Note on provenance:** this section was added *after* t48 reached `completed`, because the Captain
explicitly directed this round's material into t48 and forbade a fourth addendum task. **t48's task status is
unchanged (`completed`)**; only this file's content advanced. Consequently the hash reported with the original
completion (`ae135c06…`) is **superseded** — any reviewer anchored on it must re-anchor on the current hash.

Items folded in: the `TM616` exclusion, the collision-set definition split, the named delimitation method and
the citation discipline, and the TM601 cross-corroboration.

## 8.1 `TM616_VC_OFFSET` is excluded from every leg/collision set (FACT)

Measured with brace-depth delimitation: `TM616_VC_OFFSET` body = **L7411–7488**, containing **0** mentions of
`SW12_U1REF_BST_ACM` and **0** occurrences of `K48`/`K76`. The line that invites the opposite conclusion,
`L7500` `// 闭环: FPVI0(K83 High→PMID / K60+K61 Low→SW) + SW12_U1REF_BST_ACM(BST, K48+K76) + V1P5_U34PS_FXVI(VDRV)`,
lies **after** TM616's closing brace (`L7488`) and belongs to **TM640's** header comment block
(`L7494`–`L7502`, declaration `L7503`). ⇒ **exclude TM616** from both the leg-closing set and the collision set.

## 8.2 Collision set — one number per definition, so no unlabelled figures compete

The apparent "4 vs 5" is a **definition difference, not a contradiction**; measured this run:

| definition | members | count | evidence |
|---|---|---|---|
| closes the `K48/K76` leg (via `SetOn`) | `TM607`, `TM608`, `TM609`, `TM640` (explicit aliases) + `TM641`, `TM643` (via `K_FPVIH_TO_BST_A` = 46,48,76) | **6** | SetOn at L7000/L7087/L7170/L7513/L7623/L7734 |
| **drives** the instrument (≥1 `.Set(...)`) **and** closes the leg | `TM607`, `TM608`, `TM609`, `TM640` | **4** | `.Set` counts 3/5/5/5 |
| closes the leg **and references** the instrument at all, comments included | the four above **+ `TM641`** | **5** | `TM641` has `SW12` mentions = 1 but **`.Set` = 0** |

So the Captain's **5** is the third definition (reference-inclusive) and my earlier **4** is the second
(drive-strict); both are correct under their stated definition and are now labelled. The functionally relevant
point is unchanged: **`TM641` and `TM643` close the leg with the source not driven** — the complementary,
correct form (`TM641`'s `L7598` comment states the reason).

Per-function measurements supporting the table (brace-depth): `TM607` `.Set`=3, `TM608`=5, `TM609`=5,
`TM640`=5, `TM641`=**0** (1 comment mention, `L7621`), `TM643`=**0** (0 mentions).

## 8.3 Delimitation method (named) and the citation discipline (5th rule)

**Method — brace-depth, not nearest-preceding-`DUT_API`:**
a function body runs from its `DUT_API` line to the **first line that is exactly `}` at column 0**; a comment
block immediately preceding a declaration belongs to the **next** function, and its self-declared `TMxxx` name
must be read before the physical position is used.

**"Nearest preceding `DUT_API`" is prohibited for attribution** — falsified three times in this file:
`L7598` (belongs to TM641, would be assigned to TM640), `L7500` (belongs to TM640, would be assigned to
TM616), and my own TM640 range that swallowed TM641's block.

**Citation discipline — every count must state all three:**
1. **(a) retrieval method** — `substring` vs word-boundary. **`\bK48\b` does not match `K48_ACM5_AMP_REF`**
   (`_` after `48` is a word character, so there is no word boundary) and therefore **systematically drops the
   alias form**; use `substring` or an explicit alias list, or the guard form `K48(?![0-9])`.
2. **(b) scope + delimitation** — which function/range, and by which method (§8.3).
3. **(c) stripping method** — whether comment-only lines are included; a "mention" count and a "call-site"
   count are different quantities and must be labelled as such (§1, §8.2).

## 8.4 Deployed TM601 still drives the instrument — cross-corroboration of t33 (FACT → INFERENCE)

`TM601_LS_RDSON` body = **L9217–9353** (brace-depth), measured: `SW12_U1REF_BST_ACM` mentions **3**,
`.Set(...)` calls **3** (one non-zero, `L9269` `Set(FV, 5, …, RELAY_ON)`; then `L9338` zero-value and
`L9344` `RELAY_OFF`), and **`K48` / `K76` / `K109` / `K110` = 0** (`K46`/`K49` appear once each, both inside
comments). Its single `SetOn` (`L9255`) is
`K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP`
— no ch5 endpoint.

⇒ **INFERENCE:** the deployed tree still drives the instrument without closing its routing relays, i.e. it
still contains the defect **t38 removed in the payload** (`2d0984d9…`). This is an **independent
cross-corroboration of t33's blocker** ("t29/t38 artefacts not applied to the target tree"), reached from a
different measurement vector.

**Boundary (kept as previously stated):** this shows the deployed tree **lags the payload** — it does **not**
imply t38 failed; landing belongs to the Captain. Both TM600 (`L9057–9204`) and TM601 have **no form** of
`K48/K76` (substring *and* word-boundary checks both zero).

## 8.5 Addendum reproduction

```bash
# TM616 exclusion
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();b=ls[7410:7488];t=chr(10).join(b);print('TM616 L7411-7488: SW12=',t.count('SW12_U1REF_BST_ACM'),'K48=',len(re.findall(r'K48(?![0-9])',t)),'K76=',len(re.findall(r'K76(?![0-9])',t)));print('L7500 owner block: L7494-7502 ->',ls[7499].strip()[:80])"
# collision-set definitions
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();print('TM641 L7606-7699 .Set=',ls[7605:7699].count('SW12_U1REF_BST_ACM.Set'),'mentions=','\n'.join(ls[7605:7699]).count('SW12_U1REF_BST_ACM'));print('TM643 L7717-7813 .Set=',ls[7716:7813].count('SW12_U1REF_BST_ACM.Set'))"
# word-boundary trap
python -c "import re;print('bK48b on alias:',bool(re.search(r'\bK48\b','K48_ACM5_AMP_REF')),'| guard:',bool(re.search(r'K48(?![0-9])','K48_ACM5_AMP_REF')))"
# TM601 cross-corroboration
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();b='\n'.join(ls[9216:9353]);print('TM601 L9217-9353: SW12=',b.count('SW12_U1REF_BST_ACM'),'.Set=',b.count('SW12_U1REF_BST_ACM.Set'),'K48/76/109/110=',[len(re.findall(p,b)) for p in (r'K48(?![0-9])',r'K76(?![0-9])',r'K109(?![0-9])',r'K110(?![0-9])')])"
```

## 8.6 The payload advanced mid-check — §4 is superseded, and §2.2 changes from latent to load-bearing

**Measured after the §4 text was written**, so recorded as a correction rather than left standing:

| artefact | hash | size |
|---|---|---|
| payload as cited in §4 | `2d0984d992d5d8cb…` | 39,457 B |
| **payload on disk now** | **`6034af710a348e5780998867…`** | **41,797 B (543 lines)** |

`TM600_HS_RDSON` in the current payload = **L179–364**, single `SetOn` at **L241**:

```
cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K48_ACM5_AMP_REF, K76_ACM_BST,
            K109_BUSL1_PB0, K110_ACM18_BST, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW,
            K126_V1P5_CAP, -1);
```

⇒ **[48,76] has been added AND [109,110] retained** — this is the "two-reading-safe intersection" of t50.

**§4 is therefore superseded in one respect:** the payload is **no longer "missing leg"**. Its earlier
characterisation ("wrong leg + missing leg"; action = remove `K109/K110` **and** add `[48,76]`) no longer
describes the artefact. What remains is a **coupling-cost** decision about retaining `K109/K110` (t50 registers
that cost), not a missing-leg repair. The deployed tree (`test.cpp` `15c7d2b8…`, `L9081`) is untouched and
still lacks both legs, so §4's deployed-tree column stands.

### Node-level consequence of the intersection (FACT)
With `K48/K76` **and** `K110` closed in the same item:

* ch5 reaches the BST nets through `K48`→`K76` (`NetK76_ACM_BST_S1_4` / `NetK57_CAP_BST_SW_S1S2_3`);
* `K110` is energised, so its COM pins (which carry `S5_ACM200_FH18/SH18`) route through to **the same two
  BST nets**;
* `K109` is energised, so FPVIe1's `FL/SL` bus is tied to `K110`'s COM node.

⇒ **three potential sources** (ACM ch5, ACM ch18, FPVIe1 low-domain bus) are wired to the BST node in one item
— the very gathering §2.2 warns about, now realised at the relay level.

### But the payload mitigates it by instrument-output discipline (FACT)
* `PB0_BST_ACM` occurrences inside the TM600 body = **0** — channel 18 is **never driven**.
* `FPVI1.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF)` at **L355** (cleanup) — channel 1 explicitly released.

⇒ **INFERENCE (and this is the important change to §2.2):** the intersection is safe **because of
instrument-output discipline, not because of the relay set** — exactly the property §2.2 says is *not* enforced
by relay exclusivity. So for the current payload the pairing requirement is **load-bearing**, whereas in the
deployed tree (where neither leg was closed) it was merely latent. §2.2's remainder stands: the pairing must be
stated explicitly if it is to be an invariant; it is not provided by `cbite.SetOn`.

### Also note
`TM601_LS_RDSON` in the current payload = L377–543, `SetOn` at **L448** =
`K154, K155, K60, K61, K13, K85, K57, K126` — **no ch5 endpoint**, consistent with t38's removal. So §8.4's
statement applies to the **deployed tree only** (which still drives the instrument), not to the payload.

> **Review-anchor warning:** the payload is advancing during the run. Any review anchored on a payload hash must
> re-measure immediately before concluding; the hash in §4 and in §8.6's first row are both already stale.
