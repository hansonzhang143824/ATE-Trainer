/**
 * P0-A: does the REAL DSH preset discovery see the new expert presets?
 *
 * This imports the installed `dsh-agent-presets` implementation — the same
 * code the roster/picker reads — instead of reimplementing discovery. A green
 * run proves the roster rows exist and whether each composition loads; it does
 * NOT prove the browser selector renders them (that is the user's one-second
 * visual check, or a UI test).
 *
 * Run: node .dsh-dev/verify-preset-discovery.mjs
 */
import os from 'node:os';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const DSH_PRESETS = path.join(
  process.env.APPDATA ?? path.join(os.homedir(), 'AppData', 'Roaming'),
  'npm', 'node_modules', '@deepseek-ai', 'dsh', 'node_modules',
  '@deepseek-ai', 'dsh-agent-presets', 'lib', 'index.js',
);

const { discoverPresets } = await import(pathToFileURL(DSH_PRESETS).href);
const userRoot = path.join(os.homedir(), '.dsh', '.agent-presets');
const rows = await discoverPresets([{ path: userRoot, trust: 'user' }]);

console.log(`preset root scanned: ${userRoot}`);
console.log(`rows: ${rows.length}`);
for (const row of rows) {
  console.log(JSON.stringify({
    id: row.id,
    displayName: row.name ?? null,
    description: row.description ?? null,
    broken: row.broken ?? null,
  }));
}

// P0-C adds the schematic master; until then it is not expected to exist, and a
// missing row is not a failure. Pass `--include-schematic` once P0-C starts.
const wanted = process.argv.includes('--include-schematic')
  ? ['ptc-dft-expert', 'ptc-schematic-expert']
  : ['ptc-dft-expert'];
const missing = wanted.filter((id) => !rows.some((row) => row.id === id));
const broken = rows.filter((row) => wanted.includes(row.id) && row.broken !== undefined);
console.log(`missing: ${missing.length === 0 ? 'none' : missing.join(', ')}`);
console.log(`broken: ${broken.length === 0 ? 'none' : broken.map((row) => `${row.id}: ${row.broken}`).join('; ')}`);
process.exit(missing.length === 0 && broken.length === 0 ? 0 : 1);
