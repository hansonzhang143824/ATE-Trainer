# t45 — `SCH-Connect-Map.txt:672` section evidence and the K48 three-state reroute

**Author:** schematic-expert · **Kind:** work (t45, t42 supplementary evidence) · **Attempt:** 1
**Scope:** documents one locator claim + three corroborations + the pin-level reroute closure, and corrects
three stale counts that reached the ledger. **It does not change the t42 verdict**, and it does not modify
`t42-acm200-pin-attribution.md` (`8883daad…`) or `t44-t42-addendum.md` (`30aa1be6…`).

---

## 1. Primary claim — `L672` is the ACM200 section's own group header

```
L662  ## 列6: ACM200 → PIN (Share继电器)          ← section that owns L672
L672    BST  [Kelvin]  需闭合: K48,K76
L673      F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F
L674      S: S5_ACM200_SH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_S
L803  ## 列7: FXVIe_PLUS → PIN (Share继电器)     ← next section
```

Verified by enumerating every `## ` line and taking the last one at or before L672: the owner is
`L662 (列6: ACM200 → PIN)` and the next section starts at `L803`. **So the ACM200 column itself declares, in
its own group header, that reaching BST needs `K48,K76` with source `S5_ACM200_FH5` (pin 5) and no
`K109/K110`.**

**Why this is stronger than the locators used earlier:** it is *intra-section* (the instrument's own column
states it), whereas `L673/L674` are chain lines that could in principle be cross-referenced, and the
`K_BST_ACM` composite macro (`StdAfx.h:620`) is **documentation with 0 call sites** (measured — see §4).

### 1.1 The header also states the absence of a default route
`BST [Kelvin] 需闭合: K48,K76` lists required closures rather than "无(默认导通)". Contrast `L675 BST1
[Kelvin] 需闭合: 无(默认导通)` — BST1 *does* have a default-conducting route, BST does not. So with K48/K76
un-actuated the BST pin has **no source**, which is the FACT behind the TM600 consequence in t46.

---

## 2. Three corroborations (all re-read verbatim)

| Locator | Verbatim | What it establishes |
|---|---|---|
| `L461` | `BST ← S10_CH0_A  [通路]  需闭合: K141,K46,K48,K76` | a **non-ACM** source (QTMU) reaches BST through the **same `K46→K48→K76`** leg |
| `L462` | `S10_CH0_A -> K141(ON) -> K46(ON) -> K48(ON) -> K76(ON) -> BST` | the chain |
| `L536` | `BST ← QVM高端  [通路]  需闭合: K137,K46,K48,K76` | QVM **high** also reaches BST via `K46→K48→K76` |
| `L537` | `S8_QVM_CH0+ -> K137(ON) -> K46(ON) -> K48(ON) -> K76(ON) -> BST` | the chain |
| `L538` | `BST ← QVM低端  [通路]  需闭合: K109,K110,K139` | **the K109/K110 leg serves QVM[L]** |
| `L539` | `S8_QVM_CH0- -> K139(ON) -> K109(ON) -> K110(ON) -> BST` | the chain |

Combined with `L42/L43` (`CH0 Low -> BST 需闭合: K109,K110,K138,K139,K145,K146` ← `S1_FPVIe_FL0`) and
`L268/L269` (`CH1 Low -> BST 需闭合: K109,K110` ← `S1_FPVIe_FL1`), the `K109/K110` leg is used by
**FPVIe[L] and QVM[L]** — never by an ACM200-attributed route. This is the third independent corroboration
that the contract's `'ACM200 S5_FH18 -> BST'` label on that relay bundle is a mis-attribution.

---

## 3. The K48 three-state reroute — pin-level closure

Header row, `SCH-Connect-Map.txt` (all three start from the **same** source pin):

```
L673  F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F      K48 ON              -> BST
L775  F: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F      K48 OFF, K49 OFF    -> SW1
L778  F: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-ON) -> SW2_F      K48 OFF, K49 ON     -> SW2
```
(`L774 SW1 [Kelvin] 需闭合: 无(默认导通)`, `L777 SW2 [Kelvin] 需闭合: K49`.)

The relay pin nets that implement it (`Dali-SCH.csv`, alias-inclusive):

