# PTC Global Hash Contract

This contract applies to Captain and every PTC specialist.

## Algorithm and encoding

- Algorithm: SHA-256.
- Representation: lowercase hexadecimal, exactly 64 characters.
- No MD5, SHA-1, SHA-512, uppercase digest, shortened digest, or model-derived
  digest is valid evidence.

## Byte view

- Canonical DLP-protected input material: hash the plaintext byte view exposed
  by Python, using `scripts/hash_ate_plaintext.py`.
- Generated artifact: hash the exact bytes stored on disk. Do not decode,
  normalize newlines, canonicalize JSON, re-render YAML, or otherwise transform
  the bytes before hashing.

The algorithm is identical in both cases. Only the authoritative byte view
differs because a protected input has both a wrapper view and a plaintext view.

## Ownership

The deterministic producer or validator owns hash calculation. An agent copies
the digest emitted by that command and never selects an alternative tool. If an
approved command does not emit the required digest, the agent reports BLOCKED.

For DFT delivery:

- `hash_ate_plaintext.py` emits the workbook plaintext SHA-256.
- `refresh_dft_meta_from_source.py` emits `metaSha256` for `dft-meta.json`.
- `render_dft_conditions_yaml.py` emits `outputSha256` for
  `dft-conditions.yaml`.
- `dft-semantic-review.json` records those two artifact digests in
  `reviewedArtifacts`; it does not hash itself.

Any write after hashing invalidates the old digest and requires deterministic
regeneration before review or gate execution.

## Overwrite regression

PTC DFT delivery uses a shared per-TM output directory. Before writing, compare
the current workbook plaintext SHA-256 and run the complete DFT output gate.
A ready, fully bound set is left byte-for-byte unchanged. A missing set is
created in full. A stale or mismatched set is overwritten in full and rebound
to the current source and artifact SHA-256 values. This behavior is an explicit
overwrite regression, not isolated output storage.
