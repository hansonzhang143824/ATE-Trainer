# t9 evidence note - setup-contract idempotency (frozen at revision 21)

Purpose: the acceptance report (t9) must state HOW the setup contract freeze was made reproducible.
This note is written by setup-architect (t18, the final freeze gate) and may be cited verbatim.

## The construction that makes two runs byte-identical

`generatedAt` is DERIVED FROM the contract revision, not read from the wall clock:
`GENERATED_AT = "2026-09-16 16:02:00 (revision 21)"` alongside `CONTRACT_REVISION = 21`.

A generator that stamps `datetime.now()` can NEVER emit two byte-identical files, so "run twice, compare
hashes" would fail by construction. Making the timestamp part of the content is the only construction that
satisfies BOTH requirements at once: the artifact still carries a `generatedAt` field, and two consecutive
runs produce identical bytes. Verified twice: in t16 (intermediate self-check) and in t18 (final gate).

## Frozen facts

- artifact: team/artifacts/acceptance-20260916-dali10/setup-contract.json
- revision: 21, generatedAt "2026-09-16 16:02:00 (revision 21)"
- size: 328,723 bytes
- sha256 (python plaintext, hashed over BYTES): 7f505fdbbb60aa798fb79d16d431f095ff26693406633de9132b0e1cde7ee59f
- two consecutive generator runs: identical bytes (same hash twice)
- schema: python scripts/validate_team_artifact.py setup-contract <artifact> -> PASS, exit 0
- no concurrent writer during the two-run window (only setup-contract.json changed mtime; see t18-freeze-evidence.json)
- generator re-run reproduces the on-disk artifact byte-for-byte (generator aligned to artifact)

## Hash-method caveat for the report

Hashes MUST be computed with python over the file BYTES. PowerShell `Get-FileHash` reads ciphertext for files
inside this run directory and will not match; hashing a decoded-then-re-encoded string differs as well (CRLF vs LF).
