# t42 — ACM200 pin attribution for `SW12_U1REF_BST_ACM`: channel 5, not channel 18

**Author:** schematic-expert · **Kind:** requirements (independent adjudication) · **Attempt:** 1
**Scope of this file:** judgement + handling recommendation + locators only. No product file was modified
(the contract, test plan, payload, gates and both source trees are untouched).

---

## 0. Verdict (single answer)

**`SW12_U1REF_BST_ACM` drives ACM200 channel 5.** Therefore the BST leg for this instrument is

```
S5_ACM200_FH5 / S5_ACM200_SH5  ->  K48_ACM5_AMP_REF  ->  K76_ACM_BST  ->  BST_F / BST_S
required relays = [48, 76]        (K110 is NOT required)
```

Answer **(a)** of the task is correct and answer (b) is wrong. `K110_BST` (`K110_ACM18_BST`) belongs to the
**different** ACM200 object `PB0_BST_ACM`, which is channel 18. The two objects are distinct instruments;
`K110` is not needed for `SW12_U1REF_BST_ACM`.

For the BST–SW pair driven by ACM200 with the ground-referenced instrument named in the contract, the
complete closed set is **BST `[48,76]` + SW `[61]` = `[48,61,76]`** (SW end: `S5_ACM200_FH8/SH8 -> K61_ACM8_SW`).
`[110,61]` is valid only for the *channel-18* alternative, i.e. only if the instrument is renamed to
`PB0_BST_ACM`.

---

## 1. Why the notation question had to be settled from the header, not from the name

The macro is `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_` = `"S5_5,S6_5,S11_5,S12_5,S21_5,S22_5,S27_5,S28_5"`
(`D:\PROJECT6-DALI\ForCodexDebug\source\Pin_Channel_define.h:20`).

The header declares its own provenance and forbids editing:
`Pin_Channel_define.h:1` `//Pin_Channel_define.h : Channel string for pin or site bind`;
`:3` `//The following code was created for STS PinPlanner,don't modify`.

So the token after the site is **the ACM200 channel index**, not a pin number. That is provable from the
header itself, three ways — no naming intuition is used:

| # | Proof | Locator |
|---|-------|---------|
| 1 | `_PIN_SITE_BIND_DEFINE_MD_ACM200_SITE1_` = `"S5_0,S5_1,…,S5_23"` — exactly 24 site-5 channel tokens, i.e. indices `0..23` | `Pin_Channel_define.h:62` |
| 2 | `_GROUP_CHANNEL_DEFINE_ACM_GRP_` enumerates the same site-5 tokens `S5_1,S5_4,S5_13,…,S5_7` — the set of second tokens is exactly `{0,…,23}` | `Pin_Channel_define.h:57` |
| 3 | The 24 `_PIN_CHANNEL_DEFINE_*_ACM_` macros at `:15 – :38` appear in strict channel order, and each macro's channel is the same index: `:15`=S5_0 … `:20`=S5_5 … `:33`=S5_18 … `:38`=S5_23 | `Pin_Channel_define.h:15-38` |

Third-party confirmation that a 24-channel ACM200 is the physical device:
`knowledge/sources/hardware-specs.md` module table, ACM200 row = **24 channels** (`| **ACM200** | — | 24 |`).

Hence: **`S5_5` = site 5, ACM200 channel 5** — and `SW12_U1REF_BST_ACM` is the ACM200 object of channel 5.

### 1.1 An independent second binding: the relay alias names in StdAfx.h

The current target header encodes the channel **in the relay alias name**, and those aliases form a complete
monotonic map that agrees with the macro table index-for-index:

