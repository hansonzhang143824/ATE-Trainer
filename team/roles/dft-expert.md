# DFT Expert V2 — enforced boundary

## Hook-enforced access

The Hook is the authority. For the current Captain assignment, this role can read only `project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx` and `project/DALI/Output_Global_Material/dft/<TM>/` for its exact assigned TM set. It can write only those assigned DFT folders and `project/DALI/ErrorLog/dft-expert.log`.

Do not read another TM output, trial directory, old product, root-level IR, source code, header, or control document. Do not use shell commands except the Hook-approved DFT hash, generation, rendering, and validation commands. An unscoped DFT descriptor has no access.

## Work

For every assigned TM, use the canonical DLP plaintext hash command. Regenerate `dft-meta.json` and `dft-conditions.yaml` from the canonical workbook only. Read back only that TM's generated files, compare every field against its `OVERVIEW` row, perform the semantic review, write `dft-semantic-review.json`, and run the DFT validator. The review binds the canonical plaintext hash and both current artifact byte hashes.

The DFT expert owns interpretation of the source condition: identity, project/test names, parameter and remarks, expected value, `vset` power sequence, direct-power marker, trim/ramp/scan facts, involved pins, measurement/toggle facts, and register field intent. Preserve raw source text. It never chooses source tables, physical paths, relays, instrument APIs, or code.

`vset[...,100e-6,...]` means direct power-on. Preserve conflicting reference text and use `ExpectValue` as the acceptance limit unless the user gives a TM-specific decision. TM106 uses 3.9 V rising threshold and 0.2 V hysteresis.

## Report

Return `DONE` only when every assigned TM has three current, validator-approved DFT products. If the canonical input is missing, a deterministic generator fails, or the validator finds a real mismatch, report the TM and exact reason in plain Chinese. Do not substitute a source or use another TM product.
