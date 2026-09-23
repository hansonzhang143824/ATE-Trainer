# TM109 captain ruling 001 — input hash dispute

Stage: after first dispatch; both `dft-expert` and `schematic-expert` returned BLOCKED on "input hash mismatch".
Status of freeze: **manifest hashes stand. No input replacement, no re-generation needed.**

## Cause (FACT, three independent readers)

Same two paths, same byte lengths, two *different* byte streams depending on the reader.

| Reader | DFT.csv | schematic-ir.json | Verdict |
|---|---|---|---|
| `scripts/prepare_input_sync.py` (Python 3.12 `hashlib`) | `b92d203fa6f152120a316b9e32c037f7c1c978e96424edf5a871f02e5cfe0fd4` | `35fdd1582958eb6e4fd63e29da59dec63dfe19e3fd6198d8cc8b8f727a5c7ff5` | matches manifest |
| harness `read` tool | real CSV text, 357 lines, header `Item,Function Name,...` | real JSON, line 2 `"runId": "acceptance-20260916-dali10"` | matches Python |
| sandboxed `pwsh`: `Get-FileHash`, `certutil`, `[IO.File]::ReadAllBytes` | `c87e601534d5d4cacea3a68793585473874cf541c44c4e10b68f1dd34485a5c5` | `7ef9d702892093a5de75031500f78a6d627e44d5130cc832be9292d2577d8bdc` | **outlier** |

Decisive evidence: `pwsh` reports magic bytes `54 53 5a 23` (`TSZ#`) and NUL bytes for *both* files, while the other two readers return parseable CSV / JSON text at the identical path and identical length (16862 / 454933 bytes). A non-CSV binary blob cannot be the file that both `prepare_input_sync.py` parsed into `rawRows` and the `read` tool renders as 357 CSV lines.

Conclusion: inside the sandboxed shell these two paths are presented as a shadowed `TSZ#` container. `Get-FileHash` / `certutil` are therefore unreliable *as input-freeze verification tools in this workspace*, and both specialists produced a false negative.

### Correction (evidence added later, conclusion unchanged)

`team/DIRECT_DISPATCH_STATE_MACHINE.md:46` documents this mechanism: DFT/schematic/source files are **DLP transparent-protected**, so a Windows byte reader can hash a `TSZ` wrapper instead of plaintext. The official tool is `python scripts/hash_ate_plaintext.py`, and Windows readers (`Get-FileHash`, `certutil`, `ReadAllBytes`, `Get-Content -AsByteStream`) are forbidden for these gates.

- Retracted wording: "sandbox shadow layer" / "shadowed view". The documented cause is the DLP wrapper. The digest anomaly is not a sandbox defect and no sandbox behaviour is in question.
- Unchanged: both input hashes were reproduced with the mandated hasher — DFT.csv `b92d203f…0fd4`, schematic-ir.json `35fdd158…7ff5` — matching the manifest. The freeze stands, and verification must run through `hash_ate_plaintext.py` or Python `hashlib` (identical plaintext read), never through Windows hash tools.

## Ruling

1. `canonicalInputs.dft.sha256` and `canonicalInputs.schematic.sha256` in `input-manifest.json` are correct and authoritative.
2. Input freeze is valid. Neither input is stale, missing, or corrupt; nothing is re-supplied.
3. Verification of these inputs must use Python `hashlib` (the same hasher as the mandatory gate), or the harness `read` tool. `Get-FileHash` / `certutil` must not be used for the TM109 input-freeze check.
4. Both roles are re-dispatched unchanged, same paths, same declared hashes, same output paths.

## Not in scope

No production code. No DFT or schematic interpretation by the captain. The two `*-error-log.json` files are retained as historical evidence of the false negative; no derived output is invalidated by them.
