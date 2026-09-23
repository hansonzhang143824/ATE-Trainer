import fs from 'node:fs';
import path from 'node:path';
import { implementationScope, isImplementationLabel } from './implementation-contract.js';
import { TRAINING_READ_ONLY, trainingProfileFor } from './expert-policy-registry.js';
import { agentPresetOf } from './session-preset.js';
import { receiptIdentityFor } from './receipt-scope.js';
import { loadTrainingBindings } from './training-bindings.js';
const SCHEMATIC_LABEL = 'PTC schematic expert';
/**
 * Tools that are NOT material access and are therefore allowed even for a
 * boundary-controlled specialist: its own result channel. `structured_output` is
 * how a dispatcher's `outputSchema` is satisfied — denying it made every pinned
 * dispatch end with a boundary error instead of a result, which a real host run
 * exposed and no unit test had covered.
 */
const NON_MATERIAL_TOOLS = new Set(['run_code', 'report', 'structured_output']);
const DFT_PREFIX = 'PTC dft expert';
const IMPLEMENTATION_PREFIX = 'PTC implementation expert';
const SCHEMATIC_TEAM_LABEL = /^agent-teams:[^:]+:schematic-expert$/;
const DENIED = 'PTC material boundary: this source specialist may access only its assigned input and output paths.';
/**
 * Retired artifacts are never an input for any PTC specialist, even when a copy
 * sits inside a folder the specialist may otherwise read (the schematic output
 * root historically held `schematic-ir.json`). Reading one, or resolving a path
 * through one, is refused with its own message so the reason is unmistakable.
 */