```
K48_AMP_REF_S1   pin3 = NetK46_BUS_SH_SW1_S1_2     pin6 = NetK46_BUS_FH_SW1_S1_2   ← COM1/COM2 = ch5 ⊕ K46
                 pin2 = NetK48_AMP_REF_S1_2        pin7 = NetK48_AMP_REF_S1_7     ← NO  (default throw)
                 pin4 = NetK48_AMP_REF_S1_4        pin5 = NetK48_AMP_REF_S1_5     ← NC  (actuated throw)
K49_ACM_SW2_S1   pin3 = NetK48_AMP_REF_S1_2        pin6 = NetK48_AMP_REF_S1_7     ← COM from K48 NO side
                 pin2 = NetK49_ACM_SW2_S1_2        pin7 = NetCap_SW1_BST1_S1_2     ← default throw -> SW1
                 pin4 = NetK49_ACM_SW2_S1_4        pin5 = NetCap_SW2_BST2_S1_2     ← actuated throw -> SW2
K76_ACM_BST_S1   pin3 = NetK48_AMP_REF_S1_4        pin6 = NetK48_AMP_REF_S1_5     ← COM = K48 NC side
                 pin2/7 = U1_AMP_REF_S1                                            ← default throw
                 pin4 = NetK76_ACM_BST_S1_4        pin5 = NetK57_CAP_BST_SW_S1S2_3 ← actuated -> BST node /
                                                                                     bootstrap-cap node
```

G6K-2G-Y convention (`knowledge/hardware/relays.md:29`): default `2-3` / `6-7`; actuated `3-4` / `6-5`.

**Closed reading:** ch5 sits on `K48` COM (`pin3/6`). With K48 at default it leaves via `NO` (`pin2/7`) into
`K49` COM (`pin3/6`), and `K49` default sends it to `SW1` (`pin7` = `NetCap_SW1_BST1_S1_2`), or `SW2`
(`pin5` = `NetCap_SW2_BST2_S1_2`) when K49 is actuated. With K48 actuated it leaves via `NC` (`pin4/5`)
into `K76` COM (`pin3/6`), and K76 actuated sends it to the BST node (`pin4`) / bootstrap-cap node (`pin5`).

⇒ **One physical line, three states, exactly one destination at a time.** Closing `K48/K76` therefore
**removes** ch5 from SW1/SW2 — the change is a **reroute, not a superposition**. Note the designator is
`K49_ACM_SW2_S1` in the netlist while `StdAfx.h` aliases it `K49_ACM5_SW2`; cite both to avoid a new mismatch.

---

## 4. Corrections to three counts that reached the ledger

Method (required for reproducibility): **a function body runs from its `DUT_API` line to the first line that
is exactly `}` at column 0**; a comment block immediately preceding a declaration belongs to the **next**
function. Alias-inclusive token pattern: `K48(?![0-9])` (a plain `\bK48\b` **silently misses**
`K48_ACM5_AMP_REF`, because `_` after `48` is a word character — this caused an under-count earlier and is
worth guarding).

| Recorded | Measured | Scope of the measurement |
|---|---|---|
| "TM600 段 `.Set` 10 次**全** `RELAY_ON`" | 10 `.Set` calls, **9 `RELAY_ON` + 1 `RELAY_OFF`** (last call `L9194`); non-zero FV = **7** | `TM600_HS_RDSON` = **L9057–9204** |
| "TM640：SW12 提及 **7** 次／非零 3 次／`K48`·`K76` 各 **3** 次" | SW12 mentions **6** (5 `.Set` + 1 comment `L7512`); non-zero **3** ✓; `K48` tokens **2**, `K76` tokens **2**; `SetOn` closing the leg **1** (`L7513`) | `TM640_BOOST_HS_OCP` = **L7503–7590** |
| "TM641：提及 **2** 次／非零 0 次" | mentions **1**, non-zero **0** ✓ | `TM641_BST_UV` = **L7606–7699** |

**Where the inflated numbers came from:** bounding by "nearest preceding `DUT_API`" sweeps the *next*
function's header comment block into the previous function. That single fault produced all three
over-counts (TM641's comment block `L7592–7605` fell into TM640; the following function's block fell into
TM641). The same fault mis-attributed `test.cpp:7598` (it belongs to **TM641**, whose comment block starts
`L7593 // TM641: BUBO BST UV`) and, for a different reviewer, put `L7500` inside `TM616_VC_OFFSET`
(`L7500` actually belongs to **TM640**, whose block is `L7494–7502`). **"Nearest preceding `DUT_API`" is
falsified three times in this file — do not use it for attribution.** Read the comment block's self-declared
`TMxxx` name first, then the physical position.

