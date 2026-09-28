// CM-004: JSON Schema and semantic validation tests for the DSH native PTC
// Release Bundle manifest (schemaVersion 1).
//
// Zero external dependencies. Run with:
//   node --test plugins/dsh-ptc-control-plane/test/release-manifest-schema.test.mjs
//
// JSON Schema cannot express every frozen rule (path ordering, path-key
// uniqueness, bundleDigest binding, snapshot coverage, verification
// consistency, previousReleaseId != releaseId). Those rules live here as
// semantic checks next to the embedded JSON Schema subset validator.

import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import test from 'node:test';
import { fileURLToPath } from 'node:url';
import { digestReleaseEntries, verifyReleaseDirectory } from '../lib/release-integrity.js';

const here = path.dirname(fileURLToPath(import.meta.url));
const schemaPath = path.resolve(
  here,
  '../../../team/ptc/native-control-plane/schemas/release-manifest.schema.json',
);
const fixtureRoot = path.join(here, 'fixtures', 'release-manifest');
const schema = JSON.parse(fs.readFileSync(schemaPath, 'utf8'));

const SNAPSHOT_CATEGORIES = ['profiles', 'orchestration', 'contracts', 'policies', 'verification'];
const DATE_TIME = /^\d{4}-\d{2}-\d{2}[Tt]\d{2}:\d{2}:\d{2}(\.\d+)?([Zz]|[+-]\d{2}:\d{2})$/;

// ---------------------------------------------------------------------------
// Minimal JSON Schema draft 2020-12 subset validator (in-test, zero deps).
// Supports exactly the keywords used by release-manifest.schema.json.
// ---------------------------------------------------------------------------
const SUPPORTED_KEYWORDS = new Set([
  '$schema', '$id', 'title', 'description', 'type', 'const', 'enum', 'required',
  'properties', 'additionalProperties', 'items', 'minItems', 'uniqueItems',
  'pattern', 'minLength', 'minimum', 'maximum', 'not', 'anyOf', 'contains', 'format',
]);
const SCHEMA_BEARING_KEYWORDS = new Set([
  'properties', 'items', 'not', 'anyOf', 'contains', 'additionalProperties',
]);

function collectKeywords(node, found = new Set()) {
  if (Array.isArray(node)) {
    for (const item of node) collectKeywords(item, found);
    return found;
  }
  if (node === null || typeof node !== 'object') return found;
  for (const key of Object.keys(node)) found.add(key);
  for (const [key, value] of Object.entries(node)) {
    // "properties" is a name -> subschema map: recurse into the subschemas
    // without collecting the property names themselves as keywords.
    if (key === 'properties' && value !== null && typeof value === 'object' && !Array.isArray(value)) {
      for (const child of Object.values(value)) collectKeywords(child, found);
    } else if (SCHEMA_BEARING_KEYWORDS.has(key)) {
      collectKeywords(value, found);
    }
  }
  return found;
}

function deepEqual(a, b) {
  if (a === b) return true;
  if (Array.isArray(a) && Array.isArray(b)) {
    return a.length === b.length && a.every((item, index) => deepEqual(item, b[index]));
  }
  if (a !== null && b !== null && typeof a === 'object' && typeof b === 'object') {
    const keysA = Object.keys(a);
    const keysB = Object.keys(b);
    return keysA.length === keysB.length
      && keysA.every((key) => deepEqual(a[key], b[key]));
  }
  return false;
}

function matchesType(type, value) {
  switch (type) {
    case 'object': return value !== null && typeof value === 'object';
    case 'array': return Array.isArray(value);
    case 'string': return typeof value === 'string';
    case 'integer': return typeof value === 'number' && Number.isInteger(value);
    case 'number': return typeof value === 'number';
    case 'boolean': return typeof value === 'boolean';
    case 'null': return value === null;
    default: throw new Error(`validator does not support type "${type}"`);
  }
}

