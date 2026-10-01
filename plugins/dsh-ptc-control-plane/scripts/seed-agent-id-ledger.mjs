#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { randomUUID } from 'node:crypto';
import {
  AGENT_ID_LEDGER_PATH,
  applyChanges,
  parseAgentIdLedger,
  readAssets,
  readProject,
} from '../lib/trainer-project.js';

const rootArg = process.argv.indexOf('--root');
const root = path.resolve(rootArg >= 0 ? process.argv[rootArg + 1] : process.cwd());
const projectId = 'agent-trainer';
const idPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const sourceRoots = [
  'Training_Materials/framework/projects/agent-trainer/revisions',
  'Training_Materials/framework/projects/agent-trainer/versions',
  'publish/versions',
  'publish/workflow-templates/versions',
];

function filesUnder(relativeRoot) {
  const directory = path.join(root, relativeRoot);
  if (!fs.existsSync(directory)) return [];
  const output = [];
  const visit = current => {
    for (const entry of fs.readdirSync(current, { withFileTypes: true })) {
      const target = path.join(current, entry.name);
      if (entry.isDirectory()) visit(target);
      else if (entry.isFile() && entry.name.endsWith('.json')) output.push(target);
    }
  };
  visit(directory);
  return output.sort();
}

function addId(ids, id, source) {
  if (typeof id !== 'string' || !idPattern.test(id)) return;
  ids.set(id, [...(ids.get(id) ?? []), source]);
}

const ids = new Map();
const report = [];
for (const relativeRoot of sourceRoots) {
  let files = [];
  try { files = filesUnder(relativeRoot); } catch (error) { report.push({ source: relativeRoot, parseFailures: [`<scan>: ${error.message}`] }); }
  const parseFailures = [];
  let agentFields = 0;
  let workflowFields = 0;
  for (const file of files) {
    let value;
    try { value = JSON.parse(fs.readFileSync(file, 'utf8')); }
    catch (error) { parseFailures.push(`${path.relative(root, file)}: ${error.message}`); continue; }
    const relative = path.relative(root, file).replaceAll(path.sep, '/');
    if (/agents\/[^/]+\/agent\.json$/.test(relative)) {
      if (typeof value.agentId === 'string') { agentFields += 1; addId(ids, value.agentId, `${relative}:agentId`); }
    }
    if (/workflows\/[^/]+\.json$/.test(relative)) {
      for (const [index, step] of (Array.isArray(value.steps) ? value.steps : []).entries()) {
        if (typeof step?.agentId === 'string') { workflowFields += 1; addId(ids, step.agentId, `${relative}:steps[${index}].agentId`); }
      }
    }
  }
  report.push({ source: relativeRoot, files: files.length, agentFields, workflowFields, parseFailures });
}

let project;
try { project = readProject(root, { projectId }); }
catch (error) { console.error(`无法读取 ${projectId} registry：${error.message}`); process.exitCode = 1; process.exit(); }
for (const agent of project.agents ?? []) addId(ids, agent.agentId, `current registry: ${agent.agentId}`);

const assets = readAssets(root, { projectId, revisionId: project.revisionId });
let existing = [];
try { existing = parseAgentIdLedger(assets.files[AGENT_ID_LEDGER_PATH]).allocated; }
catch { /* Missing or damaged ledgers are rebuilt from the independent scan. */ }
const allocated = [...new Set([...existing, ...ids.keys()])].sort();
const content = `${JSON.stringify({ schemaVersion: 1, allocated }, null, 2)}\n`;
const result = applyChanges(root, {
  projectId,
  requestId: `seed-${randomUUID().replaceAll('-', '')}`,
  baseRevision: project.revisionId,
  reason: '初始化 Agent ID 台账',
  changes: [{ path: AGENT_ID_LEDGER_PATH, content }],
});
console.log(JSON.stringify({ root, projectId, revisionId: result.revisionId, changeSetId: result.changeSetId, allocated, sources: report }, null, 2));