const RETIRED_ARTIFACTS = Object.freeze(['schematic-ir.json']);
const RETIRED_DENIED = 'PTC material boundary: schematic-ir.json is a retired artifact and is never a PTC input.';
function retiredArtifact(value) {
  if (typeof value !== 'string' || value === '') return false;
  const base = path.basename(value).toLowerCase();
  return RETIRED_ARTIFACTS.some((name) => base === name);
}
function inside(candidate, root) { const relative = path.relative(root, candidate); return relative === '' || (relative !== '..' && !relative.startsWith(`..${path.sep}`) && !path.isAbsolute(relative)); }
function realTarget(raw, cwd, existing) { if (typeof raw !== 'string' || !raw.trim()) return null; const absolute = path.resolve(cwd, raw); try { if (existing || fs.existsSync(absolute)) return fs.realpathSync.native(absolute); let parent = path.dirname(absolute); const suffix = [path.basename(absolute)]; while (!fs.existsSync(parent)) { const next = path.dirname(parent); if (next === parent) return null; suffix.unshift(path.basename(parent)); parent = next; } return path.join(fs.realpathSync.native(parent), ...suffix); } catch { return null; } }
function labelOf(agent) { return agent?.session?.events?.findLast((event) => event.type === 'subagent/descriptor')?.data?.label; }
/** Captain puts the complete authorized DFT set in the descriptor. Unscoped DFT is denied. */
export function dftScope(agent, workspaceRoot) { const cwd = agent?.session?.header?.cwd; if (typeof cwd !== 'string' || !inside(path.resolve(cwd), path.resolve(workspaceRoot))) return null; const label = labelOf(agent); const match = typeof label === 'string' && /^PTC dft expert \[(TM\d+(?:,TM\d+)*)\]$/.exec(label); return match ? new Set(match[1].split(',')) : null; }
function hasDftDescriptor(agent) { const label = labelOf(agent); return typeof label === 'string' && (label === DFT_PREFIX || label.startsWith(`${DFT_PREFIX} `) || /^agent-teams:[^:]+:dft-expert$/.test(label)); }
export function isDftExpert(agent, workspaceRoot) { return dftScope(agent, workspaceRoot) !== null; }
export function isSchematicExpert(agent, workspaceRoot) { const cwd = agent?.session?.header?.cwd; if (typeof cwd !== 'string' || !inside(path.resolve(cwd), path.resolve(workspaceRoot))) return false; const label = labelOf(agent); return label === SCHEMATIC_LABEL || label === 'schematic-expert' || (typeof label === 'string' && SCHEMATIC_TEAM_LABEL.test(label)); }
function commandTm(command, kind) { if (kind === 'refresh') { const m = /^python scripts\/refresh_dft_meta_from_source\.py --source project\/DALI\/Input_GlobalMaterial\/Dali_testmode\.xlsx --tm (TM\d+) --meta project[\\/]DALI[\\/]Output_Global_Material[\\/]dft[\\/](TM\d+)[\\/]dft-meta\.json --expected-sha [a-f0-9]{64}$/.exec(command); return m && m[1] === m[2] ? m[1] : null; } if (kind === 'render') { const m = /^python scripts\/render_dft_conditions_yaml\.py --tm (TM\d+) --out project[\\/]DALI[\\/]Output_Global_Material[\\/]dft[\\/](TM\d+)[\\/]dft-conditions\.yaml --expected-sha [a-f0-9]{64}$/.exec(command); return m && m[1] === m[2] ? m[1] : null; } const m = /^python scripts\/validate_dft_outputs\.py --tm (TM\d+)$/.exec(command); return m ? m[1] : null; }
function dftDecision(exec, root, cwd, scope) { const args = exec.arguments; if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined; if (exec.name === 'pwsh') { const command = args?.command || ''; const hash = 'python scripts/hash_ate_plaintext.py project/DALI/Input_GlobalMaterial/Dali_testmode.xlsx'; const tm = command === hash ? true : ['refresh','render','validate'].map((kind) => commandTm(command,kind)).find(Boolean); return tm && (tm === true || scope.has(tm)) && !args?.workdir && !args?.run_in_background && !args?.sandbox_permissions ? undefined : DENIED; } if (exec.name !== 'read' && exec.name !== 'write') return DENIED; const target = realTarget(args?.file_path,cwd,exec.name === 'read'); if (!target) return DENIED; if (retiredArtifact(args?.file_path) || retiredArtifact(target)) return RETIRED_DENIED; const input = path.join(root,'project','DALI','Input_GlobalMaterial','Dali_testmode.xlsx'); const output = path.join(root,'project','DALI','Output_Global_Material','dft'); const permitted = [...scope].map((tm) => path.join(output,tm)); const error = path.join(root,'project','DALI','ErrorLog','dft-expert.log');
  // [31] read-only references (user ruling 2026-09-22): parsing may consult
  // register configs, schematic products, the project special-information
  // file and the parsing-rule manual; none of them may be written.
  const references = [ path.join(root,'User_input'), path.join(root,'project','DALI','reg_config'), path.join(root,'project','DALI','Output_Global_Material','schematic'), path.join(root,'project','DALI','Input_GlobalMaterial','DALI-special-information.json') ];
  const referenceRead = exec.name === 'read' && references.some((r) => target === r || inside(target, r));
  return target === input || permitted.some((folder) => inside(target,folder)) || referenceRead || (exec.name === 'write' && target === error) ? undefined : DENIED; }
function implementationDecision(exec, root, cwd, scope) {
  const args = exec.arguments;
  if (scope.error) return `PTC implementation contract: ${scope.error}`;
  if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined;
  if (exec.name === 'pwsh') {
    const trial = path.relative(root, scope.trial).split(path.sep).join('/');
    const permitted = [
      `python scripts/apply_ptc_source_comments.py --trial ${trial} --source D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp`,
      `python scripts/verify_implementation_batch.py ${trial}`,
      `python scripts/write_implementation_deliverable.py ${trial}`,
    ];
    return permitted.includes(args?.command || '') && !args?.workdir && !args?.run_in_background && !args?.sandbox_permissions
      ? undefined : 'PTC implementation contract: only the signed template, comment, verification, and delivery commands are allowed.';
  }
  if (exec.name === 'subagent' || exec.name === 'glob' || exec.name === 'grep' || (exec.name !== 'read' && exec.name !== 'write')) {
    return 'PTC implementation contract: old trials, status files, directory enumeration, and delegation are forbidden. Use the signed recipe.';
  }
  const target = realTarget(args?.file_path, cwd, exec.name === 'read');
  if (!target) return DENIED;
  const implementationOutput = path.join(scope.trial, 'implementation');
  const error = path.join(root, 'project', 'DALI', 'ErrorLog', 'ate-implementer.log');
  if (target === scope.contractPath || inside(target, implementationOutput) || target === error) return undefined;
  if (scope.sourceFiles.has(target)) {
    if (exec.name === 'read') return undefined;
    const writable = new Set([
      path.resolve('D:/PROJECT6-DALI/ForCodexDebug/source/test.cpp'),
      path.resolve('D:/PROJECT6-DALI/ForCodexDebug/source/sub.cpp'),
    ]);
    return writable.has(target) ? undefined : DENIED;
  }
  return 'PTC implementation contract: read only the current signed method contract and named formal source files; do not inspect old trials or status.';
}