function validateAgainst(schemaNode, value, at, errors) {
  if (schemaNode === true) return;
  if (schemaNode === false) {
    errors.push(`${at}: schema is false`);
    return;
  }
  if (schemaNode === null || typeof schemaNode !== 'object') {
    throw new Error(`invalid schema node at ${at}`);
  }
  if (schemaNode.type !== undefined) {
    const types = Array.isArray(schemaNode.type) ? schemaNode.type : [schemaNode.type];
    if (!types.some((type) => matchesType(type, value))) {
      errors.push(`${at}: expected type ${types.join('|')}`);
      return;
    }
  }
  if (schemaNode.const !== undefined && !deepEqual(value, schemaNode.const)) {
    errors.push(`${at}: expected const ${JSON.stringify(schemaNode.const)}`);
  }
  if (schemaNode.enum !== undefined
    && !schemaNode.enum.some((option) => deepEqual(option, value))) {
    errors.push(`${at}: value is not one of ${JSON.stringify(schemaNode.enum)}`);
  }
  if (typeof value === 'string') {
    if (schemaNode.minLength !== undefined && value.length < schemaNode.minLength) {
      errors.push(`${at}: shorter than minLength ${schemaNode.minLength}`);
    }
    if (schemaNode.maxLength !== undefined && value.length > schemaNode.maxLength) {
      errors.push(`${at}: longer than maxLength ${schemaNode.maxLength}`);
    }
    if (schemaNode.pattern !== undefined && !new RegExp(schemaNode.pattern).test(value)) {
      errors.push(`${at}: does not match pattern ${schemaNode.pattern}`);
    }
    if (schemaNode.format !== undefined) {
      if (schemaNode.format === 'date-time') {
        if (!DATE_TIME.test(value)) errors.push(`${at}: not an RFC 3339 date-time`);
      } else {
        throw new Error(`validator does not support format "${schemaNode.format}"`);
      }
    }
  }
  if (typeof value === 'number') {
    if (schemaNode.minimum !== undefined && value < schemaNode.minimum) {
      errors.push(`${at}: below minimum ${schemaNode.minimum}`);
    }
    if (schemaNode.maximum !== undefined && value > schemaNode.maximum) {
      errors.push(`${at}: above maximum ${schemaNode.maximum}`);
    }
  }
  if (Array.isArray(value)) {
    if (schemaNode.minItems !== undefined && value.length < schemaNode.minItems) {
      errors.push(`${at}: fewer than minItems ${schemaNode.minItems}`);
    }
    if (schemaNode.maxItems !== undefined && value.length > schemaNode.maxItems) {
      errors.push(`${at}: more than maxItems ${schemaNode.maxItems}`);
    }
    if (schemaNode.uniqueItems === true) {
      for (let i = 0; i < value.length; i += 1) {
        for (let j = i + 1; j < value.length; j += 1) {
          if (deepEqual(value[i], value[j])) {
            errors.push(`${at}[${j}]: duplicates item ${i}`);
            i = value.length;
            break;
          }
        }
      }
    }
    if (schemaNode.items !== undefined) {
      value.forEach((item, index) => validateAgainst(schemaNode.items, item, `${at}[${index}]`, errors));
    }
    if (schemaNode.contains !== undefined
      && !value.some((item) => validateQuietly(schemaNode.contains, item))) {
      errors.push(`${at}: no item matches "contains"`);
    }
  }
  if (value !== null && typeof value === 'object' && !Array.isArray(value)) {
    for (const key of schemaNode.required ?? []) {
      if (!(key in value)) errors.push(`${at}: missing required property "${key}"`);
    }
    for (const [key, propertySchema] of Object.entries(schemaNode.properties ?? {})) {
      if (key in value) validateAgainst(propertySchema, value[key], `${at}.${key}`, errors);
    }
    if (schemaNode.additionalProperties !== undefined) {
      for (const key of Object.keys(value)) {
        if (Object.prototype.hasOwnProperty.call(schemaNode.properties ?? {}, key)) continue;
        if (schemaNode.additionalProperties === false) {
          errors.push(`${at}: additional property "${key}" is not allowed`);
        } else if (typeof schemaNode.additionalProperties === 'object') {
          validateAgainst(schemaNode.additionalProperties, value[key], `${at}.${key}`, errors);
        }
      }
    }
  }
  if (schemaNode.not !== undefined && validateQuietly(schemaNode.not, value)) {
    errors.push(`${at}: matches the "not" subschema`);
  }
  if (schemaNode.anyOf !== undefined
    && !schemaNode.anyOf.some((option) => validateQuietly(option, value))) {
    errors.push(`${at}: matches no "anyOf" option`);
  }
}

function validateQuietly(schemaNode, value) {
  const errors = [];
  validateAgainst(schemaNode, value, '$', errors);
  return errors.length === 0;
}

function schemaErrors(manifest) {
  const errors = [];
  validateAgainst(schema, manifest, '$', errors);
  return errors;
}

