# Independent adversarial review (R7) — TM600/TM601 BST claims C1–C6

> Reviewer role: independent adversarial reviewer, read-only. Started by the orchestrating agent with the six claims below.
> Method: every text file was read with python `open(path,'rb')`; every line quoted below is what I read at the cited locator.
> Boundary: I changed **nothing** except this one report file. No target-tree write, no `D:/PROJECT6-DALI/devel` access, no gate/contract/script write.
> **No hardware / no bench**: every electrical conclusion here is documentary, not measured.

---

## 0. Hash and identity check (my own computation, before any verdict)

| Object | C1/C2/C3 quoted | I computed (python, SHA-256) | Match |
|---|---|---|---|
| `project/DALI/Dali_testmode.xlsx` | `f4bbb856…569564`, 2026-09-16 21:46:39 | 12,210,680 B / `f4bbb8569763784c500974121fca0d18dc3018061c50875e49c8da1fa0569564` (**first read**) | ✅ |
| `D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp` | `15c7d2b8…236c01a`, 469,714 B | 469,714 B / `15c7d2b8d37b15648d552ad5dde14e57b5c0d520d05a41c8c41492a06236c01a` | ✅ |
| `project/DALI/SCH-Connect-Map.txt` | `cc8009fb…` | 66,403 B / `cc8009fbb27eef0cf29b45e4e50b05e1b5d7b5d49095a32005261a79d83cb427` | ✅ |
| `knowledge/hardware/voltage-inference.md` | (no hash given) | 5,082 B / `6eb9dea919bb6ed193099e52225e808af1515a9250240e94f2013e1847507b27` | — |
| `knowledge/hardware/relays.md` | (no hash given) | 13,624 B / `8029ee13690ca2158e48ea002bad69f2d943d76126bb133b4e54b8401934fcdb` | — |

### 0.1 **[NEW, high impact] The "sole authority" workbook drifted on disk during this review**

- My first read of `project/DALI/Dali_testmode.xlsx` returned **12,210,680 B / `f4bbb856…`** — identical to C1 and identical to the run's own pin `team/artifacts/tm601r3-20260916/pin/snapshot-manifest.json` (`/files/dft_xlsx/sha256 = f4bbb856…`, `/files/dft_xlsx/mtime = 2026-09-16 21:46:39`).
- Re-reading the **same path** later in the same session returned **10,677,032 B / `0b0480a290581fd3d10ec9db7aef45664949174bb8f1a94e926f24cfa582abbd`, mtime `2026-09-16 22:13:39`** (my clock at that moment: 22:17:04).
- Content comparison of the two revisions: identical for the two rows under review, but **the row locators moved** — TM600 HS_RDSON is now OVERVIEW **row 21** and TM601 LS_RDSON is OVERVIEW **row 22** (old revision: rows 132 / 133), and only **2** rows of the TM5xx/TM6xx family remain (old revision had TM510, TM511, TM600, TM601, TM602, TM603 in six consecutive rows). Shared-string count 2318 → 781.

FACT: the file at that path is not the same byte object that C1 anchors to; TM601's row is no longer "row 133".
FACT: the pinned snapshot (`pin/snapshot-manifest.json`) still records the old object, so C1's metadata came from the pin, not from fabrication.
UNKNOWN: **why** it changed (user re-save vs. a filtered/derived workbook vs. a redaction layer). I have no way to attribute it from inside this sandbox.
CONSEQUENCE: every claim keyed to "OVERVIEW row 133" and to the xlsx hash is valid only against the **pin**; anyone re-opening the live file must re-locate by `Item=TM601` / `Name=LS_RDSON`, not by row number, and must re-hash. I use the **pinned revision (`f4bbb856…`)** as C1's referent throughout, and I re-confirmed the two rows' content independently in the **new** revision (identical E/F/L/Q/AH).

---

## 1. Claim-by-claim verification

### C1 — workbook is the modified DFT; row 133 gained `vset[bst,5,100e-6,0]`; row 132 unchanged

**Verdict: CONFIRMED (content and the "gained/unchanged" deltas), with two corrections to the framing.**

Verbatim (pinned revision, my parse of `xl/worksheets/sheet3.xml`, sheet name `OVERVIEW`):

- **ROW 132** = `A 'TM600'`, `B 'BUBO'`, `C 'HS_RDSON'`, **`E '11'`**, `F 'mΩ'`, `H 'Y\r\n2 FLOAT'`,
  `L 'vset[vbat,3.5,100e-6,0]\r\nvset[pmid,5,100e-6,0]\r\nvset[bst_sw,5,1e-3,0]\r\nvset[vdrv,5,100e-6,0]'`,
  `N 'delay[1e-3]\r\niset[sw,1,1e-3,0]\r\ndelay[2e-3]\r\nfinish[]'`,
  `O 'VBAT\r\nBST-SW'`, `P 'ISW'`, **`Q 'PMID-SW\r\nfloating source：V(BST_SW)'`**.
- **ROW 133** = `A 'TM601'`, `C 'LS_RDSON'`, **`E '7.5'`**, `F 'mΩ'`,
  `L 'vset[vbat,3.5,100e-6,0]\r\nvset[vdrv,5,100e-6,0]\r\nvset[vbus,5,100e-6,0]\r\nvset[bst,5,100e-6,0]'`,
  `N 'delay[5e-3]\r\niset[pmid_sw,1,1e-3,0]\r\ndelay[2e-3]\r\nfinish[]'`,
  `Q 'SW-PGND\r\nfloating source：I(PMID_SW)'`, `K 'Rds,on=(SW-PGND)/IPMID2SW'`.