**Numbers that were confirmed as recorded:** TM600's `.Set` count = 10; the staircase
`0→5→10→15→20→15→10→5→0`; the top range `ACM200_40V`; the final `RELAY_OFF`; TM600's body hits for
`K46/K48/K49/K76/K109/K110` **all zero**; TM640's non-zero = 3; TM641's non-zero = 0.

**Full census (brace-depth, alias-inclusive) — the authoritative version of the contested numbers:**

| function | body range | `.Set` calls | `RELAY_ON` | `RELAY_OFF` | non-zero FV | closes `K48/K76` leg (SetOn) | closes via `K_FPVIH_TO_BST_A` |
|---|---|---|---|---|---|---|---|
| `InitBeforeTestFlow` | L877–973 | 1 | 1 | 0 | 0 | no | 0 |
| `InitAfterTestFlow` | L976–1025 | 1 | 1 | 0 | 0 | no | 0 |
| `SetupFailSite` | L1030–1085 | 1 | 1 | 0 | 0 | no | 0 |
| `TM607_BUCK_LS_ZCD` | L6985–7064 | 3 | 2 | 1 | 1 | **yes** (explicit aliases) | 0 |
| `TM608_BOOST_HS_ZCD` | L7073–7151 | 5 | 4 | 1 | 3 | **yes** (explicit aliases) | 0 |
| `TM609_BOOST_HS_NEG` | L7160–7239 | 5 | 4 | 1 | 3 | **yes** (explicit aliases) | 0 |
| **`TM640_BOOST_HS_OCP`** | **L7503–7590** | **5** | **4** | **1** | **3** | **yes** (explicit aliases) | 0 |
| `TM641_BST_UV` | L7606–7699 | **0** | 0 | 0 | 0 | no | **1** |
| `TM643_VBAT_LOOP_INDICTOR` | L7717–7813 | **0** | 0 | 0 | 0 | no | **1** |
| **`TM600_HS_RDSON`** | **L9057–9204** | **10** | **9** | **1** | **7** | **no** | 0 |
| `TM601_LS_RDSON` | L9217–9353 | 3 | 2 | 1 | 1 | no | 0 |

(`TM641`'s only mention of the instrument is a **comment**, `L7621`
`// ⚠ K48/K76 同时把 ACM200_FH5(SW12_U1REF_BST_ACM) 输出端接 BST → 该源全程 RELAY_OFF 不驱动` — hence 0 `.Set` calls.)

**Leg-closure sets (brace-depth, `SetOn` operands only):**

| Set | Members | Count |
|---|---|---|
| functions closing the `K48/K76` leg | `TM607`(L7000), `TM608`(L7087), `TM609`(L7170), `TM640`(L7513) via explicit `K48_ACM5_AMP_REF`+`K76_ACM_BST`; `TM641`(L7623), `TM643`(L7734) via `K_FPVIH_TO_BST_A` (=46,48,76) | **6** |
| **collision set** — drives the instrument **and** closes the leg | **`TM607`, `TM608`, `TM609`, `TM640`** | **4** |
| closes the leg but does **not** drive the instrument | `TM641`, `TM643` (0 `.Set` calls each) — this is the correct "close the leg with the ACM source held off" form | 2 |

> **Two corrections to what was circulated earlier:**
> 1. **`TM616_VC_OFFSET` must be excluded** from any leg/collision list — its true body `L7411–7488` has
>    **0** instrument mentions and **0** `K48/K76` tokens. The tempting line `L7500`
>    (`… + SW12_U1REF_BST_ACM(BST, K48+K76) + …`) lies in **TM640's** header block (`L7494–7502`).
> 2. **The collision set is 4, not 5.** I previously reported it as 5 with `TM641` included; measurement shows
>    `TM641` makes **0** `.Set` calls of the instrument (it closes the leg via `K_FPVIH_TO_BST_A` while holding
>    the ACM source off, exactly as its `L7598` comment describes). `TM643` is in the same close-only class.

---

## 5. FACT / INFERENCE / UNKNOWN

**FACT**
1. `L672` belongs to the section opened at `L662 (列6: ACM200 → PIN)` (next section `L803`), and reads
   `BST [Kelvin] 需闭合: K48,K76`; `L673/L674` give `S5_ACM200_FH5/SH5 -> K48(ON) -> K76(ON) -> BST_F/S`.