// ---------------------------------------------------------------------------
// Semantic checks JSON Schema cannot express. Mirrors the frozen interface
// and lib/release-integrity.js; codes are stable contract identifiers.
// ---------------------------------------------------------------------------
function semanticErrors(manifest) {
  const errors = new Set();
  // S1: files are unique by path and strictly ascending by path.
  // Uses the same JS string comparison as lib/release-integrity.js
  // (validateExpected: entry.path <= previous throws).
  let previous = '';
  for (const entry of manifest.files) {
    if (entry.path <= previous) errors.add('files-not-sorted-unique');
    previous = entry.path;
  }
  // S2: bundleDigest is the canonical digest of the declared file list.
  if (manifest.bundleDigest !== digestReleaseEntries(manifest.files)) {
    errors.add('bundle-digest-mismatch');
  }
  // S3: every snapshot path exists in files and every file is declared.
  const declared = new Set();
  for (const category of SNAPSHOT_CATEGORIES) {
    for (const filePath of manifest.snapshots[category]) {
      if (manifest.files.some((file) => file.path === filePath)) declared.add(filePath);
      else errors.add('snapshot-path-not-in-files');
    }
  }
  for (const file of manifest.files) {
    if (!declared.has(file.path)) errors.add('file-not-declared-in-snapshots');
  }
  // S4: an overall passed conclusion requires both sub-conclusions passed.
  const verification = manifest.releaseVerification;
  if (verification.result === 'passed'
    && (verification.singleAgentEvaluation !== 'passed'
      || verification.pipelineRegression !== 'passed')) {
    errors.add('release-verification-inconsistent');
  }
  // S5: a release cannot be its own previous release.
  if (manifest.previousReleaseId !== null
    && manifest.previousReleaseId === manifest.releaseId) {
    errors.add('previous-release-id-self');
  }
  return [...errors];
}

// ---------------------------------------------------------------------------
// Fixtures
// ---------------------------------------------------------------------------
const fixtureNames = fs.readdirSync(fixtureRoot).filter((name) => name.endsWith('.json')).sort();
const loadFixture = (name) => JSON.parse(fs.readFileSync(path.join(fixtureRoot, name), 'utf8'));

const validNames = fixtureNames.filter((name) => name.startsWith('valid-'));
const schemaInvalidNames = fixtureNames.filter((name) => name.startsWith('invalid-schema-'));
const semanticInvalidNames = fixtureNames.filter((name) => name.startsWith('invalid-semantic-'));

const EXPECTED_SEMANTIC_ERRORS = {
  'invalid-semantic-bundle-digest.json': 'bundle-digest-mismatch',
  'invalid-semantic-duplicate-path.json': 'files-not-sorted-unique',
  'invalid-semantic-previous-release-self.json': 'previous-release-id-self',
  'invalid-semantic-snapshot-coverage.json': 'snapshot-path-not-in-files',
  'invalid-semantic-verification-conflict.json': 'release-verification-inconsistent',
};

test('schema freezes the v1 manifest contract', () => {
  assert.equal(schema.$schema, 'https://json-schema.org/draft/2020-12/schema');
  assert.equal(schema.properties.schemaVersion.const, 1);
  assert.equal(schema.additionalProperties, false);
  assert.deepEqual(schema.required, [
    'schemaVersion', 'releaseId', 'createdAt', 'createdBy', 'previousReleaseId',
    'snapshots', 'files', 'bundleDigest', 'releaseVerification',
  ]);
  assert.deepEqual(
    Object.keys(schema.properties.snapshots.properties).sort(),
    [...SNAPSHOT_CATEGORIES].sort(),
  );
  assert.equal(schema.properties.snapshots.additionalProperties, false);
  assert.equal(schema.properties.bundleDigest.pattern, '^[a-f0-9]{64}$');
  assert.equal(schema.properties.files.items.properties.sha256.pattern, '^[a-f0-9]{64}$');
  // The embedded validator must support every keyword the schema uses.
  const unsupported = [...collectKeywords(schema)].filter((keyword) => !SUPPORTED_KEYWORDS.has(keyword));
  assert.deepEqual(unsupported, [], 'schema uses keywords the in-test validator cannot evaluate');
});

test('valid fixtures pass the schema and every semantic check', () => {
  assert.ok(validNames.length >= 2, 'at least two valid fixtures exist');
  for (const name of validNames) {
    const manifest = loadFixture(name);
    assert.deepEqual(schemaErrors(manifest), [], `${name} must be schema-valid`);
    assert.deepEqual(semanticErrors(manifest), [], `${name} must pass all semantic checks`);
    assert.equal(
      manifest.bundleDigest,
      digestReleaseEntries(manifest.files),
      `${name} bundleDigest must equal the lib-computed canonical digest`,
    );
  }
  const manifests = validNames.map(loadFixture);
  assert.ok(manifests.some((m) => m.previousReleaseId === null), 'first release (null previousReleaseId) is covered');
  assert.ok(manifests.some((m) => typeof m.previousReleaseId === 'string'), 'successor release (non-null previousReleaseId) is covered');
});