| StdAfx extern (L) | Pin_Channel_define macro (L) | alias carrying `ACM<n>` | channel |
|---|---|---|---|
| `:64 VAC123_AMUX_ACM` | `:15 VAC123_AMUX` | `K18/K19/K20_ACM0_*` | 0 |
| `:65 ACDRV123_VCC_ACM` | `:16 ACDRV123_VCC` | `K22…K25_ACM1_*` | 1 |
| `:66 SCL_VACWL_ACM` | `:17 SCL_VACWL` | `K33_ACM2_VAC_WL` | 2 |
| `:67 KLV12_PGNDWL_ACM` | `:18 KLV12_PGNDWL` | `K36/K37_ACM3_*` | 3 |
| `:68 BST12_U1PS_ACM` | `:19 BST12_U1PS` | `K42/K43_ACM4_*` | 4 |
| **`:69 SW12_U1REF_BST_ACM`** | **`:20 SW12_U1REF_BST`** | **`K48_ACM5_AMP_REF`, `K49_ACM5_SW2`** | **5** |
| `:70 LG1_LG2_ACM` | `:21 LG1_LG2` | `K52_ACM6_LG2` | 6 |
| `:71 VDM_SDA_ACM` | `:22 VDM_SDA` | `K59_ACM7_SDA` | 7 |
| `:72 VCP_SW_ACM` | `:23 VCP_SW` | `K61_ACM8_SW` | 8 |
| `:74 VBUS_DRVH1_ACM` | `:25 VBUS_DRVH1` | `K4_ACM10_DRVH1` | 10 |
| **`:82 PB0_BST_ACM`** | **`:33 PB0_BST`** | **`K110_ACM18_BST`** | **18** |
| `:87 PA7_PD2_ACM` | `:38 PA7_PD2` | `K121_ACM23_PD2` | 23 |

Locators: `D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h:64-87` (externs),
`StdAfx.h:160,174-185,193-197,203-204,211-212,215,222,224,228,260,263-264,266,269,273,276,279,282,285,288,291,294,333`
(aliases). Two `BST`-bearing objects exist and they are **not** the same instrument:

* `SW12_U1REF_BST_ACM` → channel **5** → BST leg through `K48`+`K76`
* `PB0_BST_ACM` → channel **18** → BST leg through `K110`

**This is the trap:** `SW12_U1REF_BST_ACM` and `PB0_BST_ACM` both contain the literal string `BST`, and
`K110_ACM18_BST` and `K76_ACM_BST` both contain `BST`. Matching on the string finds the wrong pair.

---

## 2. Netlist confirmation (authoritative `project/DALI/Dali-SCH.csv`)

Pin-level net membership shows which instrument hangs on which BST leg:

```
net NetK46_BUS_FH_SW1_S1_2 : K46_BUS_FH_SW1_S1.2 , K48_AMP_REF_S1.6 , S5_ACM200_FH5
net NetK46_BUS_SH_SW1_S1_2 : K46_BUS_SH_SW1_S1.3 , K48_AMP_REF_S1.3 , S5_ACM200_SH5
net NetK109_BUSL_PB0_S1_4  : K109_BUSL_PB0_S1.4  , K110_BST_S1.6    , S5_ACM200_FH18
net NetK109_BUSL_PB0_S1_5  : K109_BUSL_PB0_S1.5  , K110_BST_S1.3    , S5_ACM200_SH18
```

`Dali-SCH.csv` rows for `NetName=NetK46_BUS_FH_SW1_S1_2` (member `S5_ACM200_FH5`) and
`NetName=NetK109_BUSL_PB0_S1_4` (member `S5_ACM200_FH18`); relay pin nets under
`Designator=K48_AMP_REF_S1` (pins 6/3), `K76_ACM_BST_S1` (pins 3/6 → 5), `K109_BUSL_PB0_S1` (pins 3/6),
`K110_BST_S1` (pins 6/3, 5, 4).

