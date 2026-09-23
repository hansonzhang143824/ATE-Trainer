# t47 — Is TM600's `K48/K76` closure isolatable, given ch5 endpoint sharing?

**Author:** schematic-expert · **Kind:** work (t47) · **Attempt:** 1
**Question (as upgraded by the Captain):** does the sharing of the ACM200 ch5 endpoints (the in-service
functions that drive the instrument, plus the two `aliasFlatTable` variant rows) make TM600's `K48/K76`
closure **non-isolatable**? If there is a conflict, state how the fix must be expressed; if there is none,
state why — **no middle ground**.

## Answer

**There is no runtime conflict. TM600's `K48/K76` closure IS isolatable**, and the reason is decisive:
**`cbite.SetOn` is an exclusive operation — each call defines the complete conducting set, and every relay
not listed is RELEASED.** Therefore no relay state carries over between test items, and each of the
in-service functions already carries its own complete set. TM600's defect is precisely that `K48/K76` are
**absent from its complete set** (so they are *released*, not "left closed by someone else"), and its fix is a
**single-call addition** to the existing `SetOn` at `test.cpp:9081`.

The one thing the fix must **not** do is add `K46`: TM600 must keep FPVIe0's high bus off ch5's node (§3.3).

---

## 1. The governing semantics — `SetOn` is exclusive (FACT)

`knowledge/sources/cbite-qtmue.md`:

```
L61  ## 2.3 SetOn()
L65  BYTE SetOn(int k1, ...);
L87  cbite.SetOn(K1, K2, -1);         // only K1,K2 on; K3,K4 off
L88  cbite.SetOn(K1, K2, K3, K4, -1); // all four on
L89  cbite.SetOn(-1);                 // all off
L92  **⚠ 排他陷阱（用户 2026-08-09 纠正）**：`SetOn` 是**排他（exclusive）操作**——每次调用只闭合
     括号内列出的继电器，**未列出的全部释放（OFF）**。
L93  - 错误模式：SetOn(A, -1); SetOn(B, -1); 两次分开调用 → 第二次把 A 释放，最终只有 B 闭合。
L94  - 正确做法：要同时闭合多个继电器，列在同一次 SetOn 括号内：SetOn(A, B, -1);
L96  - DALI 实际踩坑（2026-08-09）：TM109/110、TM111/112 原写成两行分开 SetOn … 已合并为单次调用。
```

Consequences used throughout this document:
1. **Per-item state is complete and self-contained** — unlisted ⇒ released, so nothing leaks in from a
   previous item, and nothing an item forgets can be inherited.
2. **All relays an item needs must be in ONE call** — the split-call failure mode at `L92–L93`.
3. **"Not listing" is an active statement of intent** (the relay will be OFF), not a neutral omission.

---

## 2. Per-function state of the ch5 endpoints

**ch5's endpoint set = `{K46, K48, K76, K49}`**, established at pin level (`Dali-SCH.csv`):

```
ch5 source pin      S5_ACM200_FH5  sits on net NetK46_BUS_FH_SW1_S1_2
that net's members  = { K46_BUS_FH_SW1_S1.2 , K48_AMP_REF_S1.6 , S5_ACM200_FH5 }   <- K46 and K48 both here
K48 pin3/6          = NetK46_BUS_SH/FH_SW1_S1_2   (COM = ch5 node)
K48 pin2/7 (default throw) = NetK48_AMP_REF_S1_2/_7  -> K49 COM (pin3/6)
K48 pin4/5 (actuated throw)= NetK48_AMP_REF_S1_4/_5  -> K76 COM (pin3/6)
K49 pin7 = NetCap_SW1_BST1_S1_2 (SW1)      K49 pin5 = NetCap_SW2_BST2_S1_2 (SW2)
K76 pin4 = NetK76_ACM_BST_S1_4 (BST_F node) K76 pin5 = NetK57_CAP_BST_SW_S1S2_3 (bootstrap-cap node)
```

**Not in the set:** `K41` / `K43`. Measured pins — `K41_BUS_FL_BST_S1` = `FPVIe0_FL_BUS_S1 ↔
NetK41_BUS_FL_BST_S1_2`, `K43_BST2_S1` pins 3/6 = `NetK42_AMP_PS_S1_2/_7`: these are the **FPVIe[L] →
BST1/BST2** legs, on different nets from ch5's. So the variant rows `bst1_sw1 = [46,41]` and
`bst2_sw2 = [46,49,41,43]` share **`K46` and `K49`** with ch5, **not** `K41`/`K43`.

