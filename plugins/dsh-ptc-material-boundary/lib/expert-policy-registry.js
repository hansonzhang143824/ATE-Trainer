/**
 * The executionClass registry (handoff section 4.2).
 *
 * The handoff is explicit that this table must exist in CODE and be read by the
 * dispatcher and the guard together — a table that lives only in Markdown is not
 * enforcement. This module is pure data plus validation: it declares what each
 * class may read, where it may write, and which gates it must pass, using paths
 * relative to the workspace root with `<TM>` as the only placeholder.
 *
 * It deliberately performs no filesystem access and holds no state, so both the
 * guard and the dispatcher can read one authoritative answer, and tests can
 * assert the table without a workspace.
 */

/**
 * Path helper placeholders allowed in a declaration: `<TM>` (the authorised test
 * mode) and `<run>` (the run's own directory). Nothing else — an undeclared
 * placeholder would silently resolve to a real path at enforcement time.
 */
const PLACEHOLDER = /^<(TM|run)>$/;

/** @type {Readonly<Record<string, {readable: readonly string[], writable: readonly string[], gates: readonly string[]}>>} */
export const EXECUTION_CLASSES = Object.freeze({
  'input-dft': Object.freeze({
    readable: Object.freeze([
      'project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx',
      'project/DALI/Output_Global_Material/dft/<TM>', // self-check of its own current output only
    ]),
    writable: Object.freeze([
      'project/DALI/Output_Global_Material/dft/<TM>',
      'project/DALI/ErrorLog/dft-expert.log',
    ]),
    gates: Object.freeze(['input hash', 'field completeness', 'readSources', 'dft output validation']),
  }),
  'input-schematic': Object.freeze({
    readable: Object.freeze([
      'project/DALI/Input_GlobalMaterial/Dali-SCH.csv',
      'project/DALI/Input_GlobalMaterial/sch_confirmed.json',
      'project/DALI/Input_GlobalMaterial/CBIT表-DALI.xlsx',
      'project/DALI/Output_Global_Material/schematic', // self-check only
    ]),
    writable: Object.freeze([
      'project/DALI/Output_Global_Material/schematic',
      'project/DALI/ErrorLog/schematic-expert.log',
    ]),
    gates: Object.freeze(['input hash', 'readSources', 'connect map / statistic validation']),
  }),
  'strategy-standard': Object.freeze({
    readable: Object.freeze([
      'project/DALI/Output_Global_Material/dft/<TM>',
      'project/DALI/Output_Global_Material/schematic',
      'approved project headers and project rules',
    ]),
    writable: Object.freeze(['<run>/strategy']),
    gates: Object.freeze(['path', 'source table', 'relay combination', 'register source evidence']),
  }),
  'method-standard': Object.freeze({
    readable: Object.freeze(['<run>/strategy', 'approved reference material']),
    writable: Object.freeze(['<run>/method']),
    gates: Object.freeze(['method contract schema', 'scan / trim rules']),
  }),
  'implementation-standard': Object.freeze({
    readable: Object.freeze(['<run>/method', 'approved project sources and standards']),
    writable: Object.freeze(['approved target source files', '<run>/implementation']),
    gates: Object.freeze(['implementation batch checks', 'trim check', 'comment rules', 'power-down order']),
  }),
  'review-readonly': Object.freeze({
    readable: Object.freeze(['the reviewed stage contract, artifacts and evidence']),
    writable: Object.freeze(['<run>/review']),
    gates: Object.freeze(['review contract schema']),
  }),
  'compile-standard': Object.freeze({
    readable: Object.freeze([
      '<run>/implementation',
      '<run>/review',
      '<run>/method',
      'approved VS project files',
    ]),
    writable: Object.freeze(['<run>/compile', 'ErrorLog/compile-diagnostician.log']),
    gates: Object.freeze(['bounded incremental compile', 'current source hash binding', 'build report schema']),
  }),
  'evolution-proposal': Object.freeze({
    readable: Object.freeze([
      'closed run evidence and verified rule-improvement proposals',
      'team/ptc rule and governance documents',
    ]),
    writable: Object.freeze(['team/expert-profiles/evolution-expert/proposals', 'ErrorLog/evolution-expert.log']),
    gates: Object.freeze(['proposal schema', 'evidence binding']),
  }),
});

/**
 * The label shape the material boundary recognises for each class. A published
 * profile must declare exactly this string (with `<TM>` rendered from its target
 * TMs), otherwise the dispatcher refuses: `lib/policy.js` fails OPEN for a label
 * it does not recognise, so a caller-chosen label could otherwise hand a child no
 * boundary at all. `input-schematic` is deliberately TM-less — the schematic
 * product is one shared artifact, not one per test mode.
 */