**"gained / unchanged" is independently witnessed** by the previous run's own extract
`team/artifacts/acceptance-20260916-dali10/dft-raw/overview-dft.json`, which self-records
`"sha256": "d9d721a3a6606232bb463c8147d4955bea623bf81996e9ff85ccb8e463c7788e"` for the same path (a **third**, older revision) and contains:

- `TM600` … `Code1: 'vset[vbat,3.5,100e-6,0]\nvset[pmid,5,100e-6,0]\nvset[bst_sw,5,1e-3,0]\nvset[vdrv,5,100e-6,0]'`, `ExpectValue 11 mΩ` ⇒ row 132 **unchanged** across three revisions ✅
- `TM601` … `Code1: 'vset[vbat,3.5,100e-6,0]\nvset[vdrv,5,100e-6,0]\nvset[vbus,5,100e-6,0]'` (**three** vset lines, no `bst`) ⇒ the fourth line `vset[bst,5,100e-6,0]` **was added** ✅

Corrections / omitted caveats:

1. **"Sole authority" is a policy assertion, not a reading, and it is contested by the run's own evidence.** `project/DALI/input/DFT.csv:90-97` (TM600) reads verbatim `TM600,RDSON_TEST,HS_RDSON,10,mohm,,,"vset[vbat,4.2,100e-6,0]` / `vset[pmid,15,100e-6,0]` / `vset[bst2sw,5,1e-3,0]` / `vset[vdrv,5,100e-6,0]"` … `"iset[pmid2sw,1,1e-3,0]",PMID-SW,MV&MI`; `:98-104` (TM601) reads `TM601,,LS_RDSON,8,mohm,,,"vset[vbat,4.2,100e-6,0]` / `vset[pmid,9,100e-6,0]` / `vset[vdrv,5,100e-6,0]"` … `"iset[sw2pgnd,1,1e-6,0]",PGND-SW,MV&MI`. The deployed tree itself says (test.cpp:9036-9037): *"TWO-PROVENANCE CORROBORATION … the archived revision pairs 11 / 7.5 mohm with pmid 5 V, while DFT.csv pairs 10 / 8 mohm with pmid 15 / 9 V"*, and (9053-9054) *"BD-01 limits are 11 / 7.5 mohm (OVERVIEW, user-ruled) with DFT.csv 10 / 8 mohm retained verbatim as a registered conflict"*. So there is a **registered, deliberate coexistence of two DFT authorities**; "sole authority" is a ruling to be argued, not a fact C1 can assert from the workbook alone.
2. **Missing caveat that matters for the TM601 remedy:** row 133 has **no `vset[pmid]` and no `vset[bst_sw]`** (unlike row 132), its forced source is named `I(PMID_SW)` while the deployed function forces the loop between **PGND and SW** (`test.cpp:9255`, `9294-9301`), and its measured quantity is `SW-PGND`. C1 quotes the row but does not flag that its token set differs structurally from TM600's.
3. The claimed **mtime 21:46:39** matches the pin and the workbook's embedded `docProps/core.xml` (`dcterms:modified 2026-09-16T13:46:38Z` = 21:46:38 +0800) but **no longer matches the live file** (see §0.1).

### C2 — the deployed code lines (TM600 staircase, TM640 pattern, TM601, PB0_BST_ACM)

**Verdict: CONFIRMED, essentially line-for-line. No quoted value is wrong; two body extents and one interpretive point are imprecise.**