* Channel **5** sits on the **`K46/K48` node** — i.e. at the *input* of K48. Routing it to BST needs
  K48 and K76: **`[48,76]`**. (K46 is the FPVIe0-CH0-high BUS relay, which is on the same wire but is not
  traversed by the channel-5 route — hence the IR's `[48,76]`, without 46.)
* Channel **18** sits on the **`K109/K110` node** — at the input of K110. Its default path is
  `K110(Relay-NC) -> PB0_F/PB0_S`, and only K110 actuated steers it to BST: **`[110]`**.

Route headers, `project/DALI/SCH-Connect-Map.txt`:

* `:673` `F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F`
* `:674` `S: S5_ACM200_SH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_S`
* `:724` `F: S5_ACM200_FH18 -> K110(Relay-NC) -> PB0_F`
* `:725` `S: S5_ACM200_SH18 -> K110(Relay-NC) -> PB0_S`
* `:39` `CH0 High -> BST  [Kelvin]  需闭合: K46,K48,K76`   (FPVIe0 route, a different source)
* `:42` `CH0 Low -> BST  [Kelvin]  需闭合: K109,K110,K138,K139,K145,K146`   (FPVIe low-domain route)
* `:268` `CH1 Low -> BST  [Kelvin]  需闭合: K109,K110`   (FPVIe1 low-domain route)

Note K109's pins are `FPVIe1_FL_BUS_S1` (pin 3) and `FPVIe1_SL_BUS_S1` (pin 6): the `K109/K110` leg is
**FPVIe's low-domain leg to BST**, shared with ACM200 channel 18 — it is not an ACM200-only leg.

---

## 3. `schematic-ir.json` cross-check

| IR path id | `requiredOnRelays` | `relayChain` |
|---|---|---|
| `S5_ACM200_FH5->BST_F_S1` | `[48, 76]` | `K48_AMP_REF_S1`, `K76_ACM_BST_S1` |
| `S5_ACM200_SH5->BST_S_S1` | `[48, 76]` | `K48_AMP_REF_S1`, `K76_ACM_BST_S1` |
| `S5_ACM200_FH18->BST_F_S1` | `[110]` | `K110_BST_S1` |
| `S5_ACM200_SH18->BST_S_S1` | `[110]` | `K110_BST_S1` |

Locator: `team/artifacts/acceptance-20260916-dali10/schematic-ir.json` → `paths[]` with
`dutPin == "BST"` (accepted PathProofs, engine `native_csv_graph_v2`).

Both routes physically exist. The IR therefore cannot by itself decide which *instrument object* owns which
channel — that decision comes from §1/§1.1, and it selects channel 5 for `SW12_U1REF_BST_ACM`.

---

## 4. The contract's internal contradiction, and what is authoritative

`team/artifacts/acceptance-20260916-dali10/setup-contract.json` contains **both** answers:

| Contract entry | Value | Consistent with |
|---|---|---|
| `$.tmDeltas.TM600.pinRouteTable.BST.列6` (`ACM200 → PIN (Share继电器)`) | `needsClosed = [48, 76]` | **channel 5 ✔** |
| `$.tmDeltas.TM1205.pinRouteTable.BST.列6` | `needsClosed = [48, 76]` | **channel 5 ✔** |
| `$.resources[2].channelsInScope.SW` | `S5_ACM200_FH8/SH8 (K61_SW)` | channel 8 ✔ (`K61_ACM8_SW`) |
| `$.resources[2].channelsInScope.INT` | `S5_ACM200_FH15/SH15 (K102_PC3)` | channel 15 ✔ (`K102_ACM15_PC3`) |
| `$.resources[2].channelsInScope.VDM` | `S5_ACM200_FH7/SH7 (K59_SDA)` | channel 7 ✔ (`K59_ACM7_SDA`) |
| **`$.resources[2].channelsInScope.BST`** | **`S5_ACM200_FH18/SH18 (K110_BST)`** | **channel 18 ✘ — the sole outlier** |
| **`$.aliasResolution[3].resolution.relayChain[0].relay`** | **`K110_ACM18_BST`** | **✘** |
| **`$.aliasFlatTable[3].relayPath`** | **`K110_ACM18_BST -> K61_ACM8_SW`** | **✘** |
| `$.aliasResolution[3].resolution.forceInstrument` | `SW12_U1REF_BST_ACM` (quotes the macro `'S5_5,S6_5,…'`) | channel 5 ✔ — and it is the *same object string* as the two rows above, which is the contradiction |
| `$.legacyKMap.mapping[2].current` | `K46+K48+K76 (FPVIe0 CH0 high) or K109+K110 (FPVIe1 CH1 low)` | partially right; **omits the ACM200 channel-5 leg entirely** |
| `$.resources[19]` = `K110_BST_S1` | role "BST select relay (ACM200 and FPVIe low-domain share it)" | right about the sharing, silent on which channel index |

**Decisive internal-consistency argument:** the same `channelsInScope` mapping uses the correct rule for
SW (8), INT (15) and VDM (7) — in each case the channel number is exactly the ACM channel in the alias name
and the macro index. BST is the one entry that breaks the rule, and it breaks it by picking the relay whose
*name* contains `BST` rather than the channel that the `SW12_U1REF_BST_ACM` macro names.

### Recommended handling (recommendation only — this task must not edit the contract)

1. **Authority order for the ACM200 side:** ① `Pin_Channel_define.h` macro (PinPlanner-generated, header
   declares it non-editable) ② `StdAfx.h` channel-bearing alias names ③ the CSV net membership — all three
   agree on channel 5 / `[48,76]`. Treat the machine-generated `pinRouteTable.列6 = [48,76]` as the correct
   ACM200-side entry and keep it.
2. **Correct these three contract entries in the next revision** (contract owner, not t42):
   `resources[2].channelsInScope.BST` → `S5_ACM200_FH5/SH5 (K48_AMP_REF+K76_ACM_BST)`;
   `aliasResolution[3].resolution.relayChain[0].relay` → `K48_ACM5_AMP_REF` then `K76_ACM_BST`;
   `aliasFlatTable[3].relayPath` → `K48_ACM5_AMP_REF -> K76_ACM_BST -> BST, K61_ACM8_SW -> SW`.
   Closed set becomes **`[48,61,76]`**.
3. **Keep the channel-18 data but re-label it.** `K110_ACM18_BST` / `K109_BUSL1_PB0` are real and belong to
   `PB0_BST_ACM` (channel 18) and to the FPVIe low-domain leg. `aliasResolution[3].alternatives[0]`
   (the "two independent single-ended sources … ACM200 FH18 → BST via K110_BST" fallback) is the only place
   where `[110,61]` is correct — so if that fallback is adopted, the instrument must be **renamed to
   `PB0_BST_ACM`**, and the contract must not keep the `SW12_U1REF_BST_ACM` name beside `K110`.
4. **Amend `legacyKMap.mapping[2]`** to record three distinct legs: FPVIe0-CH0-high `[46,48,76]`,
   ACM200 channel 5 `[48,76]`, FPVIe low-domain / ACM200 channel 18 `[109,110]`.
5. With (2) applied, `setup-contract` no longer pairs a channel-5 instrument with a channel-18 relay set and
   the ACM200-side pinRouteTable stops being "an outlier that happens to be right".

---

## 5. Delivery-state check (the task's "does the deliverable/deployed state lack 48/76?" question)

Three states exist and they differ:

| State | Locator | BST leg closed | Verdict |
|---|---|---|---|
| Human-authored precedent (BUCK/BOOST items) | `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp:7000,7087,7170,7513` inside `TM607_BUCK_LS_ZCD`, `TM608_BOOST_HS_ZCD`, `TM609_BOOST_HS_NEG`, `TM640_BOOST_HS_OCP` (also `:7500,7597,7621,7713` of `TM616/TM640/TM641`) | `K48_ACM5_AMP_REF`, `K76_ACM_BST` | **correct leg**, and the comments state the binding explicitly |
| Payload (t16 output) | `team/artifacts/…/implementation-payload-TM600-TM601.cpp:219` | `K109_BUSL1_PB0, K110_ACM18_BST` — **no 48/76** | **wrong leg** (channel 18 for a channel-5 instrument) |
| Currently deployed TM600/TM601 | `test.cpp:9081` (`TM600_HS_RDSON`), `:9255` (`TM601_LS_RDSON`) | neither `48/76` nor `109/110` | no BST source leg at all |

The precedent even documents the resource rule and the trap:
`test.cpp:7598` `//   ⚠ K48/K76 与 ACM200_FH5(SW12_U1REF_BST_ACM) 共用接入 BST → 该源全程 RELAY_OFF 不驱动` and
`test.cpp:7621` `// ⚠ K48/K76 同时把 ACM200_FH5(SW12_U1REF_BST_ACM) 输出端接 BST → 该源全程 RELAY_OFF 不驱动`.
The deployed code names the pair **`ACM200_FH5` + `SW12_U1REF_BST_ACM`** in the same breath — an explicit,
in-code confirmation of §1 that post-dates the contract's erroneous entry.

**So:** yes — the payload lacks `48,76`. Per the task's phrasing, the true defect is the **missing `[48,76]`
channel-5 leg, not a missing `K110`**; and the payload's `K109` additionally ties the *FPVIe1 low-domain bus*
(`FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1`) into the BST node, so in TM600 it energises a relay set that does not
connect the instrument the contract names. Whether the deployed TM600/TM601 *must* drive BST from ACM200 at
all is a separate requirement question (§6, UNKNOWN) — but if ruling (ii)'s ground-referenced ACM200 BST drive
is required, the correct addition is `K48`+`K76`, and both the payload's `[109,110]` and the deployed
"no BST leg" are deficient.

---

## 6. FACT / INFERENCE / UNKNOWN

### FACT (read directly, each with locator; none is machine-measured)
1. `_PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_` = `"S5_5,…"` — `Pin_Channel_define.h:20`.
2. The site/bind macro lists `S5_0…S5_23` (24 tokens) — `Pin_Channel_define.h:62`; the ACM group macro's
   site-5 token set is exactly `{0…23}` — `Pin_Channel_define.h:57`.
3. The 24 ACM macros occupy `:15-:38` in channel order — `Pin_Channel_define.h:15-38`.
4. ACM200 is a 24-channel device — `knowledge/sources/hardware-specs.md` module table (ACM200 row).
5. `extern ACM200 SW12_U1REF_BST_ACM;` at `StdAfx.h:69`; `extern ACM200 PB0_BST_ACM;` at `StdAfx.h:82`.
6. Alias names carry the channel: `K48_ACM5_AMP_REF` (`StdAfx.h:211`), `K61_ACM8_SW` (`:224`),
   `K110_ACM18_BST` (`:279`), `K102_ACM15_PC3` (`:269`), `K59_ACM7_SDA` (`:222`).
7. CSV net membership: `S5_ACM200_FH5` shares `NetK46_BUS_FH_SW1_S1_2` with `K46.2` and `K48.6`;
   `S5_ACM200_FH18` shares `NetK109_BUSL_PB0_S1_4` with `K109.4` and `K110.6`.
8. `SCH-Connect-Map.txt:673/674` route ch5 → `K48,K76` → BST; `:724/725` route ch18 → `K110(NC)` → PB0.
9. IR `paths[]`: ch5 → BST `requiredOn=[48,76]`; ch18 → BST `requiredOn=[110]`.
10. Contract `$.tmDeltas.TM600.pinRouteTable.BST.列6` = `[48,76]` while
    `$.resources[2].channelsInScope.BST` = `S5_ACM200_FH18/SH18 (K110_BST)` and
    `$.aliasResolution[3].resolution.relayChain[0].relay` = `K110_ACM18_BST`.
11. Deployed precedent closes `K48_ACM5_AMP_REF`+`K76_ACM_BST` and names them `ACM200_FH5` +
    `SW12_U1REF_BST_ACM` — `test.cpp:7000,7598,7621`.
12. `K109_BUSL_PB0_S1` pins 3/6 are `FPVIe1_FL_BUS_S1`/`FPVIe1_SL_BUS_S1` — CSV `Designator=K109_BUSL_PB0_S1`.
13. Both `Pin_Channel_define.h` copies (workspace and debug tree) are byte-identical,
    sha256 `d5ce16a0ae79549424110755e99d9ae74cce79d18b8a1eaae3fd5588df285e35`, 10,934 B.

### INFERENCE
1. Because the site token enumerates `0..23` and ACM200 has 24 channels, `S5_5` denotes site-5 ACM200
   channel 5 and `S5_23` the 24th, so `SW12_U1REF_BST_ACM` is bound to channel 5. (FACT 1–4.)
2. Because channel 5's net sits at K48's input and K48→K76→BST is the only ACM200 route out of that net,
   the required set for `SW12_U1REF_BST_ACM` is `[48,76]`, and `[110]` — whose net is K110's input, reached
   only by channel 18 — is not required. (FACT 6–9.)
3. The contract's `channelsInScope.BST` entry is the erroneous one: the same map applies the macro-channel
   rule correctly to SW/INT/VDM, and the ACM-object string `SW12_U1REF_BST_ACM` is quoted in the very entry
   that carries the channel-18 relay. (FACT 4–6, 10.)
4. The payload inherited that error rather than inventing it (it cites the contract's route table), and its
   "required" reasoning about K110 is valid only for the channel-18 object. (FACT 10; payload `:205-219`.)

### UNKNOWN (not decided here, not assumed)
1. **Whether TM600/TM601 must drive BST from ACM200 at all.** The deployed items close
   `K57_CAP_BST_SW` but no BST source leg; ruling (ii) says the BST–SW rail "stays the ground-referenced
   `SW12_U1REF_BST_ACM` form". Reconciling those two needs the ruling's owner, not this task.
2. **Whether `PB0_BST_ACM` (channel 18) may be used instead.** It is a physically valid route to BST via
   `[110]`, but adopting it changes the declared instrument and would need its own ruling.
3. **Electrically verified behaviour.** Nothing here is machine-measured; all of it is netlist/document
   reading. Compilation or a green gate does **not** constitute electrical sign-off.
4. **Whether the contract owner's `列6 = [48,76]` was machine-generated.** Asserted from its agreement with
   `SCH-Connect-Map.txt:673` — plausible but not proven from the generator source.

---

## 7. Reproduction commands (run from the workspace root; python is required for the DLP-encrypted files)

```bash
python -c "import re;p=open('project/DALI/Pin_Channel_define.h',encoding='utf-8',errors='replace').read().splitlines();print(p[19]);print(p[32]);print(p[56][:120]);print(p[61][:120])"
python -c "import re;s=open('D:/PROJECT6-DALI/ForCodexDebug/source/StdAfx.h',encoding='utf-8',errors='replace').read().splitlines();print([ (i+1,l.strip()) for i,l in enumerate(s) if re.search(r'K(48|61|76|109|110)_',l)])"
python -c "import re;m=open('project/DALI/SCH-Connect-Map.txt',encoding='utf-8',errors='replace').read().splitlines();print(m[672]);print(m[673]);print(m[723]);print(m[724])"
python -c "import json;d=json.load(open('team/artifacts/acceptance-20260916-dali10/schematic-ir.json',encoding='utf-8-sig'));print([(p['from'],p['requiredOnRelays'],[r['relay'] for r in p['relayChain']]) for p in d['paths'] if p['dutPin']=='BST' and p['from'].startswith('S5_ACM200')])"
python -c "import json;c=json.load(open('team/artifacts/acceptance-20260916-dali10/setup-contract.json',encoding='utf-8-sig'));print(c['resources'][2]['channelsInScope']);print(c['aliasFlatTable'][3]['relayPath'])"
```

**Task-mandated verify command** (must exit 0):
`python -c 'import json,sys;d=json.load(open("team/artifacts/acceptance-20260916-dali10/schematic-ir.json",encoding="utf-8-sig"));print(type(d).__name__)'`

---

## 8. Impact and independent review

**Impact:** this changes the relay set t29 plans around. If TM600 requires the ACM200 ground-referenced BST
drive, the correct set is `[48,61,76]` and **not** `[109,110,61]`; the current deployment closes neither, so
a TM600 item that assumes ACM200 holds BST−SW at 5 V would not be exercising what the contract declares.
Nothing here is proven by measurement.

**Independent review requested** (the author must not self-review): please have `rule-reviewer` check (i) that
the site-token semantics are read from the header rather than assumed, (ii) that channel 5 / `[48,76]` is the
unique reading of FACT 1–9, and (iii) that no product file was modified by this task. This file is the only
artefact t42 wrote.
