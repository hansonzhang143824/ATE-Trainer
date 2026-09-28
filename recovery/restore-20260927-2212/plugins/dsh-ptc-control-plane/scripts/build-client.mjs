import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const pluginRoot = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const sources = ['state.js', 'native-sessions.js', 'draft-editor.js', 'issue-editor.js',
  'workflow-status.js', 'panel.js', 'trainer-state.js', 'trainer-native.js', 'trainer-assets.js', 'trainer-workbench.js', 'index.js'].map((name) =>
  fs.readFileSync(path.join(pluginRoot, 'client', name), 'utf8').replace(/^\uFEFF/, ''));

function transform(source) {
  return source
    .split(/\r?\n/)
    .filter((line) => !line.startsWith('import '))
    .join('\n')
    .replace(/^export default .*;\s*$/gm, '')
    .replace(/^export (async function|function|const) /gm, '$1 ')
    .trim();
}

const body = sources.map(transform).join('\n\n');
const indented = body.split('\n').map((line) => line.trimEnd() ? `\t\t${line.trimEnd()}` : '').join('\n');
const output = `window.__ModuleLoader__.load({
\tid: "dsh-ptc-control-plane",
\tfactory: (require) => {
\t\tvar module = { exports: {} };
\t\tvar exports = module.exports;
\t\tObject.defineProperty(exports, Symbol.toStringTag, { value: "Module" });
\t\tconst { createElement, useEffect, useState, useSyncExternalStore } = require("react");
${indented}
\t\texports.apply = apply;
\t\texports.inject = inject;
\t\treturn module.exports;
\t}
});
`;

const target = path.join(pluginRoot, 'lib', 'client.js');
fs.mkdirSync(path.dirname(target), { recursive: true });
fs.writeFileSync(target, output, 'utf8');
console.log(`built ${path.relative(process.cwd(), target)} (${Buffer.byteLength(output)} bytes)`);