function schematicDecision(exec, root, cwd) { const args = exec.arguments; if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined; if (exec.name === 'pwsh') { const hashCsv='python scripts/hash_ate_plaintext.py project/DALI/Input_GlobalMaterial/Dali-SCH.csv'; const hashConfirmed='python scripts/hash_ate_plaintext.py project/DALI/Input_GlobalMaterial/sch_confirmed.json'; const hashCbit='python scripts/hash_ate_plaintext.py project/DALI/Input_GlobalMaterial/CBIT表-DALI.xlsx'; const generate=/^python scripts\/generate_schematic_txt\.py --source project\/DALI\/Input_GlobalMaterial\/Dali-SCH\.csv --confirmed project\/DALI\/Input_GlobalMaterial\/sch_confirmed\.json --cbit project\/DALI\/Input_GlobalMaterial\/CBIT表-DALI\.xlsx --out-dir project\/DALI\/Output_Global_Material\/schematic --expected-source-sha [a-f0-9]{64} --expected-confirmed-sha [a-f0-9]{64} --expected-cbit-sha [a-f0-9]{64}$/; const valid=args?.command===hashCsv || args?.command===hashConfirmed || args?.command===hashCbit || args?.command==='python scripts/validate_schematic_outputs.py' || generate.test(args?.command || ''); return valid && !args?.workdir && !args?.run_in_background && !args?.sandbox_permissions ? undefined : DENIED; } if (exec.name !== 'read' && exec.name !== 'write') return DENIED; const target=realTarget(args?.file_path,cwd,exec.name === 'read'); if (!target) return DENIED; if (retiredArtifact(args?.file_path) || retiredArtifact(target)) return RETIRED_DENIED; const inputs=new Set([path.join(root,'project','DALI','Input_GlobalMaterial','Dali-SCH.csv'),path.join(root,'project','DALI','Input_GlobalMaterial','sch_confirmed.json'),path.join(root,'project','DALI','Input_GlobalMaterial','CBIT表-DALI.xlsx')]); const output=path.join(root,'project','DALI','Output_Global_Material','schematic'); const error=path.join(root,'project','DALI','ErrorLog','schematic-expert.log'); return inputs.has(target) || inside(target,output) || (exec.name === 'write' && target === error) ? undefined : DENIED; }
const TRAINING_DENIED = 'PTC training boundary: a training session may write only its own master profile (metadata, instructions, output contract, cases, evaluation, CHANGELOG). Published versions, status.json, project code, production artifacts and other profiles are read-only here.';
/**
 * The training-session rule (handoff rule 6).
 *
 * Keyed off the DSH preset in the session header rather than off `workspaceRoot`:
 * a training session's workspace is wherever the user opened it while the
 * boundary's root is the deployment's workspace, so a root-scoped check would
 * never fire for the very sessions this rule is about. Reads stay unrestricted
 * (the rule constrains what training may CHANGE); writes are confined to the
 * profile's own draft area, and the only shell commands it may run are the two
 * gated scripts that own evaluation and release.
 *
 * INFERENCE, flagged for review: allowing the gated publisher means a training
 * session can still create `versions/vN` and update `publishedVersion`, which
 * rule 6 lists as forbidden for a training profile. It is allowed here because
 * handoff section 5.1 has the user run evaluate-then-publish from the training
 * session, and the publisher refuses unless a full evaluation passed, refuses to
 * overwrite a version, and keeps the previous one. Hand-editing those files is
 * denied. If the intent is that only the Captain may release, drop the
 * `publishing` branch below and this becomes strictly draft-only.
 */
