# t44 — Addendum to t42: ACM200 pin attribution for `SW12_U1REF_BST_ACM`

**Author:** schematic-expert · **Kind:** work (t42 addendum) · **Attempt:** 1
**Task:** record the hardening evidence for t42 (ACM200 pin attribution) so t43 can review it.
**Effect on the verdict: none.** t42's conclusion is **confirmed, not revised** — `SW12_U1REF_BST_ACM` drives
ACM200 **channel 5**, so its route to the BST pin needs **[48, 76]** and **not K110**.

**Artifact relations**

| File | Status | sha256 |
|---|---|---|
| `t42-acm200-pin-attribution.md` | **unchanged** — verdict of record | `8883daad0d22e669eeb1dd8038a3ad72591078413aed097473d33949300f4cfb` (19,351 B) |
| `t44-t42-addendum.md` | this file — evidence supplement | see `t44-t42-addendum-pin.json` |

t42 was already terminal when this evidence was assembled, so rather than mutate its hashed bytes this
addendum carries the additions. Read **t42 §0–§8 together with this file**; where they overlap, this file is
the more complete statement of the evidence hierarchy and it corrects one claim about the current tree.

---

## 1. Evidence hierarchy (strongest first) — and why the order matters

### Layer 1 — BEHAVIOURAL: human-authored call sites in the deployed tree (strongest)
The shipped BUCK/BOOST items close exactly this leg and name the instrument in the same breath:

```
test.cpp:7000  cbite.SetOn(K_FPVIH_TO_PGND_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW,
                           K48_ACM5_AMP_REF, K76_ACM_BST, K85_CAP_PMID, K65_nQON_PU, -1);   // TM607_BUCK_LS_ZCD
test.cpp:7087  ... K48_ACM5_AMP_REF, K76_ACM_BST ...                                        // TM608_BOOST_HS_ZCD
test.cpp:7170  ... K48_ACM5_AMP_REF, K76_ACM_BST ...                                        // TM609_BOOST_HS_NEG
test.cpp:7513  ... K48_ACM5_AMP_REF, K76_ACM_BST ...                                        // TM640_BOOST_HS_OCP
test.cpp:6997  //   BST  <- SW12_U1REF_BST_ACM: K48_ACM5_AMP_REF + K76_ACM_BST (FH5->BST)
test.cpp:7598  //   (!) K48/K76 与 ACM200_FH5(SW12_U1REF_BST_ACM) 共用接入 BST -> 该源全程 RELAY_OFF 不驱动
test.cpp:7621  // (!) K48/K76 同时把 ACM200_FH5(SW12_U1REF_BST_ACM) 输出端接 BST -> 该源全程 RELAY_OFF 不驱动
```
These are **executed** code, not declarations: they bind `SW12_U1REF_BST_ACM` to `ACM200_FH5` and to
`K48_ACM5_AMP_REF`+`K76_ACM_BST` in both the comment and the operand list. This layer alone settles the fork
and does not depend on interpreting `S5_5`, on the `FH<n>` numbering, or on any unused macro.

### Layer 2 — NAMING: the alias names carry the channel (header-internal)
`StdAfx.h:211 K48_ACM5_AMP_REF` — relay K48 is, by the project's own current naming, the **ACM channel 5**
relay. Companion aliases: `:224 K61_ACM8_SW` (ch 8), `:222 K59_ACM7_SDA` (ch 7), `:269 K102_ACM15_PC3`
(ch 15), `:279 K110_ACM18_BST` (ch 18). K48's pins 6/3 sit on the `S5_ACM200_FH5`/`SH5` net, so the naming
and the physical net agree without any appeal to what "FH5" means numerically.

### Layer 3 — DOCUMENTATION: exhaustive enumeration of the `ACM200 -> BST*` composite macros
Every composite macro in `StdAfx.h` whose comment attributes a BST route to a source:

| Locator | Macro | Relays | Comment source |
|---|---|---|---|
| `StdAfx.h:620` | `K_BST_ACM` | **48,76** | `ACM200[] -> BST: K48_ACM5_AMP_REF + K76_ACM_BST` |
| `StdAfx.h:619` | `K_BST2_ACM` | 43 | `ACM200[] -> BST2: K43_ACM4_BST2` |
| `StdAfx.h:377` | `K_FPVIH_TO_BST_A` | 46,48,76 | `FPVIe[H] -> BST` |
| `StdAfx.h:378` | `K_FPVIH_TO_BST_B` | 131,132,134,135 | `FPVIe[H] -> BST` |
| `StdAfx.h:451` | `K_FPVIL_TO_BST_A` | **109,110**,138,139,145,146 | `FPVIe[L] -> BST` |
| `StdAfx.h:452` | `K_FPVIL_TO_BST_B` | **109,110** | `FPVIe[L] -> BST` |
| `StdAfx.h:514` | `K_BST_QTMU` | 141,46,48,76 | `QTMU[S10_CH0_A] -> BST` |
| `StdAfx.h:556` | `K_BST_QVMH` | 137,46,48,76 | `QVM[H] -> BST` |
| `StdAfx.h:557` | `K_BST_QVML` | **109,110**,139 | `QVM[L] -> BST` |
| `StdAfx.h:447/448/449/450` | `K_FPVIL_TO_BST1_A/B`, `K_FPVIL_TO_BST2_A/B` | 41 / 41,43 / 138,139,145,146,41(,43) | `FPVIe[L] -> BST1/BST2` |
| `StdAfx.h:554/555` | `K_BST1_QVML`, `K_BST2_QVML` | 138,41 / 138,41,43 | `QVM[L] -> BST1/BST2` |

**Exhaustive result: the ACM200-attributed routes to BST/BST2 are `[48,76]` and `[43]` — never K110.** Every
K110-bearing BST macro is attributed to `FPVIe[L]` or `QVM[L]`/`QVM[低端]`.

> **Strength caveat, stated plainly:** `K_BST_ACM` and `K_FPVIL_TO_BST_B` have **1 definition and 0 call
> sites** each (measured: `test.cpp` 0/0, payload 0/0, `StdAfx.h` 1 def / 0 non-definition uses). Layer 3 is
> therefore **intent/documentation evidence, not behaviour**. The behavioural weight sits in Layer 1.

### Layer 4 — PHYSICAL: netlist net membership (authoritative `Dali-SCH.csv`)
```
channel 5  net NetK46_BUS_FH_SW1_S1_2 = {K46_BUS_FH_SW1_S1.2, K48_AMP_REF_S1.6, S5_ACM200_FH5}     <- no K110
channel 18 net NetK109_BUSL_PB0_S1_4  = {K109_BUSL_PB0_S1.4,  K110_BST_S1.6,    S5_ACM200_FH18}    <- no K48/K76
```
The two legs are **disjoint**: K110 is absent from channel 5's net and K48/K76 absent from channel 18's.

### Layer 5 — CONTROL GROUP: the enumeration is shared (5/5, measured)
macro channel == ACM alias number == netlist pin suffix, for every one of five instruments:

| Instrument | macro ch | alias | netlist pin | its net |
|---|---|---|---|---|
| `BST12_U1PS` | 4 | `K42_ACM4_AMP_PS` | `S5_ACM200_FH4` | `NetK41_BUS_FL_BST_S1_2` |
| **`SW12_U1REF_BST`** | **5** | **`K48_ACM5_AMP_REF`** | **`S5_ACM200_FH5`** | `NetK46_BUS_FH_SW1_S1_2` |
| `VDM_SDA` | 7 | `K59_ACM7_SDA` | `S5_ACM200_FH7` | `NetK58_BUSH_VDM_S1_4` |
| `VCP_SW` | 8 | `K61_ACM8_SW` | `S5_ACM200_FH8` | `NetK60_BUSL_VCP_S1_4` |
| `PB0_BST` | 18 | `K110_ACM18_BST` | `S5_ACM200_FH18` | `NetK109_BUSL_PB0_S1_4` |

Site-5 ACM200 F-pin suffixes present in the netlist: exactly `{0…23}` (24 = the documented ACM200 channel
count). So `_5` and `_18` are **two different channels**, and the macro's `_5` is not the same instance as
`FH18`.