Composite macros expanded from `StdAfx.h` for the closures below:
`K_FPVIH_TO_PMID_A`=83 (`:421`), `K_FPVIH_TO_PGND_A`=154,155 (`:417`), `K_FPVIH_TO_BST_A`=46,48,76
(`:377`), `K_FPVIH_TO_SW1_A`=46 (`:425`), `K_FPVIH_TO_SW2_A`=46,49 (`:427`), `K_FPVIL_TO_BST1_A`=41
(`:447`), `K_FPVIL_TO_BST2_A`=41,43 (`:449`).

### 2.1 Census (body = `DUT_API` line → first column-0 `}`; alias-inclusive)

| function | body | `.Set` calls of the instrument | non-zero FV | SetOn call(s) (line) | **expanded closed set** | ch5 endpoints closed |
|---|---|---|---|---|---|---|
| `TM607_BUCK_LS_ZCD` | L6985–7064 | 3 | 1 | L7000 | {13,48,57,60,61,65,76,85,154,155} | **K48, K76** |
| `TM608_BOOST_HS_ZCD` | L7073–7151 | 5 | 3 | L7087 | {13,48,57,60,61,65,76,83,85} | **K48, K76** |
| `TM609_BOOST_HS_NEG` | L7160–7239 | 5 | 3 | L7170 | {13,48,57,60,61,65,76,83,85} | **K48, K76** |
| `TM616_VC_OFFSET` | L7411–7488 | **0** | 0 | L7429 | {13,85} | **none** |
| `TM640_BOOST_HS_OCP` | L7503–7590 | 5 | 3 | L7513 | {13,48,57,60,61,65,76,83} | **K48, K76** |
| `TM641_BST_UV` | L7606–7699 | **0** | 0 | L7623 | {13,46,48,60,61,65,76,85} | **K46, K48, K76** |
| `TM643_VBAT_LOOP_INDICTOR` | L7717–7813 | **0** | 0 | L7734 | {46,48,60,61,65,76,85} | **K46, K48, K76** |
| `TM1205_TRX_BST_UV_GD` | L8766–8877 | **0** | 0 | L8791 | {13,41,46,65} | **K46** |
| ″ | ″ | — | — | L8835 | {13,41,43,46,49,65} | **K46, K49** |
| **`TM600_HS_RDSON`** | **L9057–9204** | **10** | **7** | **L9081** | **{13,57,60,61,83,85,126}** | **NONE** |
| `TM601_LS_RDSON` | L9217–9353 | 3 | 1 | L9255 | {13,57,60,61,85,126,154,155} | **NONE** |

Comment-only lines that mention `SetOn` (e.g. `L6998`, `L7427`, `L8834`, `L9070`, `L9073`) are excluded.
`TM1205` is the **only** function here with two SetOn calls; its own comment (`L8834`
`// 路2: BST2-SW2 (重新 SetOn 切路 …)`) states the second call deliberately re-selects the path — which under
exclusivity means the first call's relays are released. That is intended there; the same pattern would be a
defect if unintentional (`cbite-qtmue.md:92–93`).

### 2.2 Corrected membership of the "drives the instrument AND closes the leg" set

The list circulated earlier of **six** functions (`TM607, TM608, TM609, TM616, TM640, TM641`) is superseded —
measured:

| set | members | count |
|---|---|---|
| drives the instrument (≥1 `.Set`) **and** closes the `K48/K76` leg | **`TM607`, `TM608`, `TM609`, `TM640`** | **4** |
| closes the leg but makes **0** `.Set` calls (holds the source off) | `TM641`, `TM643` (both via `K_FPVIH_TO_BST_A` = 46,48,76) | 2 |
| neither drives nor closes | `TM616` (body L7411–7488: 0 instrument mentions, 0 `K48/K76` tokens) | — |

`TM641`'s only instrument mention is a **comment** (`L7621`), and its `L7598` comment states the rule
explicitly: `K48/K76 与 ACM200_FH5(SW12_U1REF_BST_ACM) 共用接入 BST → 该源全程 RELAY_OFF 不驱动`.

