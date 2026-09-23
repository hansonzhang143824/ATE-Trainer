# PTC DFT Expert — CHANGELOG

## draft (unpublished)

- Initial master assets: metadata, instructions, output contract, the TM106 golden
  case and the case index.
- Declared executionClass `input-dft`; the class name is read from the plugin's
  `expert-policy-registry.js` at evaluation time, so this profile cannot drift
  away from the enforced policy without the evaluation failing.
- TM106 asserts the structural contract, the canonical input identity and the
  read-source boundary only. Its expected DFT semantic values are marked
  `PENDING_DOMAIN_INPUT` and no evaluation may claim to have checked them.
