# test-plan.json — copy index and anchor rule (plan side)

**Purpose.** The captain ruled that the retained `test-plan*.json` byte copies stay on disk (deleting them
re-created the "unreproducible hash" failure this run already paid for), and asked for the copies to carry
distinguishable labels. This index supplies those labels **without creating a new plan version**; the
authoritative labels for any *value* remain the live artifact's own `revision` field and `revisionHistory`.

**Canonical rule (binding).**

* **canonical = the live file at `team/artifacts/acceptance-20260916-dali10/test-plan.json`** — the generator's
  current output. Any re-run reproduces it, so it is the only valid anchor.
* **Every `test-plan.<vN>.json` sibling is a HISTORICAL copy** and must never be used as an anchor, quoted as
  "current", or fed to a downstream pin.
* Citation discipline: name the **exact path**, recompute size + sha256 with python (plaintext, over bytes) at
  citation time, and print `mtime` **and** the `revision` string together. Never cite a hash carried across
  messages, and never use a glob.

## Live artifact

| path | size | sha256 | mtime | revision |
|---|---|---|---|---|
| `test-plan.json` | 176875 | `f0f825dd302d4105676b113f2335bc1f6fe54c8bcd46a32d621c1026c111dc04` | 2026-09-16 19:24:17 | `v21 (t27 - authorised, freeze lifted inside this scope only)` |

## Retained copies (history; labels as requested)

| copy | role label | size | sha256 | mtime | revision in file |
|---|---|---|---|---|---|
| `test-plan.v1.json` | v1 — t4 terminal delivery | 98641 | `19e6f2c389db69a7c944a41883dc9af7b2b1083bfc495c2b4d0ed901b8e13cfe` | 2026-09-16 14:11:43 | (no revision field) |
| `test-plan.v2.json` | v2 — captain final batch | 113773 | `7f1bdf976c721596b00203c38eef29d559701a7bbdaa06a2d045855265a86463` | 2026-09-16 14:15:48 | (no revision field) |
| `test-plan.v3.json` | v3 — t10 closures | 121694 | `2e93a46c54c79b9028940840f6cf162d15304f89df3c3e88dd5fdea5f5061eda` | 2026-09-16 14:20:55 | v3 (t10) |
| `test-plan.v4.json` | v4 — user final batch + captain BD batch | 128624 | `738998ca98414f326fb0fdde895f4bf8aa6bd921672480cbd215384f6087a72b` | 2026-09-16 14:25:51 | v4 |
| `test-plan.v5.json` | v5 — relay-wiring safety revision | 131707 | `18cf4d7ff9844c4af7a3bf48d9223815d9600ac0ba5b81f2451b9186c20833ab` | 2026-09-16 14:30:12 | v5 |
| `test-plan.v6.json` | v6 — BD-08 artifact revision | 134802 | `d84035516c04795c511cba598a86e11602728bc088512bee57266fc73e68a478` | 2026-09-16 14:33:04 | v6 |
| `test-plan.v7.json` | v7 — status alignment | 136263 | `e1dd24defaed603b80126ee83be0dad7dc2d455a250ef19a74c1e90623677dc6` | 2026-09-16 14:37:12 | v7 |
| `test-plan.v8.json` | v8 — closure wording + provenance | 137290 | `4294a043e674c68cdb42ca7e87d6d5a02709cac3a3bfd4c7ec002f4f64c2e304` | 2026-09-16 14:43:04 | v8 |
| `test-plan.v9.json` | v9 — evidence-accuracy corrections | 142445 | `19ff5e842d45168aae68b24b3eb2a0d41deaff72d9f28e4080577ab7a2a14842` | 2026-09-16 14:47:19 | v9 |
| `test-plan.v10.json` | v10 — stimulus-layer separation | 144250 | `c47098a37dc11ffd54d034ecb990721674b3b764be32f5c60556ba8069af0e2e` | 2026-09-16 14:51:03 | v10 |
| `test-plan.v12.json` | v12 — t11 gap closure, **captain-applied** | 148150 | `b3ea171484c2ecc2ae2e941bab95aceceb2899c703e938141c56fee35bf18ddb` | 2026-09-16 14:57:09 | v12 |
| `test-plan.v13.json` | v13 — generator/JSON resync after the v12 hand-edit | 150245 | `b8bae3c8c3adb8803d721372dad6d4b8c852074b8d1c3274e33fe1fcb6185171` | 2026-09-16 15:13:07 | v13 |
| `test-plan.v14.json` | v14 — t11 scope closure | 151276 | `316ee352f9621bea423b638cf952042295d6548af59bab4eda62cbcdb2f7c851` | 2026-09-16 15:18:50 | v14 |
| `test-plan.v15.json` | v15 — sense-network mechanism + bring-up criteria | 156206 | `b3af9c7550bf3adffdb6416e5a3d3074df952c31b15f4718d423006fab6d3738` | 2026-09-16 15:28:53 | v15 |
| `test-plan.v16.json` | v16 — final U-numbering alignment | 157175 | `33a0a4e46a209f036bfd5c0fc0316ae51cc67ce64277d2be78173c0615498e6d` | 2026-09-16 15:31:18 | v16 |
| `test-plan.v17.json` | v17 — pulse-cap metric + option-(b) convergence | 160645 | `29c0206ebaeb341dde9739709a91141dd75d0fbd47f2be2cfe6bc2a9e147b508` | 2026-09-16 18:07:25 | v17 |
| `test-plan.v18.json` | v18 — verbatim U11 alignment — **stale/void as an anchor** | 161516 | `0578bd5e5b17f7bee0feafb75641c22f4105eb0bcf410126def47bdd5920ea62` | 2026-09-16 18:09:28 | v18 |
| `test-plan.v20.json` | **v20early** — earlier build of revision v20 | 166099 | `1925250df53f8b52126fdda9efa84ae84fe2bc8e529867e0965fc0ffe9a08016` | 2026-09-16 18:17:42 | v20 (t17 closure) |
| `test-plan.v20final.json` | **v20final** — later build of the same revision v20 | 166099 | `fabdd24f220d3b3e1eaf2bc782bf896adceb38074a72bffa7ba0d2d181ec8ed4` | 2026-09-16 19:04:49 | v20 (t17 closure) |

## Notes that prevent the known mis-readings

1. **Two same-size "v20" byte states are not two versions.** `v20early` and `v20final` are builds of the *same*
   `revision v20`; the only difference is three `inputArtifacts` hashes (`setup-contract.json`
   `7f505fdb… → fd00a508…`, `dali_tm_meta.json`, `test_conditions.yaml`) because the generator recomputes input
   hashes at build time under `hashPolicy`. Neither is canonical: **v21 supersedes both.**
2. **`v11` and `v19` have no copies on disk.** They were produced between two snapshots (the retained copy is
   always taken from the *previous* build), so their hashes are **not reproducible from the tree**. A hash quoted
   for them can only come from a message, never from a file — treat it as unreproducible.
3. **`v18` is void as an anchor** and is retained only as history; it was superseded twice (v20, then v21).
4. Division of labour: this index is the plan side's own record. The downstream input pin lives in
   `implementation-input-pin.json`, which is owned by the setup side.