2. `L675` shows BST1 *does* have a default route ("无(默认导通)") while `L672` shows BST does not.
3. `L461/L462`, `L536/L537` reach BST through `K46→K48→K76`; `L538/L539` reach BST through `K109→K110`
   (QVM low); `L42/L43`, `L268/L269` likewise for FPVIe[L].
4. Relay pin nets in §3 (K48/K49/K76), and the three-state route table `L673`/`L775`/`L778`.
5. All counts and the leg-closure sets in §4, with the stated method and scopes.

**INFERENCE**
1. Because ch5's line has exactly one destination per relay state and K48's actuated throw leads to `K76`,
   closing `K48/K76` **reroutes** ch5 away from SW1/SW2 to the BST node — i.e. the two uses are mutually
   exclusive. (Follows from FACT 4.)
2. Because `L672` lists required closures and no default route, an item that enables ch5 without closing
   `K48/K76` delivers nothing to BST. (Follows from FACT 1–2; the TM600-specific consequence is t46.)
3. Every ACM200-attributed route to BST in the header is `K_BST_ACM = 48,76`; the only `ACM200[] -> BST*`
   composites are `K_BST_ACM` and `K_BST2_ACM = 43` — neither contains K110. (Follows from the exhaustive
   macro enumeration in t44 §1 Layer 3.)

**UNKNOWN**
1. The electrical consequence of the SW1 landing at the DUT — owner / bench decision, **not** mine. I do not
   characterise 20 V on SW1 as harmless or as fatal.
2. Whether TM600/TM601 must be driven from ACM200 at all, and whether switching to `PB0_BST_ACM` (ch18) +
   `[110]` is permitted — contract-owner decisions.
3. Whether the deployed `test.cpp` (`15c7d2b8…`) lags the payload (`2d0984d9…`) by design or by pending
   landing — the captain's record, not derivable from the files.

---

## 6. Reproduction (all reads via python; the DALI sources are DLP-transparent-encrypted)

```bash
# L672 section attribution
python -c "l=open('project/DALI/SCH-Connect-Map.txt',encoding='utf-8',errors='replace').read().splitlines();s=[(i+1,x.strip()) for i,x in enumerate(l) if x.startswith('## ')];print([y for y in s if y[0]<=672][-1]);print(l[671]);print(l[672]);print(l[673])"
# the three corroborations
python -c "l=open('project/DALI/SCH-Connect-Map.txt',encoding='utf-8',errors='replace').read().splitlines();[print(i,l[i-1].strip()) for i in (461,462,536,537,538,539)]"
# the three-state reroute headers
python -c "l=open('project/DALI/SCH-Connect-Map.txt',encoding='utf-8',errors='replace').read().splitlines();[print(i,l[i-1].strip()) for i in (672,673,674,774,775,777,778)]"
# relay pin nets
python -c "import csv;r=list(csv.reader(open('project/DALI/Dali-SCH.csv',encoding='utf-8-sig',newline='')));H=r[0];n=H.index('NetName');d=H.index('Designator');p=H.index('PinNumber');[print(x,[(y[p],y[n]) for y in r[1:] if y[d]==x]) for x in ('K48_AMP_REF_S1','K49_ACM_SW2_S1','K76_ACM_BST_S1')]"
# brace-depth recount (alias-inclusive) - replace TMxxx as needed
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();ds=[(i,m.group(1)) for i,x in enumerate(ls,1) for m in [re.search(r'DUT_API\s+\w+\s+(\w+)\s*\(',x)] if m];n=[k for k,(i,f) in enumerate(ds) if f=='TM640_BOOST_HS_OCP'][0];s=ds[n][0];lim=ds[n+1][0]-1;e=next(i for i in range(s,lim+1) if re.fullmatch(r'\}\s*',ls[i-1]));t='\n'.join(ls[s-1:e]);print(s,e,'SW12',t.count('SW12_U1REF_BST_ACM'),'K48',len(re.findall(r'K48(?![0-9])',t)),'K76',len(re.findall(r'K76(?![0-9])',t)))"
```

---

## 7. Boundary

Read-only apart from this file. **No writes to** `t42-acm200-pin-attribution.md` or
`t44-t42-addendum.md` (both kept byte-stable so their reported hashes stay valid), the contract, test plan,
payload, gate scripts, `devel`, or the target tree. Temporary scripts were removed.

All of the above is **static connectivity plus header/netlist/in-service-function-body evidence**. It is
**not** machine-measured and **not** an electrical conclusion; a green gate or a closed compile is not
electrical sign-off.