### Layer 6 — IR cross-check
`S5_ACM200_FH5->BST_F_S1` / `SH5->BST_S_S1` → `requiredOnRelays = [48,76]`;
`S5_ACM200_FH18->BST_F_S1` / `SH18->BST_S_S1` → `[110]`.

---

## 2. Correction: the "current SetOn closes K109/K110" claim is only true of the payload

The gate-side handover described TM600's current state as "现 SetOn（含 K109/K110、无 48/76）". Measured now,
by file:

| Artifact | sha256 (python plaintext) | TM600 `SetOn` operands | BST leg | Verdict |
|---|---|---|---|---|
| **Deployed** `ForCodexDebug/source/test.cpp:9081` | `15c7d2b8d37b1564…` (469,714 B) | `K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP` | **neither** `48/76` nor `109/110` | **漏闭 only** |
| **Payload** `implementation-payload-TM600-TM601.cpp:219` | `2d0984d992d5d8cb…` (39,457 B) | the above **plus** `K109_BUSL1_PB0, K110_ACM18_BST` | `109/110` (ch18 / FPVIe[L] leg) | **闭错 + 漏闭** |

So "闭错" belongs to the **payload**; the **deployed** tree closes no BST source leg at all (it closes only
`K57_CAP_BST_SW`, the bootstrap capacitor, plus the PMID/SW/rails). `TM601` in both artifacts closes neither
leg (payload `:426`; deployed `:9255`) — consistent with t38's removal of TM601's ACM drive.

This distinction changes the disposition of the two items, not the verdict: the payload's defect is
`[109,110]` instead of `[48,76]`; the deployed tree's defect is the missing `[48,76]`.

---

## 3. Why the gate-side framing "macro says channel 5 vs netlist says FH18" dissolves

Both readings are the *same* 0..23 enumeration; `5 != 18`, so there is no macro-versus-netlist conflict:

* `S5_ACM200_FH18` / `SH18` sit on K110's COM pins **because K110 is channel 18's relay**
  (`K110_ACM18_BST`, `StdAfx.h:279`; K110 pins 6/3 = `NetK109_BUSL_PB0_S1_4/_S1_5`). That fact supports
  "channel 18 has a leg to BST via K110", **not** "`SW12_U1REF_BST_ACM` goes via K110".
* The netlist **does** locate channel 5's instance — as `S5_ACM200_FH5` on `NetK46_BUS_FH_SW1_S1_2`. It simply
  cannot be located by the *macro name*, which is why a name-based search returns the K110 hits only.