const PUBLISHED_DENIED = 'PTC master boundary: a published version snapshot and status.json are immutable to every session; release them with scripts/publish_expert_profile.py, which refuses to overwrite a version and keeps the previous one.';
/**
 * Published master assets are protected from EVERY session by the path alone.
 *
 * This exists because the training rule above is keyed off the session's PRESET,
 * resolved the way DSH resolves it — and that value is demonstrably absent in a
 * headless session (a real run recorded `agentPreset: null`), leaving the
 * question of whether a GUI session carries it unverified. A rule whose only
 * protection depends on that value would be unproven protection, so immutability of `versions/**` and
 * `status.json` is enforced here without it. Draft assets stay editable.
 */
function publishedAssetDenial(exec, cwd) {
  if (exec.name !== 'write') return undefined;
  const target = realTarget(exec.arguments?.file_path, cwd, false);
  if (!target) return undefined;
  const marker = path.join(path.resolve(cwd), 'team', 'expert-profiles');
  if (!inside(target, marker)) return undefined;
  const parts = path.relative(marker, target).split(path.sep).join('/').split('/');
  if (parts.length >= 3 && parts[1] === 'versions') return PUBLISHED_DENIED;
  if (parts.length === 2 && parts[1] === 'status.json') return PUBLISHED_DENIED;
  return undefined;
}

function trainingDecision(exec, cwd, profileId, allowPublish = true) {
  const args = exec.arguments;
  if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined;
  // A training session never dispatches: the master is being edited, not run.
  if (exec.name === 'subagent') return 'PTC training boundary: a training session does not dispatch specialists; it edits its own draft.';
  const profileRoot = path.join(path.resolve(cwd), 'team', 'expert-profiles', profileId);
  if (exec.name === 'pwsh') {
    const command = typeof args?.command === 'string' ? args.command.trim() : '';
    const permitted = new Set([
      `python scripts/evaluate_expert_profile.py --profile ${profileId} --version draft`,
      `python scripts/evaluate_expert_profile.py --profile ${profileId} --version draft --skip-regression`,
    ]);
    const publishing = allowPublish && new RegExp(`^python scripts/publish_expert_profile\\.py --profile ${profileId} --version v[0-9]+$`).test(command);
    return (permitted.has(command) || publishing) && !args?.workdir && !args?.run_in_background && !args?.sandbox_permissions ? undefined : TRAINING_DENIED;
  }
  if (exec.name !== 'write') return undefined;
  const target = realTarget(args?.file_path, cwd, false);
  if (!target) return TRAINING_DENIED;
  const relative = path.relative(profileRoot, target).split(path.sep).join('/');
  if (inside(target, profileRoot)
    && !TRAINING_READ_ONLY.some((name) => relative === name || relative.startsWith(`${name}/`))) return undefined;
  // Address-book extension ([28]): training-material snapshot writes and
  // verification products come from Training_Materials/_expert_bindings.json —
  // the same address book the trainer consumes. Fail-closed: unreadable or
  // invalid bindings keep the profileRoot-only boundary above.
  const { entry, reason } = loadTrainingBindings(cwd, profileId);
  if (!entry) return `${TRAINING_DENIED} (bindings: fallback - ${reason})`;
  if (inside(target, entry.writes)) return undefined;
  if (entry.prefix && inside(target, entry.verification)
    && path.basename(target).startsWith(entry.prefix)) return undefined;
  return TRAINING_DENIED;
}