- **TM600 body extent**: `DUT_API int TM600_HS_RDSON(...)` at `test.cpp:9057`; body closes at `test.cpp:9204` (`return 0; }`), so "~L9057-9216" overstates by ~12 lines (9216 is inside TM601's header comment). Harmless.
- **Only one `cbite.SetOn` in TM600 — `test.cpp:9081` verbatim**:
  `cbite.SetOn(K83_BUSH0_PMID, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);`
  ⇒ **K48/K76 absent. CONFIRMED.** (I read the whole function: no second `SetOn`.)
- **The staircase — `test.cpp:9091`…`9115` verbatim** (power-on), with the in-file comments:
  `9091 FPVI0.Set(FV, 0, FPVIe_1V, FPVIe_10UA, FPVIe_RELAY_ON);`
  `9097 SW12_U1REF_BST_ACM.Set(FV, 0, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);`
  `9099 // step 1: PMID 0 V, BST-SW 5 V` → `9100 SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);`
  `9102 PMID_HG2_FXVI.Set(FV, 5, FXVIe_PLUS_10V, …)` · `9104 // step 2: PMID 5 V, BST-SW 5 V`
  `9105 …Set(FV, 10, ACM200_20V, …)` · `9107 PMID_HG2_FXVI.Set(FV, 10, FXVIe_PLUS_20V, …)`
  `9109 // step 3: PMID 10 V, BST-SW 5 V` · `9110 …Set(FV, 15, ACM200_40V, …)` · `9112 PMID_HG2_FXVI.Set(FV, 15, FXVIe_PLUS_30V, …)`
  `9114 // step 4: PMID 15 V, BST-SW 5 V (FET on -> SW follows PMID)` · `9115 …Set(FV, 20, ACM200_40V, …)`
  ⇒ values 0→5→10→15→20 on the ACM channel against PMID 0→5→10→15; ends **PMID 15 V / BST 20 V**. CONFIRMED. Also `9086 // ATE excitation per the plan (DFT/OVERVIEW, BD-08): PMID 15 V, VBAT 4.2 V, VDRV 5 V` — note this **contradicts row 132** (`vbat 3.5` / `pmid 5`) by the run's own comment; C2 does not flag it.
- **`test.cpp:9195` is a ghost release**: `FPVI1.Set(FV, 0, FPVIe_1V, FPVIe_10MA, FPVIe_RELAY_OFF);  // channel 1 (BST-SW loop) releases first` — FPVI1 is never turned on anywhere in TM600, and its BST routes (`StdAfx.h:378 K_FPVIH_TO_BST_B 131,132,134,135`; `:452 K_FPVIL_TO_BST_B 109,110`) are never closed. C2 quotes the line's region but not this defect.
- **TM640 — CONFIRMED verbatim**: `7517 // DFT: vbat=3.5V pmid=5V bst_sw=5V vdrv=5V; … 先固定 PMID=SW，再建立 BST-SW=5V`; `7513 cbite.SetOn(K_FPVIH_TO_PMID_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K65_nQON_PU, -1);`; `7521 SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);  // PMID=SW=0V, BST-SW=5V`; `7524 PMID_HG2_FXVI.Set(FV, 5, …)`; `7526 SW12_U1REF_BST_ACM.Set(FV, 10, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON); // SW=5V, BST-SW=5V`. Body ends at 7590 ("~L7503-7605" overstates by 15 lines).
- **TM601 — CONFIRMED**: body `9217`–`9353` (exact); single `SetOn` at `9255`: `cbite.SetOn(K154_BUSH0_AMUX, K155_FOVI3_PGND, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K85_CAP_PMID, K57_CAP_BST_SW, K126_V1P5_CAP, -1);` ⇒ neither `K48/K76` nor `K46/K49/K109/K110` present ✅. `9269 SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V, ACM200_100MA, ACM200_RELAY_ON);` ✅ with `9260 // ATE excitation per the plan (DFT/OVERVIEW, BD-08): VBAT 4.2 V, PMID 9 V, VDRV 5 V` and `9271 PMID_HG2_FXVI.Set(FV, 9, FXVIe_PLUS_20V, …)`; LSON bit `9278 I2CWriteSameData(DEV_ADDR, 0x5A, 0x01);`.
- **Channel identity — CONFIRMED and now proven**: `Pin_Channel_define.h:20 #define _PIN_CHANNEL_DEFINE_SW12_U1REF_BST_ACM_  "S5_5,S6_5,S11_5,S12_5,S21_5,S22_5,S27_5,S28_5"` (⇒ **S5 = ACM200 pin 5**), matching `SCH-Connect-Map.txt:673 F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F`; and `Pin_Channel_define.h:33 …PB0_BST_ACM_ "S5_18,…"` ⇒ ch18. `StdAfx.h:620 #define K_BST_ACM 48,76 // ACM200[] -> BST: K48_ACM5_AMP_REF + K76_ACM_BST` and `StdAfx.h:638 #define K_SW_ACM 61 // ACM200[] -> SW: K61_ACM8_SW` (note: ch8, not ch5).
- **PB0_BST_ACM — CONFIRMED** (all uses): `5003` (FV 0 init), `5022`/`5026` (`rampv_capv(PB0_BST_ACM, …)` PWM1 threshold toggle), `5041`/`5045` (power-off), `5185`/`5187`/`5189` (`Set`/`MeasureVI(50,5)`)/`5192` (`GetMeasResult(site, MIRET)` for `pwm1_curr`), `5196`/`5199`. No BST-node use.

**The material omission in C2**: the same comment block contains, at **`test.cpp:9024-9033`**, the deployed tree's **direct denial of C3** (see below). C2 quotes that block's BD-01/limitations lines (9052-9054) but skips 9024-9033.

### C3 — `SCH-Connect-Map.txt` lines 672-674

**Verdict: PARTLY-CONFIRMED.** The quoted text is verbatim exact; the *authority* of that reading is not established.

`SCH-Connect-Map.txt:672-674` verbatim:
```
672   BST  [Kelvin]  需闭合: K48,K76
673     F: S5_ACM200_FH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_F
674     S: S5_ACM200_SH5 -> K48(Relay-ON) -> K76(Relay-ON) -> BST_S
```
**What fails**: the deployed tree contradicts it in its own words —
`test.cpp:9027-9028`: *"ACM200 reaches SW only and cannot reach BST, and FXVIe_PLUS reaches PMID/PGND only with its low side returning to AGND_F, so it cannot form a floating pair."*
`test.cpp:9033`: *"(Counter-evidence to date: ACM200 does not reach BST.)"*
This is a **four-way inconsistency already on record** (connect map vs. deployed comment vs. contract vs. gate) and the run's own R8 receipt lists it as a **blocking UNKNOWN** requiring a user ruling on which evidence is authoritative (`review/captain-recovery-r8-independent-review.md` §2 row 2, §5.2). C3 presents the map side as settled and does not disclose the contradiction it is standing on.

### C4 — the "correct shape" for TM600 at PMID=5 V, and the safety consequence

**Verdict: PARTLY-CONFIRMED. The prescription survives; the safety argument fails as stated and was already retracted by the run itself.**

*Prescription (holds).* "BST leads PMID by 5 V; final state BST absolute = 10 V for a PMID=5 V point" matches the deployed precedent in four places: TM640 (7513/7521/7526), TM608_HS_ZCD (7087/7096/7098/7100 `// SW=5V, BST-SW=5V`), TM609_BOOST_HS_NEG (7170/7179/7182/7184), and TM607_BUCK_LS_ZCD (7000/7008/7010). The gate states the same target: `scripts/verify_bst_sw_sequence.py:6` *"HS (BOOST, PMID-SW): powered_pins 含 BST-SW/BST_SW → BST 5V→10V 台阶"* and `:545 print("[contract] BST>=SW and 0<=BST-SW<=5V; operating target BST-SW=5V")`.

*What fails:*

1. **"Copying the deployed 15 V staircase onto a PMID=5 V point" is not a well-defined operation, and the natural reading of it is already the TM640 pattern.** The deployed sequence is an **interleaved BST/PMID ladder**: BST = {0,5,10,15,20} with PMID = {0,5,10,15} interleaved (`9100/9102/9105/9107/9110/9112/9115`). Its **first three rungs** — BST 5 at PMID 0, PMID 5, BST 10 — are *precisely* the "TM640 pattern" C4 proposes as the correct shape. Truncated after the third rung it satisfies `0 ≤ BST−SW ≤ 5 V` at every settled state; only the *tail* (BST 15/20 while PMID stayed at 5) violates, and that requires deliberately discarding the PMID rungs that belong to the same ladder. So the claim that the deployed shape is wrong **for a PMID=5 V point** is not supported by the ladder's geometry: the difference is the number of rungs, not the shape.
2. **The premise "the 15 V staircase reaches BST" is unproven, by the run's own finding.** With K48/K76 never closed in TM600 (`9081`), the commanded 5–20 V was never shown to arrive at BST. The run's own R8 receipt records this exact argument as **WITHDRAWN**: *"「沿用 15 V 台阶在 PMID=5 V 工况下会得 BST−SW=15 V，支持 A1」 → 撤回：该论证建立在一个未成立的假设上：部署态 TM600 从未闭合 K48/K76 ⇒ 20 V 台阶根本没被证明到达过 BST 节点"* (`review/captain-recovery-r8-independent-review.md` §3). C4 re-asserts the withdrawn argument.
3. **The gate cited does not enforce the rule.** I read the gate: its BST−SW checks are **exact-string counts** (e.g. `:165-166`, `:177-178`, `:200-201`, `:229`: `require_exact_count(power_on, "SW12_U1REF_BST_ACM.Set(FV, 5, ACM200_10V", 1, …)`) plus a contract closure-set comparison (`:429`). `"[contract] BST>=SW and 0<=BST-SW<=5V"` at `:545` is a **printed banner**, not a numeric evaluation of the ACM setpoints. Citing it as the rule's enforcement overstates it — and the current run's own sandbox evidence says the same (`sandbox-fix-verification.md` §4.2: *"该门只校验闭集，不校验阶梯 … 门禁绿 ≠ 操作点正确"*).

*Omitted, material:* for TM600 the same workbook row's Check column demands a **floating source** (`Q 'PMID-SW\r\nfloating source：V(BST_SW)'`), yet deployed TM600 uses a **ground-referenced** ACM source and never drives the declared floating channel (the only FPVI1 action is the ghost `RELAY_OFF` at `9195`). Neither C2 nor C4 mentions that the row-132 check is unmet in kind, not just in value.

### C5 — `voltage-inference.md` lines ~18/142/151-160

**Verdict: REFUTED as stated.** Both halves of the claim fail on the text.

Verbatim from `knowledge/hardware/voltage-inference.md`:
- `18 PMID_FOVI.Set(FV, 15) → PMID = 15V` — a **generic type-A example**, not TM600.
- `121 示例: VBAT=4.2, VDRV=5, SW=0, PMID=15, BST=20`; `128 BST=20 (A) → BST-SW=20-15=5V ✓`
- `142 DFT: vset[vbat,4.2], vset[pmid,15], vset[bst2sw,5], vset[vdrv,5]`; `143 iset[pmid2sw,1A] (dynamic)`; `145 FPVI: K31_BUS_PMID + K17_BUSH_SW 闭合 → 类型D`; `146 BST-SW: 无BUS → 类型A独立: BTST_ACM=20V, SW_ACM=0V`
- `151-161` table: `153 上电初态 | 0V|0V|0V|0V`, `154 台阶1 | 0V|0V|5V|5V`, **`155 台阶3 | 10V|0V|15V|15V`**, **`156 台阶4 | 15V|0V|20V|20V`**, `157 FET导通 | 15V|15V|20V|5V ✓`, `159 下电台阶1 | 10V|10V (C)|15V|5V`, `160 下电台阶3 | 0V|0V (C)|5V|5V`

Why it fails:
1. **It is not "the same deployed staircase".** The deployed comments assert **BST−SW = 5 V at every rung** (`9099/9104/9109/9114`), i.e. SW tracks PMID; the document's table asserts **SW = 0 V** and therefore **BST−SW = 15 V and 20 V** at 台阶3/台阶4. The two descriptions agree on raw ACM setpoints and the final PMID 15/BST 20 pair, but they **disagree on the BST−SW column by a factor of 3–4** — the very column the rule is about. C5 collapses that disagreement.
2. **It is a competing value set for the same item, not merely "an alternative operating point".** The document's DFT line (142) is a value-for-value transcription of the **competing DFT authority** `project/DALI/input/DFT.csv:90-92` (`vbat 4.2`, `pmid 15`, `bst2sw 5`, `ist[pmid2sw]`), and `voltage-inference.md:145` even names relays (`K31_BUS_PMID`, `K17_BUSH_SW`) that do not appear anywhere in the deployed TM600 function (which uses `K83_BUSH0_PMID`, `K60/K61`). So the document is a **stale/parallel DFT provenance** that directly contradicts row 132 (`pmid 5`, `bst_sw 5`, `vbat 3.5`). Calling it "not a competing value" is the opposite of what the text shows. The run's own R8 receipt reached the same conclusion and **downgraded this exact claim to "不充分"** (§3, second row): *"`voltage-inference.md:142-143` 是逐字转录 `DFT.csv` … ⇒ 改标记文件并不能退役 15 V"*.

### C6 — TM601: source commanded, BST node unconnected, fix belongs in the setup contract

**Verdict: PARTLY-CONFIRMED.** The missing closure is real and the contract-owner framing is directionally right; three parts of the statement are incomplete or wrong.

Confirmed: `test.cpp:9255` closes no BST-route relay while `9269` commands `SW12_U1REF_BST_ACM` (proven = ACM200 S5 pin 5). Every documented route to BST requires at least one relay group that is absent — `SCH-Connect-Map.txt:39-41 CH0 High -> BST 需闭合: K46,K48,K76`; `:42-44 CH0 Low -> BST 需闭合: K109,K110,K138,K139,K145,K146`; `:265-270 CH1 High/Low -> BST K131,K132,K134,K135 / K109,K110`; `:461-462`, `:536-539` (same K46/K48/K76 or K109/K110 chains); `:672-674` (K48,K76). None of those numbers appears in the TM601 `SetOn`, and the only BST-adjacent closure is `K57_CAP_BST_SW`, which is a **capacitor branch**, not a source (`:904 SW 稳压 Cap_SW_BST_S1 C=220nF 需闭合: K57`). So no DC source reaches BST.

What fails / is missing:

1. **"Leaving the BST node unconnected" is incomplete and understates the hazard.** `SCH-Connect-Map.txt:774-776` reads `SW1 [Kelvin] 需闭合: 无(默认导通)` / `F: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F` and `:777-779 SW2 … 需闭合: K49`. With `K48` **not** actuated and `K49` never closed anywhere in the file (`K49_` has **0 hits** in test.cpp), the ch5 source is **not floating — it is steered to the SW1 pin by default**. So the deployed TM600/TM601 are commanding a 5–20 V / 5 V source onto **SW1**, a different DUT switch node, while claiming to drive BST. C6 says "BST is not actually driven" (true) but misses that the same source is driving something unintended; and no claim in C1–C6 mentions SW1, K49, or the K45 SW1-cap relay.
2. **The same defect exists in TM600, and there it is the headline.** C6 restricts the consequence to TM601; but TM600's `9081` is missing exactly the closure that the run's own contract and sandbox already require for TM600 (below), and TM600 is the item whose entire power sequence is built around BST.
3. **"The fix belongs in the setup contract" needs a stronger qualification.** The contract and the code are already out of sync in *both* directions, on the record:
   - `sandbox/fix-test-result.json` (this run): unedited copy → `[t30] TM600_HS_RDSON: 契约声明必需 [48, 60, 61, 76, 83] … 缺失=[48, 76]` / `*** FAIL ***` exit 1; after adding only `K48_ACM5_AMP_REF + K76_ACM_BST` to TM600's `SetOn` → `缺失=[]` / `BST-SW SEQUENCE PASSED` exit 0 (contract `rev=36`).
   - `t50-payload-k76-evidence.md`: the **authorised** TM600 `SetOn` is `K83, K60, K61, K48, K76, K13, K85, K57, K126` — i.e. the deployed tree is **behind the authorised payload**, not merely un-improved; and the same file records that the contract still demands `K110` for TM600 (*"rev 25 … still demands K110 for TM600"*), which is the contradicting route.
   - `t38-acm-pin5-exposure.md`: *"`K48/K76` are the relays that carry anything to BST in this fixture"* — I verified its cited locators (`:673/:775/:778`) myself.
   So "the contract owner must fix it" is right for **TM601** (whose contract registers **no BST leg at all** — see `t50` §: *"TM601.pinRouteTable has NO BST node"*) but for **TM600** the contract already demands the closure and the *code* is what lags. C6 conflates the two.

---

## 2. Counter-evidence the claims missed

| # | Counter-evidence (verbatim locator) | Bites |
|---|---|---|
| CE-1 | **Four deployed siblings at PMID = 5 V with a BST 5→10 V staircase and K48+K76 closed**: TM608 `test.cpp:7087 cbite.SetOn(K_FPVIH_TO_PMID_A, K60_BUSL0_VCP, K61_ACM8_SW, K13_VBAT_Cap, K57_CAP_BST_SW, K48_ACM5_AMP_REF, K76_ACM_BST, K85_CAP_PMID, K65_nQON_PU, -1);` + `7091 // Golden HS_ZCD: FPVI0 FV=0 先固定 PMID=SW，再用独立源建立 BST-SW=5V` / `7092 // 全程保证 BST>=SW 且 BST-SW<=5V`; TM609 `7170/7174-7175/7179/7184`; TM640 `7513/7517/7521/7526`; TM607 (an **LS** item) `7000/7003-7004/7008`. | The "15 V staircase" is the **outlier** for these two items, not the house style; and an LS item (TM607) *does* drive BST via K48/K76 — i.e. an LS test needing a BST rail is normal here. |
| CE-2 | **The deployed tree denies ACM200→BST**: `test.cpp:9027 … ACM200 reaches SW only and cannot reach BST` and `9033 (Counter-evidence to date: ACM200 does not reach BST.)` | C3/C4/C6 all rest on the opposite reading. |
| CE-3 | **A second, competing DFT authority**: `project/DALI/input/DFT.csv:90-92` (TM600: `pmid 15`, `bst2sw 5`, `vbat 4.2`, `10 mohm`) and `:98-100` (TM601: `pmid 9`, `8 mohm`); confirmed as an authority by `test.cpp:9036-9037,9053-9054`. | C1 ("sole authority") and C5 ("not a competing value"). |
| CE-4 | **The doc contradicts the deployed comments on the BST−SW column**: `voltage-inference.md:155 BST-SW 15V`, `:156 BST-SW 20V`, `:154 BST-SW 5V` vs `test.cpp:9104/9109/9114 // … BST-SW 5 V`. | C5 ("same staircase"). |
| CE-5 | **`relays.md` is self-conflicting about the K46–K59 family**, and therefore about what "released K48" means: `:99 **P2P 继电器** (MOS) | K46~K59, K68 | **断开** (MOS 关断) | **闭合** (MOS 导通)` vs `:158 > 当前 DALI 无 P2P 继电器, 该规则为占位`. Meanwhile the connect map shows K48 as a **changeover** whose un-actuated contact conducts to SW1 (`:774-776`). `relays.md:48` also states the general opto rule *"必须 cbite.SetOn 才会导通"*. | The closure reasoning in C6 is *not* resolvable from the relay docs; this run already flags it (r7 recorder Q3). |
| CE-6 | **K57 tension, unresolved in the reviewed items**: the BST-SW gate *requires* it — `scripts/verify_bst_sw_sequence.py:536-537 …missing BST-SW differential capacitor relay … (… SCH-Connect-Map L904 Cap_SW_BST_S1 需闭合 K57)` — while `relays.md:125/131` requires removing a pin's cap when that pin's current is measured, and the prior run's ledger records *"K57 结论明确=**不应闭合**"* (`t26` output, `.agent-teams/ate-dali-acceptance/team.json`). The deployed TM601 argues the opposite at `9234-9254` and `9251-9254` warns the settling effect is unanalysed. | No claim in C1–C6 mentions K57. |
| CE-7 | **The gate cannot see the claimed violation.** `verify_bst_sw_sequence.py:165-229` = exact string counts; `:429` = closure set; `:545` = banner. | C4's appeal to the gate. |
| CE-8 | **Open contract contradiction for TM600/TM601**: `fix-test-result.json` (contract rev 36) demands `[48,60,61,76,83]` for TM600 — mixing the ch5 route (`48,76`, `SCH:673`) with the ch18/FPVIe route (`109,110`, `SCH:42/:268`) — while `t38`/`t42`/`t43`/`t50` ruled the ch5 route correct and the t50 narrowing was *"BLOCKED at the bst-sw gate"*; and TM601 registers no BST leg at all. | C6's "fix belongs in the contract" — the contract is itself the contested artifact. |

---

## 3. The arithmetic (question 3)

| Quantity | Value | Basis |
|---|---|---|
| V(SW)−V(PGND) at 1 A, 7.5 mΩ | **7.5 mV = 0.0075 V** | 1 A × 7.5e-3 Ω (row 133 `E 7.5`, `F mΩ`); the workbook's own formula `K133 Rds,on=(SW-PGND)/IPMID2SW` |
| V(SW)−V(PGND) at 1 A, 11 mΩ (HS row) | 11 mV | row 132 `E 11 mΩ` |
| BST−SW with a ground-referenced 5 V source on BST, **assuming SW ≈ 0 V** | **4.9925 V** | 5 − 0.0075 |
| Same, if SW is pinned to PMID=5 V (TM600 HS case) | **0 V** | `test.cpp:7518/9091` FPVI0 `FV,0` ties PMID=SW; row-132 check is `BST-SW`, so a literal BST = 5 V yields BST−SW = 0 |
| BST−SW if the ACM rungs continue to 15/20 while SW stays at 5 V | **10 V then 15 V** | 15 − 5, 20 − 5 |

**Formula check for row 133:** `Rds,on = (SW−PGND)/I(PMID_SW)`; 7.5 mΩ × 1 A = 7.5 mV, so the workbook demands a **7.5 mV** measurement — consistent with `FPVIe_MV_X10` and with the deployed `9167` idiom, and consistent with the deployed note `9015-9016` (*"the expected drop is ~11 mV / 7.5 mV at 1 A, three orders below the 0.5 V clamp"*).

**Does the debug column `SW-PGND=0.3` contradict the 7.5 mΩ limit? Yes — under either unit reading, and it cannot be reconciled as a same-condition measurement:**

- `OVERVIEW!AH133` (pinned rev, and identical in the drifted rev as row 22) = `'I=1A\r\nSW-PGND=0.3'` — **no unit** (shared string index 251 in both revisions).
- If `0.3` is **volts**: 0.3 V / 1 A = **300 mΩ = 40.0 × the 7.5 mΩ acceptance limit** (and 40× the 7.5 mV expectation).
- If `0.3` is **millivolts**: 0.3 mV / 1 A = **0.3 mΩ = 0.04 × the limit** — i.e. 25× *below* the limit, equally inconsistent with a limit that is supposed to be near the real value.
- The sibling cell `AH132 = 'I=0.2A\r\npmid-sw=46mV'` shows the convention of the column: **wrong current (0.2 A vs the row's `iset[sw,1,…]`) and a value that yields 46 mV / 0.2 A = 230 mΩ = 20.9 × the 11 mΩ limit**. Two rows, two ~21–40× discrepancies ⇒ the column is not an RDSON measurement at the row's own conditions and **cannot be used to calibrate or to re-derive either limit**. (The run's R8 receipt independently reached the same conclusion for AH132/AH133, `review/captain-recovery-r8-independent-review.md` §4.)

---

## 4. Safety judgement on C4's scenario (question 4)

**Scenario as written:** "copy the deployed 15 V staircase onto a PMID=5 V point".

**FACT (verbatim readings):**
1. In both reviewed items the BST node has **no DC source**: TM600 `9081` and TM601 `9255` close none of the BST-route relays (`SCH:39-44, 265-270, 461-462, 536-539, 672-674`); the only BST-adjacent closure is the **capacitor** relay `K57_CAP_BST_SW` (`SCH:904`, `Cap_SW_BST_S1 C=220nF`), which both items close.
2. The ch5 source's **default** endpoint is **SW1**, not BST: `SCH:774-776 SW1 [Kelvin] 需闭合: 无(默认导通) / F: S5_ACM200_FH5 -> K48(Relay-NC) -> K49(Relay-NC) -> SW1_F`; `:777-779` selects SW2 with `K49`, and `K49_` never appears in `test.cpp` (**0 hits**).
3. The deployed tree asserts the fixture cannot route ACM200 to BST at all (`test.cpp:9027`, `9033`).
4. A Schottky **exists** across the bootstrap node: `project/DALI/Component-Statistic.txt:476-477 D_Schottky)) (3): D_BST_SW_S1, D_SW1_BST1, D_SW2_BST2` (token `D_BST_SW_S1` occurs **0** times in `test.cpp`).
5. Documented limit class: `docs/BST-SW通用知识介绍.txt:21 绝对最大值：芯片数据手册会规定BST-SW间的最大允许电压，例如不超过5.5V`; `:23` UV threshold example 2.3 V; `:30` device examples 2.5 V (ROHM) / ~5 V (TI); `:46` the floating-pair method needs *no* absolute requirement and normally forces SW to PGND = 0 V.
6. Gate behaviour: see §1 C4 point 3 (counts + closure set; banner only).

**INFERENCE (mine, flagged as such):**
- "Copying the staircase" is only well-defined in two ways. **(i) Literal copy of the code block:** impossible as a PMID=5 V point — the block itself commands PMID 10 V and 15 V (`9107/9112`), so the copy *is* the PMID=15 V operating point, and every settled state keeps BST−SW = 5 V. **(ii) Non-literal copy (keep PMID/SW at 5 V, keep feeding the ACM rungs 5/10/15/20):** BST−SW becomes 0 / 5 / 10 / 15 V, and the last two exceed the 5 V-class limit by ~2–3×.
- But **in the deployed state** (K48/K76 open) the commanded voltage does not reach BST at all: by the map it is steered to **SW1**; by the deployed comment (`9027`) ACM200 cannot reach BST even when closed. Therefore the *"the DUT bootstrap node gets over-volted by copying the staircase"* consequence is **not established by any evidence I read**. The real, documented effect of the copy is **an unintended 5–20 V drive on the SW1 pin** (and, with `K48/K76` closed as C6's fix would do, a **steering change**: SW1 loses the drive and BST gains it — meaning the fix and the hazard are the same relay pair).
- **If** the rungs were also routed to BST with K48+K76 closed while PMID stayed at 5 V, then ~15 V would stand across the `Cap_SW_BST_S1` 220 nF capacitor and the DUT's HS-driver rail (`BST`) — that is the only mechanism by which C4's stated consequence becomes physically real, and it is a *conditional* statement, not the deployed state.
- The 220 nF capacitor itself is not the hazard at 15 V; the hazard is the DUT's BST pin/driver and the possibility that `D_BST_SW_S1` forward-conducts into SW depending on its orientation.

**UNKNOWN (cannot be settled from what I read; do not treat as fact):**
- **K48/K76 released-state semantics.** `relays.md:99` says the K46–K59 family is "MOS, default open"; `relays.md:158` says the project has no P2P relays; the connect map renders K48 as a changeover with a *conducting* default to SW1. Which is true decides whether "released" = open or = reroute. (This run's own recorder flags the identical tension: `_record_r7.py` → Q3.)
- **`D_BST_SW_S1` orientation** (which net is the anode) and therefore whether a Schottky clamps BST−SW, and in which direction. I verified existence only — no netlist orientation, no datasheet.
- **The DUT's actual BST−SW absolute maximum** (the doc's 5.5 V is an "例如/for example", not this chip's datasheet, which is not in the workspace).
- **SW/PGND absolute DC reference in TM601.** `test.cpp:9214` states `K93_AGND2PGND must stay OPEN or PGND is tied to AGND_F (SD-3)`, so PGND is *not* tied to AGND, and the TM601 loop (PGND high / SW low, floating source) does not by itself define SW = 0 V. Hence "BST−SW ≈ 4.99 V from a ground-referenced 5 V BST source" holds **only under the assumption SW ≈ 0 V** — the same assumption the doc (`:46`, `:49`) and the run's R8 arithmetic make, but it is an assumption, not a reading.
- **SW1's own abs-max / whether a 5–20 V drive on SW1 is harmless** — no evidence read.
- Whether the *gate* or the *contract* is authoritative for the TM600 closure set (CE-8).

---

## 5. Verdict table (question 5)

| Claim | Verdict | What fails / must be qualified |
|---|---|---|
| **C1** workbook = modified DFT, row 133 gained `vset[bst,5,…]`, row 132 unchanged, "sole authority" | **CONFIRMED (deltas) / "sole authority" PARTLY** | Deltas proven against a third, older revision (`dft-raw/overview-dft.json`, xlsx `d9d721a3…`): TM601 Code1 3→4 vset lines, TM600 identical, `E 11`. But (a) "sole authority" is contested by `DFT.csv:90-104` + the registered two-provenance conflict (`test.cpp:9036-9054`); (b) the live file **drifted mid-review** (§0.1) — hash/size/row numbers no longer match C1 or the pin; (c) row 133 has no `vset[pmid]`/`vset[bst_sw]` and names `I(PMID_SW)` while the code forces PGND↔SW. |
| **C2** deployed-code readings | **CONFIRMED** | No quoted value wrong. Imprecise: TM600 body ends 9204 (not 9216), TM640 ends 7590 (not 7605). Materially **incomplete**: omits `test.cpp:9024-9033` (ACM200→BST denial), the ghost `FPVI1` release at `9195`, and the SW1 default-throw (CE-1/CE-2, §2). |
| **C3** connect-map K48/K76 → BST | **PARTLY-CONFIRMED** | Text verbatim exact (`:672-674`). Authority unproven: the deployed tree asserts the opposite (`:9027`, `:9033`); the run's own R8 lists this as a blocking UNKNOWN. |
| **C4** "correct shape" + safety consequence | **PARTLY-CONFIRMED (prescription yes; safety REFUTED as stated)** | The shape matches four deployed siblings and the gate's stated target; but the 15 V staircase is an interleaved BST/PMID ladder whose own first three rungs *are* the prescribed shape, its arrival at BST is unproven (K48/K76 never closed), the cited gate does not evaluate BST−SW numerically, and the run's R8 receipt already **withdrew this identical argument**. |
| **C5** doc = same staircase, "alternative operating point" | **REFUTED** | The doc's table asserts BST−SW = 15 V/20 V at 台阶3/4 (`:155-156`) where the code comments assert 5 V (`:9109/:9114`) — not the same staircase; and its DFT line (`:142-143`) transcribes the competing `DFT.csv` authority, so it *is* a competing value set for the same item (R8 downgraded this claim to 不充分). |
| **C6** TM601 source commanded, BST undriven, fix in contract | **PARTLY-CONFIRMED** | Missing closure is real and proven; but "unconnected" is wrong — the source is default-steered to **SW1** (`SCH:774-779`, K49 absent); the identical defect in **TM600** (`9081`) is omitted; and "fix in the contract" is only half true for TM600 (contract rev 36 already demands `[48,76]`; the *code* lags, per `sandbox/fix-test-result.json`), while the contract is itself contradictory about which route TM600 needs. |

### Strongest unresolved objection

**The ACM200→BST reachability question is unresolved, and every claim C3/C4/C6 depends on it.** `SCH-Connect-Map.txt:672-674` (K48+K76) and `test.cpp:9027/9033` ("ACM200 reaches SW only and cannot reach BST") cannot both be true, and the same conflict propagates into the contract (rev 36 demands `[48,60,61,76,83]` — a *union* of two different routes — while the gate FAILs the deployed tree by exactly `[48,76]`). Until that is settled, "the deployed staircase never reached BST" and "BST was driven to 20 V" are both unfalsified, and C4's safety scenario has no determinate physical subject. Secondary but independent: **which DFT governs** (pinned OVERVIEW vs. `DFT.csv`) is a four-field coupling (PMID 5/15, VBAT 3.5/4.2, `iset[sw]` vs `iset[pmid2sw]`/`sw2pgnd`, limits 11/7.5 vs 10/8 mΩ) that cannot be settled by taking PMID alone.

### What would settle it (single measurement / single file)

1. **One continuity measurement** on the fixture at the ACM200 S5 pin-5 output: with `K48` de-energised vs. energised (and `K49` open), measure to **SW1** and to **BST**. This single pair of readings decides both the C3/C6 route question and the CE-1 "SW1 is being driven" hazard. Equivalent bench check: `K48`+`K76` closed → is AC continuity present from `S5_ACM200_FH5` to `BST`?
2. **One file**: the fixture netlist pin table — `project/DALI/Dali-SCH.csv` (plus `project/DALI/Component-Statistic.txt`) — read at pin level for `K48`, `K49`, `K76`, `K110`, `K57`, `D_BST_SW_S1`. The prior run already used exactly this method (`t47-ch5-endpoint-sharing.md`, `t48-node-convergence-and-precedent.md`: `K76.pin4 = K110.pin4 = NetK76_ACM_BST_S1_4`, `K76.pin5 = K110.pin5 = NetK57_CAP_BST_SW_S1S2_3`), and the Schottky's two nets would fix its orientation if the schematic symbol's A/K pin naming is recoverable.
3. For the operating point, one bench run of TM600's RDSON at both candidate points (PMID 5 V / BST 10 V and PMID 15 V / BST 20 V) with MVRET/MIRET logged, compared against 11 mΩ and 10 mΩ, would retire the C1/C5 "which DFT" question without further document argument.

---

## 6. What I could NOT check (explicit limits)

- **No hardware, no bench, no relay actuation, no continuity** — nothing electrical is measured anywhere in this report.
- **`ABS` sheet rows M29/M30/M44/M50** (cited by the R8 receipt as `BST-SW` upper-limit evidence) — I did not read them; my 5.5 V-class limit comes from `docs/BST-SW通用知识介绍.txt:21` only.
- **`D_BST_SW_S1` orientation** and any clamp behaviour — existence verified, orientation not.
- **The DUT datasheet** for BST−SW abs-max, SW1 abs-max, and `Rds,on` vs PMID — not present in this workspace.
- **`vset[...]` tool semantics** (there is no DFT-tool manual here): whether `vset[bst,5,…]` for an LS item means an *absolute* pin voltage or a differential/other semantic cannot be settled from a specification; my "≈4.99 V" equivalence is arithmetic under the SW ≈ 0 V assumption, not a semantics claim.
- **Cause of the workbook drift in §0.1** — I can show the byte-level change (size/hash/mtime/row shift) but not attribute it.
- I did **not** re-verify every one of the ~136 artifacts in the prior run; I read the ones that bear on C1–C6 (`dft-raw/overview-dft.json`, `sandbox/*`, `sandbox-fix-verification.md`, `t38`, `t50`, `review/captain-recovery-r8-independent-review.md`, `pin/snapshot-manifest.json`).
- The claims' *policy* half ("the workbook is the sole authority", "the fix belongs to the contract owner") is outside what a read-only reviewer can confirm; I report only where artifacts contradict the framing.

---

### One-line summary

C2/C1-deltas hold up verbatim; C3 is a correct quote of a contested source; C4's prescription is right but its safety argument is the one the run already retracted and is mis-framed (the deployed ladder's first three rungs *are* the "TM640 pattern"); C5 is refuted by the document's own BST−SW column and by `DFT.csv`; C6 is right that BST is undriven and wrong that the source is merely "unconnected" — it is default-steered onto **SW1** — and the same defect is present in **TM600**; and the workbook the whole review is anchored to **changed on disk mid-review**.