export const RUNTIME_LABEL = Object.freeze({
  'input-dft': 'PTC dft expert [<TM>]',
  'input-schematic': 'PTC schematic expert',
  'strategy-standard': 'PTC strategy expert [<TM>]',
  'method-standard': 'PTC method expert [<TM>]',
  'review-readonly': 'PTC rule reviewer [<TM>]',
'implementation-standard': 'PTC implementer [<TM>]',
  'compile-standard': 'PTC compile diagnostician [<TM>]',
  'evolution-proposal': 'PTC evolution expert',
});

/**
 * Presets whose sessions are TRAINING sessions for one expert master (handoff
 * rule 6: a training profile may write only its own draft, cases, evaluation and
 * CHANGELOG — never production artifacts, project code, `versions/vN` or
 * `publishedVersion`).
 *
 * These are DSH preset ids. The session's preset is read through
 * `lib/session-preset.js`, which mirrors DSH's own resolution (newest
 * `agent-preset/selected` event first, creation header as the fallback) — the
 * header alone is NOT enough, because a session the user switched into a training
 * preset keeps its original header.
 * The training rule keys off this and NOT off the plugin's `workspaceRoot` on
 * purpose: a training session's workspace is wherever the user opened it, while
 * the boundary's root is the deployment's workspace, so a root-scoped check would
 * simply never fire for a training session.
 */
export const TRAINING_PRESET_PROFILE = Object.freeze({
  'ptc-dft-expert': 'ptc-dft-expert',
  'ptc-schematic-expert': 'ptc-schematic-expert',
  'strategy-expert': 'strategy-expert',
  'method-expert': 'method-expert',
  'rule-reviewer': 'rule-reviewer',
'ate-implementer': 'ate-implementer',
  'compile-diagnostician': 'compile-diagnostician',
  'evolution-expert': 'evolution-expert',
});

/** Paths inside a master profile that a training session may never write. */
export const TRAINING_READ_ONLY = Object.freeze(['versions', 'status.json']);

/** @param {unknown} presetId @returns {string | undefined} */
export function trainingProfileFor(presetId) {
  return typeof presetId === 'string' && Object.hasOwn(TRAINING_PRESET_PROFILE, presetId)
    ? TRAINING_PRESET_PROFILE[presetId]
    : undefined;
}

/**
 * The declared class of each expert master profile. A receipt claiming a class
 * that is not this profile's declared class is rejected (see dispatch-receipt).
 */
export const PROFILE_EXECUTION_CLASS = Object.freeze({
  'ptc-dft-expert': 'input-dft',
  'ptc-schematic-expert': 'input-schematic',
  'strategy-expert': 'strategy-standard',
  'method-expert': 'method-standard',
  'rule-reviewer': 'review-readonly',
  'ate-implementer': 'implementation-standard',
  'compile-diagnostician': 'compile-standard',
  'evolution-expert': 'evolution-proposal',
  'method-reviewer': 'review-readonly',
  'implementation-reviewer': 'review-readonly',
});

/** @param {unknown} value @returns {boolean} */
export function isExecutionClass(value) {
  return typeof value === 'string' && Object.hasOwn(EXECUTION_CLASSES, value);
}

/** @param {unknown} profileId @returns {string | undefined} */
export function executionClassForProfile(profileId) {
  return typeof profileId === 'string' ? PROFILE_EXECUTION_CLASS[profileId] : undefined;
}

/** @param {unknown} executionClass @returns {{readable: readonly string[], writable: readonly string[], gates: readonly string[]} | undefined} */
export function policyFor(executionClass) {
  return isExecutionClass(executionClass) ? EXECUTION_CLASSES[executionClass] : undefined;
}

/** @param {unknown} executionClass @returns {string | undefined} */
export function runtimeLabelFor(executionClass) {
  return typeof executionClass === 'string' && Object.hasOwn(RUNTIME_LABEL, executionClass)
    ? RUNTIME_LABEL[executionClass]
    : undefined;
}

/**
 * Whether a declared path uses only supported placeholders.
 * @param {unknown} declared @returns {boolean}
 */
export function isDeclaredPath(declared) {
  if (typeof declared !== 'string' || declared.trim() === '') return false;
  const angle = declared.match(/<[^>]*>/g) ?? [];
  return angle.every((token) => PLACEHOLDER.test(token));
}