const DOWNSTREAM_CLASSES = new Set(['strategy-standard', 'method-standard', 'review-readonly', 'implementation-standard', 'compile-standard', 'evolution-proposal']);
// The approved VS project root the implementer compiles into and the compile
// diagnostician builds from. It lives outside the PTC workspace root on purpose;
// the boundary allows it explicitly for the classes whose contract names it.
const TARGET_SOURCE_ROOT = 'D:/PROJECT6-DALI/ForCodexDebug';
const TRIM_STANDARD_DIRS = ['knowledge/standards', 'knowledge/references/L4-Golden-code'];
const DOWNSTREAM_DENIED = 'PTC material boundary: this specialist may access only its assigned run inputs and its own stage outputs.';
const DOWNSTREAM_NO_TRIALS = 'PTC material boundary: this pinned dispatch recorded no trial directories, so its run scope cannot be verified.';
/** The gate command each downstream class may run (prefix match; no workdir, no background, no sandbox). */
const CLASS_GATE_COMMANDS = {
  'strategy-standard': /^python scripts\/validate_strategy_contract\.py(?: |$)/,
  'method-standard': /^python scripts\/validate_method_contract\.py(?: |$)/,
  'review-readonly': /^python scripts\/(?:review_method_batch|verify_implementation_batch|validate_strategy_contract|validate_method_contract)\.py(?: |$)/,
  'implementation-standard': /^python scripts\/(?:verify_implementation_batch|write_implementation_deliverable|apply_ptc_source_comments|render_register_writes|ptc_trim_validation)\.py(?: |$)/,
  'compile-standard': /^python scripts\/run_ptc_incremental_compile\.py(?: |$)/,
  'evolution-proposal': /^python scripts\/validate_evolution_proposal\.py(?: |$)/,
};
/**
 * Receipt-scoped boundary for the downstream experts (handoff second batch).
 *
 * The scope comes ONLY from the pinned receipt: its trialDirs are the run's
 * frozen per-TM trial directories, its targetTms the authorised set. Read roots
 * per class: strategy reads the accepted DFT output of its TMs plus the
 * schematic map; method reads the strategy contracts of its trials; the
 * reviewer reads its trials (contracts, artifacts, evidence) plus DFT outputs.
 * Writes go to the trial's own stage directory and the expert's error log.
 */
function downstreamDecision(exec, root, cwd, receipt) {
  const cls = receipt.executionClass;
  const args = exec.arguments;
  if (NON_MATERIAL_TOOLS.has(exec.name)) return undefined;
  if (exec.name === 'pwsh') {
    const command = typeof args?.command === 'string' ? args.command : '';
    const gates = CLASS_GATE_COMMANDS[cls];
    return gates && gates.test(command) && !args?.workdir && !args?.run_in_background && !args?.sandbox_permissions ? undefined : DOWNSTREAM_DENIED;
  }
  if (exec.name !== 'read' && exec.name !== 'write') return DOWNSTREAM_DENIED;
  // Receipt trialDirs are workspace-relative (or absolute); resolve against the
  // boundary root, never the process cwd.
  const trials = Array.isArray(receipt.trialDirs) ? receipt.trialDirs.map((p) => path.resolve(root, String(p))) : [];
  if (cls === 'evolution-proposal') {
    // Non-stage role: no trials. The scope is closed run evidence and the PTC
    // rule/governance documents; writable only through proposal documents.
    const target = realTarget(args?.file_path, cwd, exec.name === 'read');
    if (!target) return DOWNSTREAM_DENIED;
    const readable = [path.join(root, 'team', 'artifacts'), path.join(root, 'team', 'ptc')];
    const writable = [path.join(root, 'team', 'expert-profiles', 'evolution-expert', 'proposals'), path.join(root, 'project', 'DALI', 'ErrorLog', 'evolution-expert.log')];
    if (exec.name === 'read' && (readable.some((folder) => inside(target, folder)) || writable.some((folder) => inside(target, folder)))) return undefined;
    if (exec.name === 'write' && writable.some((folder) => inside(target, folder))) return undefined;
    return DOWNSTREAM_DENIED;
  }
  if (trials.length === 0) return DOWNSTREAM_NO_TRIALS;
  const target = realTarget(args?.file_path, cwd, exec.name === 'read');
  if (!target) return DOWNSTREAM_DENIED;
  const errorLog = (name) => path.join(root, 'project', 'DALI', 'ErrorLog', name);
  const tms = Array.isArray(receipt.targetTms) ? receipt.targetTms : [];
  const dftOf = (tm) => path.join(root, 'project', 'DALI', 'Output_Global_Material', 'dft', String(tm));
  const schematic = path.join(root, 'project', 'DALI', 'Output_Global_Material', 'schematic');
  const stageDir = (name) => trials.map((trial) => path.join(trial, name));
  const readable = cls === 'strategy-standard'
    ? [...tms.map(dftOf), schematic]
    : cls === 'method-standard' ? stageDir('strategy')
      : cls === 'implementation-standard'
        ? [...stageDir('method'), ...stageDir('strategy'), ...TRIM_STANDARD_DIRS.map((dir) => path.join(root, dir)), TARGET_SOURCE_ROOT]
        : cls === 'compile-standard'
          ? [...stageDir('implementation'), ...stageDir('review'), ...stageDir('method'), TARGET_SOURCE_ROOT]
          : [...trials, ...tms.map(dftOf)];
  const writable = cls === 'strategy-standard' ? [...stageDir('strategy'), errorLog('strategy-expert.log')]
    : cls === 'method-standard' ? [...stageDir('method'), errorLog('method-expert.log')]
      : cls === 'implementation-standard' ? [...stageDir('implementation'), errorLog('implementer.log'), TARGET_SOURCE_ROOT]
        : cls === 'compile-standard' ? [...stageDir('compile'), errorLog('compile-diagnostician.log')]
          : [...stageDir('review'), errorLog('rule-reviewer.log')];
  // Reads: readable roots plus the expert's own writable stage dir. Writes:
  // writable roots ONLY — an upstream contract stays read-only even though it
  // is a declared read source.
  if (exec.name === 'read' && (readable.some((folder) => inside(target, folder)) || writable.some((folder) => inside(target, folder)))) return undefined;
  if (exec.name === 'write' && writable.some((folder) => inside(target, folder))) return undefined;
  return DOWNSTREAM_DENIED;
}

