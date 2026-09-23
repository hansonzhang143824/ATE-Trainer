# TM601_LS_RDSON — FR-001 exception: final ruling, locators, and the meta-root-cause evidence

Author: ate-implementer (content) · Reviewer: rule-reviewer (t22) · Executor: Captain (write-capable).
Payload: `implementation-payload-TM600-TM601.cpp` = **32969 B /
`7399598332fac6c342ec44f2e0217e5f43cebc499e17974e4b8c431aded1885b`**.
Wiring citations: `project/DALI/SCH-Connect-Map.txt`. Rule citations: `scripts/verify_relay_trace.py`.
Meta citations: `project/DALI/meta/dali_tm_meta.json`. Frozen ruling: BD-08 + test-plan v20.

## 1. This function's real powered rails

| Terminal | Route | needsClosed | Locator |
| --- | --- | --- | --- |
| Low side | `CH0 Low -> SW [Kelvin]` | `K60,K61` | `SCH-Connect-Map.txt:174` |
| High side | `CH0 High -> PGND [Kelvin]` | `K154,K155` | `:156` |

`K154` alone is `CH0 High -> AMUX` (`:33`); `K154+K155` is PGND (`:156`). **VBUS is never on that path** —
it is reached only via `CH0 Low -> VBUS needsClosed: K3` (`:213`) or CH1 `K138,K139,K145,K146,K3` (`:421`),
and this function closes **no `K3`**.

## 2. Root cause, now provable from the meta's own text — the gate input contradicts BD-08

The meta entry for `TM601_LS_RDSON` reads verbatim:

```
hardwareInit: vset vbat 3.5 / vset vdrv 5.0 / vset vbus 5.0 / iset pmid_sw 1.0 (1e-3) / en_tm / field / field
capAuthority: powered_pins ["ISW","SW","VBAT","VBUS","VDRV"]
              mi_pins []   ramp_pins []   testpad_pins []
```

**The frozen ATE stimulus for TM601 is VBAT 4.2 / PMID 9 / VDRV 5, with VBUS 5 V explicitly a
`simulationDomainReference` and *not* an ATE stimulus** (BD-08 + test-plan v20). The meta instead carries
`vbat 3.5` and `vbus 5.0` — the OVERVIEW/`.sv` layer. The generator is explicit about where these come
from: `gen_testitems_meta.py:148-149` derives `capAuthority` from the **OVERVIEW row** (`powered_pins` =
vset + Power column + Dynamic bare pins).

So the gate's premise "VBUS is statically powered" is an artefact of the **OVERVIEW-derived meta**, and it
is in direct conflict with the frozen ATE ruling. `K5_VBUS_Cap` is therefore a **model false positive**,
not a real supply omission — exactly as the Captain ruled. It is **not closed**.

## 3. Per-cap ruling

| Cap | Basis | Ruling |
| --- | --- | --- |
| **K5_VBUS_Cap** (`:915`, `Cap2_VBUS_S1 4.7uF`) | VBUS is not a TM601 ATE stimulus; arrival needs `K3` (`:213`/`:421`); meta's `vbus 5.0` is simulation-domain | **NOT closed** |
| **K44_Cap_SW2_BST2** (`:906`) | SW2 ← `K46,K49` (`:183`) — a different node; SW2 not in `powered_pins` | **NOT closed** |
| **K45_Cap_SW1_BST1** (`:905`) | SW1 ← `K46` (`:177`) — a different node; SW1 not in `powered_pins` | **NOT closed** |
| **K57_CAP_BST_SW** (`:904`, `Cap_SW_BST_S1 220nF`) | SW ← `K60,K61` (`:174`); SW **is** in `powered_pins` | **closed** — see §4 |

The K44/K45 flag exists only because the family test is by prefix: `cap_pin()` (`:100-115`) turns
`K45_Cap_SW1_BST1` into `SW1_BST1`, and `fam_intersect()` (`:56-58`) matches it to powered pin `SW`
because `"SW1_BST1".startswith("SW")`. `gen_testitems_meta.py:394` applies the same family-intersection
idea to compute its audit column, which is why the meta itself reports SW-family caps as "needed".

## 4. K57 — the rule basis the Captain asked for, with the locator

Verbatim, `verify_relay_trace.py:325-326`:

```python
if fam_intersect(mi, ptok) or fam_intersect(ramp, ptok):
    continue  # 该 PIN 被测电流 / 是 ramp 扫描源 (按 PIN 豁免, 非按函数)
```

with the header at `:10` — `powered_pins 供电轨 / mi_pins 测电流豁免 / ramp_pins ramp源豁免`. The
exemption is **PIN-keyed on `mi_pins`/`ramp_pins`**, and for this item the meta declares
`mi_pins = []` and `ramp_pins = []` **verbatim**. **Therefore the exemption does not fire for SW as the
inputs currently stand, so K57 is required by the rule and is closed.**

But the same reading exposes a second meta gap: the item **does** measure current, through the 1 A force
loop whose return traverses SW (`iset pmid_sw 1.0` in the meta's own `hardwareInit`), and the generated
`params` list is **empty** (`gen_testitems_meta.py:191-197` maps a Check column `I(pin)` to an MI param;
this row produced none). So `mi_pins` is empty because the derivation missed the pin, not because the pin
is not measured.

**Consequence, stated honestly:** under option (A) — correcting the meta's authority sets to the frozen
ATE stimulus — this function's `mi_pins` should carry the measurement pin, at which point the exemption
**fires and K57 should not be closed either**, leaving this item with no cap closure at all. Under the
inputs as they stand today, K57 stays closed. **Either way the payload is defensible; I am not defending
the closure against t22.** Removing K57 is a one-line change.

## 5. Position versus the two options

- **(A) fix the model / inputs** — the right fix, and §2 gives it a precise target: make TM600/TM601
  `hardwareInit` / `powered_pins` follow the frozen ATE stimulus (VBAT 4.2 / PMID 9 / VDRV 5, excluding
  VBUS and every simulation-domain rail), populate `mi_pins` from the real measurement pins, and treat
  SW/SW1/SW2 as distinct nodes. Both `gen_testitems_meta.py` (general script, other TMs other runs) and
  the generated meta are **outside my in-scope paths**, so I recommend the Captain's own preference: a
  **run-scope override/exception**, not an edit to the shared generator logic or to another run's meta.
- **(B) named exception** — what the payload and this document implement now: K44/K45/K5 omitted with
  locators, K57 closed with the rule text quoted, and the omissions listed in the manifest `limitations`.

## 6. Measured gate state on this payload

Workspace sandbox (project's own gate): **`RELAY TRACE PASSED`** — the fabricated-name **errors** are
gone, which is what exit status keys on. Five warnings remain: the two pre-existing `TM643` ones plus
three for `TM601_LS_RDSON` (SW family matched twice by prefix, plus VBUS). This is **more** warnings than
the previous revision precisely because the silencing closures were removed; "zero warnings" is
unreachable until the meta inputs in §2 are corrected. Sandbox copy:
466495 B / `32b4d390c842b2c13f7a96e4229412444b7d8d8e173e01a2c8a412f464adbbcf`.