---

## 3. Why that produces no conflict — and what the fix must therefore be

### 3.1 No cross-item leakage (from §1.1)
Every function in §2.1 issues its own complete `SetOn`. Because unlisted relays are released, a preceding
item cannot leave `K48/K76` closed into TM600, and TM600 cannot be relying on inherited state — it simply
**releases** them. The defect is an omission from TM600's own complete set, not interference.

### 3.2 No in-item competitor for ch5
Inside TM600 the only ch5 destination it wants is BST. TM600 needs no `SW1`/`SW2` (its `scopePins` are
PMID/SW/BST/VBAT/VDRV/V1P5/PGND/AGND), so the reroute implicit in closing `K48` costs TM600 nothing.

### 3.3 Why `K46` must NOT be added (`FACT` → `INFERENCE`)
`K46` sits on ch5's node (`NetK46_BUS_FH_SW1_S1_2` = {`K46.2`, `K48.6`, `S5_ACM200_FH5`}) and its other pin is
`FPVIe0_FH_BUS_S1`. Closing `K46` therefore joins **FPVIe0's high bus** to ch5's node — which is exactly what
`TM641`/`TM643` want (they close `K_FPVIH_TO_BST_A` and consequently keep the ACM source off), but **not** what
TM600 wants. Since exclusivity releases any relay TM600 does not list, **`K46` is OFF in TM600 by
construction**, so only ch5 reaches the BST node. (Close `K48+K76` without `K46` ⇒ single source on BST.)

### 3.4 Must the fix also "explicitly constrain `K49`"? — **No** (`FACT`)
With `K48` actuated, its COM (pin3/6) connects to its **NC** throw (pin4/5) → `K76` COM, and its **default
throw** (pin2/7, which feeds `K49`'s COM) is opened. So once `K48` is ON, `K49` sees no ch5 source and **its
state cannot affect ch5's destination**. `K49` is additionally released by exclusivity (it is not in TM600's
list). An explicit `K49` constraint would be redundant. `K110` likewise: it is not listed, hence released, so
`ch18`'s pins stay off the BST node.

### 3.5 The fix, expressed in the only place it can be expressed
```
test.cpp:9081  (TM600_HS_RDSON, the single SetOn call)
  BEFORE: K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap,
          K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP
  AFTER : the same list + K48_ACM5_AMP_REF + K76_ACM_BST        <- same call, not a second SetOn
```
`K46` is not added; `K49`/`K110` need no constraint. This is the "state discipline" the Captain asked about,
and it reduces to the two rules already documented in `cbite-qtmue.md`: **one call**, **complete set**. No new
mechanism (no per-item state table, no cleanup obligation) is required for the ch5 endpoints.

---

## 4. Two counts — settled, one line each (both prior figures retired)

The disagreement was a **scope + boundary** artefact, settled in t45 §4; recorded here once so both earlier
numbers are retired:

* **TM640** — `TM640_BOOST_HS_OCP` body = **L7503–7590**: instrument mentions **6** (5 `.Set` + 1 comment
  `L7512`), non-zero FV **3**, `K48`/`K76` tokens **2 each**, `SetOn` closing the leg **1** (`L7513`).
  *(Retires "7 mentions / 3 each" and "4 lines / 5 mentions".)*
* **TM600** — `.Set` calls **10** = **9 `RELAY_ON` + 1 `RELAY_OFF`** (`L9194`), non-zero FV **7**.
  *(Retires "9 non-zero" and "10 all RELAY_ON".)*

Method that produces these (and that the earlier figures lacked): boundary = `DUT_API` line → first
column-0 `}`; a comment block immediately preceding a declaration belongs to the **next** function; token
regex alias-inclusive (`K48(?![0-9])`, since `\bK48\b` misses `K48_ACM5_AMP_REF`).

---

## 5. `K110.pin4` / `K76.pin4` convergence (INFERENCE only)

`K76_ACM_BST_S1.pin4 = NetK76_ACM_BST_S1_4` and `K110_BST_S1.pin4 = NetK76_ACM_BST_S1_4`;
`K76.pin5 = K110.pin5 = NetK57_CAP_BST_SW_S1S2_3`. So the `K48→K76` leg and the `K110` (ch18) leg land on
**the same two nets**. Combined with §3.3, the invariant is:

> Closing `K48/K76` *gathers* whatever is enabled onto the BST node; the relay set does not select the source —
> **enablement does**. Within TM600 the set is single-source because `K46` and `K110` are released.

**Whether that has an electrical consequence at the DUT is UNKNOWN and is not mine to judge** (see §6). I do
not characterise the SW1 landing or the 20 V staircase as harmless or as fatal.

---

## 6. FACT / INFERENCE / UNKNOWN

**FACT**
1. `cbite.SetOn` is exclusive; unlisted relays are released (`cbite-qtmue.md:87–96`, user-corrected 2026-08-09).
2. ch5 endpoint set = `{K46, K48, K76, K49}` at pin level; `K41`/`K43` are on the FPVIe[L]→BST1/BST2 legs
   (pin nets in §2).
3. The census in §2.1 (bodies, `.Set` counts, expanded closed sets, ch5 endpoints per function).
4. TM600's single SetOn (`L9081`) contains **none** of the ch5 endpoints; TM601's (`L9255`) likewise none.
5. `TM1205_TRX_BST_UV_GD` is the only function in scope with two SetOn calls, and its own comment marks the
   second as a deliberate path re-selection.
6. §4 counts.

**INFERENCE**
1. Because a preceding item cannot leave ch5's endpoints closed, and TM600 needs no SW1/SW2, **TM600's
   `K48/K76` closure is isolatable** — no conflict, hence no requirement for a new per-item state mechanism.
   (From FACT 1, 3, 4.)
2. The fix must add `K48`+`K76` **to the existing single call**, and must not add `K46` (which would join
   FPVIe0's high bus to ch5's node). `K49` needs no explicit constraint, because an actuated `K48` opens the
   throw that feeds `K49`. (From FACT 1, 2, 3.)
3. `TM641`/`TM643` are the in-repo precedent for the *other* configuration (close `K46` too, hold the ACM
   source off) — the complement of TM600's required configuration. (From FACT 3, 5.)

**UNKNOWN** (not decided here)
1. The electrical consequence at the DUT of the current TM600 state (BST undriven; the staircase landing on
   SW1) — owner / bench decision. **Not mine to call harmless or fatal.**
2. Whether TM600/TM601 must be driven from ACM200 at all, and whether `PB0_BST_ACM` (ch18) + `[110]` is
   permitted — contract-owner decisions.
3. Whether the deployed `test.cpp` (`15c7d2b8…`) lags the payload (`2d0984d9…`) by design or pending landing.

---

## 7. Boundary

This file is the only artefact written by t47. **No writes** to the contract (rev 24, `fd00a508…`), test plan,
payload (`2d0984d9…`), gate scripts, `devel`, or the target tree; `t42`/`t44`/`t45`/`t46` artefacts are
untouched (hashes unchanged). Temporary scripts removed.

All evidence is **static connectivity + header/netlist/in-service-function-body text**. It is **not**
machine-measured and **not** an electrical conclusion; a green gate or a closed compile is not electrical
sign-off.

**Reproduce:**
```bash
python -c "import re;from pathlib import Path;ls=Path('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp').read_text(encoding='utf-8',errors='replace').splitlines();ds=[(i,m.group(1)) for i,x in enumerate(ls,1) for m in [re.search(r'DUT_API\s+\w+\s+(\w+)\s*\(',x)] if m];[print(i,ls[i-1].strip()[:180]) for i in (7000,7087,7170,7429,7513,7623,7734,8791,8835,9081,9255)]"
python -c "import csv;r=list(csv.reader(open('project/DALI/Dali-SCH.csv',encoding='utf-8-sig',newline='')));H=r[0];n=H.index('NetName');d=H.index('Designator');p=H.index('PinNumber');[print(x,[(y[p],y[n]) for y in r[1:] if y[d]==x]) for x in ('K46_BUS_FH_SW1_S1','K48_AMP_REF_S1','K49_ACM_SW2_S1','K76_ACM_BST_S1','K41_BUS_FL_BST_S1','K43_BST2_S1')]"
python -c "import re;s=open('knowledge/sources/cbite-qtmue.md',encoding='utf-8',errors='replace').read().splitlines();[print(i,l.strip()) for i,l in enumerate(s,1) if 61<=i<=96]"
```