export function decision(exec, workspaceRoot, options = {}) { const root=path.resolve(workspaceRoot); const cwd=exec.agent?.session?.header?.cwd || root; const args=exec.arguments;
  // A training session is judged by its own rule, whatever the workspace root is.
  // The preset comes from DSH's own resolution order (newest selection event, then
  // the creation header) — a header-only read misses a session the user switched
  // INTO a training preset.
  const trainingProfile = trainingProfileFor(agentPresetOf(exec.agent));
  if (trainingProfile !== undefined) return trainingDecision(exec, cwd, trainingProfile, options.allowTrainingPublish !== false);
  // Independent of any preset: published master assets are immutable by path.
  const published = publishedAssetDenial(exec, cwd);
  if (published !== undefined) return published;
  if (exec.name === 'subagent' && inside(path.resolve(cwd),root)) { const prompt=typeof args?.prompt === 'string' ? args.prompt : ''; if (prompt.includes('team/roles/schematic-expert.md') && args?.description !== SCHEMATIC_LABEL) return `PTC schematic dispatch must use description "${SCHEMATIC_LABEL}".`; if (prompt.includes('team/roles/dft-expert.md') && !/^PTC dft expert \[TM\d+(?:,TM\d+)*\]$/.test(args?.description || '')) return 'PTC dft dispatch must name its authorized TM set in the DFT descriptor.'; if ((prompt.includes('team/roles/ate-implementer.md') || args?.description === 'ate-implementer') && !String(args?.description || '').startsWith(IMPLEMENTATION_PREFIX)) return 'PTC implementation dispatch must use a Hook-generated signed method-contract recipe descriptor.'; if (String(args?.description || '').startsWith(IMPLEMENTATION_PREFIX)) return undefined; }
  // Receipt-first identity (handoff 7.1). With no receipt on disk this returns
  // 'unpinned' for every agent and the legacy label logic below runs unchanged,
  // so a deployment that has not adopted pinned dispatch keeps today's behaviour.
  const pinned = receiptIdentityFor(root, exec.agent);
  if (pinned.kind === 'mismatch') return `PTC pinned identity: ${pinned.reason}.`;
  if (pinned.kind === 'pinned') {
    if (pinned.executionClass === 'input-dft') return dftDecision(exec, root, cwd, new Set(pinned.targetTms));
    if (pinned.executionClass === 'input-schematic') return schematicDecision(exec, root, cwd);
    if (DOWNSTREAM_CLASSES.has(pinned.executionClass)) return downstreamDecision(exec, root, cwd, pinned.receipt);
  }
  const implementation=implementationScope(exec.agent,root); if (implementation || isImplementationLabel(labelOf(exec.agent))) return implementationDecision(exec,root,cwd,implementation || {error:'missing Hook-generated contract recipe descriptor'}); const scope=dftScope(exec.agent,root); if (scope) return dftDecision(exec,root,cwd,scope); if (hasDftDescriptor(exec.agent)) return DENIED; return isSchematicExpert(exec.agent,root) ? schematicDecision(exec,root,cwd) : undefined; }