test('invalid-schema fixtures fail schema validation', () => {
  assert.ok(schemaInvalidNames.length >= 1, 'at least one invalid-schema fixture exists');
  for (const name of schemaInvalidNames) {
    const manifest = loadFixture(name);
    assert.notDeepEqual(schemaErrors(manifest), [], `${name} must fail schema validation`);
  }
});

test('invalid-semantic fixtures pass the schema but fail the expected semantic rule', () => {
  assert.deepEqual(semanticInvalidNames, Object.keys(EXPECTED_SEMANTIC_ERRORS).sort());
  for (const name of semanticInvalidNames) {
    const manifest = loadFixture(name);
    assert.deepEqual(schemaErrors(manifest), [], `${name} must be schema-valid (the rule is semantic)`);
    const errors = semanticErrors(manifest);
    assert.ok(
      errors.includes(EXPECTED_SEMANTIC_ERRORS[name]),
      `${name} must fail "${EXPECTED_SEMANTIC_ERRORS[name]}", got ${JSON.stringify(errors)}`,
    );
  }
});

test('schema rejects structural violations of the frozen shape', () => {
  const base = loadFixture('valid-first-release.json');
  const rejects = (mutate) => {
    const manifest = structuredClone(base);
    mutate(manifest);
    assert.notDeepEqual(schemaErrors(manifest), []);
  };
  rejects((m) => { m.schemaVersion = 2; });
  rejects((m) => { delete m.releaseId; });
  rejects((m) => { delete m.createdBy; });
  rejects((m) => { m.previousReleaseId = 0; });
  rejects((m) => { m.previousReleaseId = ''; });
  rejects((m) => { m.createdAt = '2026-09-22 08:00:00'; });
  rejects((m) => { m.extra = true; });
  rejects((m) => { m.releaseId = ''; });
  rejects((m) => { delete m.snapshots.contracts; });
  rejects((m) => { m.snapshots.profiles = []; });
  rejects((m) => { m.snapshots.gates = ['gates/x']; });
  rejects((m) => { m.snapshots.profiles = ['orchestration/ptc_stage_registry.json']; });
  rejects((m) => { m.files = []; });
  rejects((m) => { m.files.push({ ...m.files[0] }); });
  rejects((m) => { m.files.push({ path: 'release-manifest.json', size: 1, sha256: '0'.repeat(64) }); });
  rejects((m) => { m.files[0].extra = 1; });
  rejects((m) => { delete m.files[0].sha256; });
  rejects((m) => { m.files[0].path = '/absolute/path.json'; });
  rejects((m) => { m.files[0].path = 'a\\b.json'; });
  rejects((m) => { m.files[0].path = 'a/../b.json'; });
  rejects((m) => { m.files[0].size = -1; });
  rejects((m) => { m.files[0].size = 9007199254740992; });
  rejects((m) => { m.files[0].size = 1.5; });
  rejects((m) => { m.files[0].sha256 = m.files[0].sha256.toUpperCase(); });
  rejects((m) => { m.files[0].sha256 = m.files[0].sha256.slice(0, 63); });
  rejects((m) => { m.bundleDigest = m.bundleDigest.toUpperCase(); });
  rejects((m) => { delete m.bundleDigest; });
  rejects((m) => { delete m.releaseVerification; });
  rejects((m) => { m.releaseVerification.result = 'ok'; });
  rejects((m) => { delete m.releaseVerification.pipelineRegression; });
});

test('the files ordering rule mirrors lib/release-integrity.js exactly', () => {
  const manifest = loadFixture('valid-first-release.json');
  const reversed = { ...manifest, files: manifest.files.slice().reverse() };
  assert.ok(semanticErrors(reversed).includes('files-not-sorted-unique'));
  const missingDirectory = path.join(fixtureRoot, 'no-such-directory');
  // lib rejects the reversed list before touching the filesystem.
  assert.throws(() => verifyReleaseDirectory(missingDirectory, reversed), /unique and sorted/);
  // lib accepts the valid fixture entries: it fails later on the missing
  // directory (ENOENT), not on entry validation.
  assert.throws(
    () => verifyReleaseDirectory(missingDirectory, manifest),
    (error) => error?.code === 'ENOENT',
  );
});