And the relay-pin labels in that handover (§③: `K110.4(NC)`, `K110.7(NO)`) are **correct as written**:
`knowledge/hardware/relays.md:31` states the latching G6K deliberately inverts ordinary intuition ("标注 NO 的
脚在默认无电时闭合，NC 脚在通电后才闭合"), and `:29` gives the mnemonic "默认 2-3 通、6-7 通；通电 3-4 通、
6-5 通". Their functional conclusion (energised → BST, default → PB0) matches `relays.md:29` and
`SCH-Connect-Map.txt:43` / `:724`. No correction is due there.

---

## 4. Consequences (both branches, as requested, with the branch that applies marked)

**Branch that applies — channel 5 / `[48,76]`:**
1. Required set for `SW12_U1REF_BST_ACM` → BST = **`[48,76]`**; with the SW end (`K61_ACM8_SW`) the BST–SW
   closed set is **`[48,61,76]`**.
2. `K110` is **not required for this instrument**; `[109,110]` is the **FPVIe[L]** route (`K_FPVIL_TO_BST_A/B`,
   contract `pinRouteTable … CH1 Low = [109,110]`). The contract's `'ACM200 S5_FH18 -> BST'` label on that set is
   the mis-attribution.
3. TM600: the payload's `K109/K110` is **闭错** (wrong leg, and `K109` pins 3/6 =
   `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`, dragging FPVIe1's low-domain BUS onto the BST node) — and the
   deployed tree additionally has **漏闭** of `[48,76]`.
4. t30's expectation set: after the contract rev+1 replaces the erroneous `[110,61]` with the BST `[48,76]`
   (+SW `[61]`), the expectation becomes **`[48,61,76]`**; t30 is contract-driven so it follows automatically.
5. t29 / t39 rest on "K110 required", which this evidence does not support; the closed-set question becomes
   `[48,76]` (if the ACM200 ground-referenced BST drive is required) or nothing.
6. Contract rev+1 (owner's call, not mine): `$.resources[2].channelsInScope.BST` → `S5_ACM200_FH5/SH5
   (K48_AMP_REF + K76_ACM_BST)`; `$.aliasResolution[3].resolution.relayChain` → `K48_ACM5_AMP_REF`,
   `K76_ACM_BST`; `$.aliasFlatTable[3].relayPath` accordingly; keep the ch18/FPVIe[L] data but re-label its
   source; amend `$.legacyKMap.mapping[2]` to three legs.

**Branch that does not apply — FH18 / `[110,61]`:** would require `SW12_U1REF_BST_ACM` to be channel 18, which
contradicts Layer 1 (executed code), Layer 2 (K48's `ACM5` alias on the FH5 net), Layer 3 (no ACM200-attributed
BST macro contains K110) and Layer 5 (5/5 control group). Recorded for completeness only; the two candidates
are **not** averaged and no middle set is proposed.

---

## 5. FACT / INFERENCE / UNKNOWN

**FACT** (each with locator; none machine-measured)
1. `Pin_Channel_define.h:20` `SW12_U1REF_BST_ACM = "S5_5,…"`; `:33` `PB0_BST = "S5_18,…"`.
2. `Pin_Channel_define.h:62` `_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE1_` = `S5_0…S5_23` (24 tokens); `:57` the
   ACM group's site-5 token set is exactly `{0…23}`; `hardware-specs.md` ACM200 = 24 channels.
3. `StdAfx.h:69` `extern ACM200 SW12_U1REF_BST_ACM;`; `:82` `extern ACM200 PB0_BST_ACM;`; extern order
   `:64-87` mirrors the macro table.
4. Alias channels: `StdAfx.h:211 K48_ACM5_AMP_REF`, `:224 K61_ACM8_SW`, `:222 K59_ACM7_SDA`,
   `:269 K102_ACM15_PC3`, `:279 K110_ACM18_BST`.
5. `StdAfx.h:620 K_BST_ACM = 48,76  // ACM200[] -> BST: K48_ACM5_AMP_REF + K76_ACM_BST`;
   `:619 K_BST2_ACM = 43 // ACM200[] -> BST2`; `:452 K_FPVIL_TO_BST_B = 109,110 // FPVIe[L] -> BST`.
   `K_BST_ACM`: 1 definition, 0 call sites (measured in all three files).
6. Netlist: `NetK46_BUS_FH_SW1_S1_2 = {K46.2, K48.6, S5_ACM200_FH5}`;
   `NetK109_BUSL_PB0_S1_4 = {K109.4, K110.6, S5_ACM200_FH18}`; site-5 F-pin suffixes = `{0…23}`.
7. `SCH-Connect-Map.txt:673/674` ch5 → K48 → K76 → BST; `:724/725` ch18 → K110(NC) → PB0.
8. IR `paths[]`: ch5→BST `[48,76]`; ch18→BST `[110]`.
9. Deployed `test.cpp:7000/7087/7170/7513` close `K48_ACM5_AMP_REF`+`K76_ACM_BST`; `:6997/:7598/:7621`
   name `SW12_U1REF_BST_ACM` and `ACM200_FH5` together.
10. Deployed `test.cpp:9081` (TM600) and `:9255` (TM601) close neither `48/76` nor `109/110`; payload
    `:219` closes `K109_BUSL1_PB0, K110_ACM18_BST`; payload `:426` closes neither.
11. `K109_BUSL_PB0_S1` pins 3/6 = `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`.
12. `relays.md:29/31` latching-relay convention (NO closed when de-energised, NC when set).
13. Header copies identical: `Pin_Channel_define.h` sha256 `d5ce16a0…`, 10,934 B.

**INFERENCE**
1. `S5_5` = site-5 ACM200 channel 5, because the site token enumerates `0..23` and the device has 24 channels
   (FACT 1,2) — reinforced by FACT 3 (extern order) and FACT 5 (alias channel numbers).
2. Channel 5's instance is the one named by `SW12_U1REF_BST_ACM`, because the alias `K48_ACM5_AMP_REF` sits on
   channel 5's net and the executed call sites pair that relay with that instrument name (FACT 4,6,9).
3. Required set is `[48,76]`; `[110]` belongs to channel 18 (FACT 5,6,7,8), which is a different ACM200
   object, `PB0_BST_ACM`.
4. The contract's `'ACM200 S5_FH18 -> BST'` attribution is the mis-labelled member: the same map applies the
   channel rule correctly for SW/INT/VDM (FACT 4), and no ACM200-attributed macro contains K110 (FACT 5).
5. Payload = 闭错+漏闭; deployed tree = 漏闭 only (FACT 10).

**UNKNOWN** (not decided here, not assumed)
1. Whether TM600/TM601 **must** drive BST from ACM200 at all — the ruling says the rail "stays the
   ground-referenced `SW12_U1REF_BST_ACM` form", yet the deployed items close no BST source leg. Owner's call.
2. Whether switching to `PB0_BST_ACM` (ch18) + `[110]` is permitted — physically reachable, changes the
   declared instrument; needs its own ruling.
3. Whether `K_BST_ACM`'s 0-call-site state means the ACM200 BST drive was intentionally abandoned rather than
   merely not yet wired. Documentation vs behaviour cannot be resolved from static files.
4. Relay contact current rating / any electrical behaviour. **Nothing here is machine-measured; a green gate
   or a successful compile is not electrical sign-off.**

---

## 6. Reproduction

```bash
# channel tokens and the site/bind enumeration
python -c "p=open('project/DALI/Pin_Channel_define.h',encoding='utf-8',errors='replace').read().splitlines();print(p[19].strip());print(p[32].strip());print(p[61][:120])"
# relay alias channel numbers
python -c "import re;s=open('D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h',encoding='utf-8',errors='replace').read().splitlines();print([(i+1,l.strip()) for i,l in enumerate(s) if re.search(r'#define\s+K(48|61|76|109|110)_',l)])"
# every source-attributed BST composite macro (exhaustive enumeration)
python -c "import re;s=open('D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h',encoding='utf-8',errors='replace').read().splitlines();[print(i+1,l.strip()) for i,l in enumerate(s) if re.search(r'#define\s+K_\w*BST\w*\s+[0-9,\s]+//',l)]"
# net membership separation
python -c "import csv;rows=list(csv.reader(open('project/DALI/Dali-SCH.csv',encoding='utf-8-sig',newline='')));H=rows[0];i_n=H.index('NetName');i_m=H.index('MemberName');[print(n,[r[i_m] for r in rows[1:] if r[i_n]==n]) for n in ('NetK46_BUS_FH_SW1_S1_2','NetK109_BUSL_PB0_S1_4')]"
# executable call sites (behavioural layer)
python -c "import re;t=open('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp',encoding='utf-8',errors='replace').read().splitlines();[print(i+1,l.strip()[:170]) for i,l in enumerate(t) if 'K48_ACM5_AMP_REF' in l][:8]"
```
All reads must go through python (DLP-transparent-encrypted sources; PowerShell returns ciphertext).

**Task verify (t42's):** `python -c 'import json,sys;d=json.load(open("team/artifacts/acceptance-20260916-dali10/schematic-ir.json",encoding="utf-8-sig"));print(type(d).__name__)'` → `dict`, exit 0.

---

## 7. Scope discipline

Only this file (and its hash pin) were created by t44. t42's deliverable was **not** modified, so its reported
hash `8883daad…` remains valid. No writes to the contract, test plan, payload, gate scripts, `devel`, or the
target tree. Temporary evidence scripts were removed. Independent review of t42 + this addendum is t43
(rule-reviewer); the author does not self-review.
