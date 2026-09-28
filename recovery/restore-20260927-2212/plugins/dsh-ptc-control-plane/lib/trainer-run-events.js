import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { assertSafeRunPath } from './run-context.js';

export const frameworkSha = value => crypto.createHash('sha256').update(value).digest('hex');
export function frameworkId(value) {
  if (typeof value !== 'string' || !/^[a-zA-Z0-9][a-zA-Z0-9_-]{0,127}$/.test(value)
      || /^(con|prn|aux|nul|com[1-9]|lpt[1-9])$/i.test(value)) throw new Error('invalid framework identity');
  return value;
}
export function createRunStore(workspaceRoot) {
  const root = path.resolve(workspaceRoot);
  const safe = file => assertSafeRunPath(root, file);
  const directory = (runId, mode) => safe(path.join(root, mode === 'published' ? 'publish' : 'Training_Materials', 'runs', frameworkId(runId)));
  const locate = runId => {
    const matches = ['training', 'published'].map(mode => directory(runId, mode))
      .filter(dir => fs.existsSync(safe(path.join(dir, 'framework-run.json'))));
    if (matches.length !== 1) throw new Error(matches.length ? 'ambiguous framework run' : 'framework run not found');
    return matches[0];
  };
  function write(dir, name, value, exclusive = false) {
    const file = safe(path.join(dir, name));
    const bytes = Buffer.from(`${JSON.stringify(value, null, 2)}\n`);
    if (exclusive) fs.writeFileSync(file, bytes, { flag: 'wx' });
    else {
      const temporary = safe(`${file}.${crypto.randomUUID()}.tmp`);
      fs.writeFileSync(temporary, bytes, { flag: 'wx' });
      try { fs.renameSync(temporary, file); } finally { if (fs.existsSync(temporary)) fs.unlinkSync(temporary); }
    }
    return { path: path.relative(root, file).split(path.sep).join('/'), sha256: frameworkSha(fs.readFileSync(file)) };
  }
  function read(dir) {
    const value = JSON.parse(fs.readFileSync(safe(path.join(dir, 'framework-run.json')), 'utf8'));
    if (value.kind !== 'framework-run' || value.businessGatePassed !== false) throw new Error('invalid framework run');
    return value;
  }
  function events(dir, cursor = 0, limit = 200) {
    if (!Number.isSafeInteger(Number(cursor)) || Number(cursor) < 0) throw new Error('invalid event cursor');
    const file = safe(path.join(dir, 'framework-events.jsonl'));
    const all = fs.existsSync(file) ? fs.readFileSync(file, 'utf8').split('\n').filter(Boolean).map(line => JSON.parse(line)) : [];
    const items = all.filter(event => event.seq > Number(cursor)).slice(0, Math.min(1000, limit));
    return { events: items, cursor: items.at(-1)?.seq ?? Number(cursor), hasMore: all.at(-1)?.seq > (items.at(-1)?.seq ?? Number(cursor)) };
  }
  return { root, safe, directory, locate, write, read, events,
    create(run) {
      for (const mode of ['training', 'published']) if (fs.existsSync(directory(run.runId, mode))) throw new Error('run ID already exists');
      const dir = directory(run.runId, run.mode);
      fs.mkdirSync(path.dirname(dir), { recursive: true });
      fs.mkdirSync(dir);
      write(dir, 'framework-run.json', run, true);
      return dir;
    },
    append(dir, event) {
      const file = safe(path.join(dir, 'framework-events.jsonl'));
      const descriptor = fs.openSync(file, 'a');
      try { fs.writeSync(descriptor, `${JSON.stringify(event)}\n`); fs.fsyncSync(descriptor); }
      finally { fs.closeSync(descriptor); }
    },
    list() {
      const all = [];
      for (const mode of ['training', 'published']) {
        const dir = safe(path.join(root, mode === 'published' ? 'publish' : 'Training_Materials', 'runs'));
        if (!fs.existsSync(dir)) continue;
        for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
          if (!entry.isDirectory()) continue;
          const child = safe(path.join(dir, entry.name));
          if (fs.existsSync(safe(path.join(child, 'framework-run.json')))) all.push(read(child));
        }
      }
      return all;
    },
  };
}
