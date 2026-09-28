import assert from 'node:assert/strict';
import fs from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

const source = fs.readFileSync(new URL('../client/issue-editor.js', import.meta.url), 'utf8')
  .replace(/^import .*;\s*/gm, '').replace('export function TrainingIssueEditor', 'function TrainingIssueEditor');

function harness(runs, responseFor = () => ({ issue: { issueId: 'issue-test' }, issues: [] })) {
  const slots = [];
  const requests = [];
  let cursor = 0;
  const context = {
    createElement: (type, props, ...children) => ({ type, props: props ?? {}, children }),
    useState: initial => {
      const index = cursor++;
      if (!(index in slots)) slots[index] = initial;
      return [slots[index], value => { slots[index] = typeof value === 'function' ? value(slots[index]) : value; }];
    },
    fetch: async (url, options) => {
      requests.push({ url, body: JSON.parse(options.body) });
      return { ok: true, json: async () => responseFor(url, JSON.parse(options.body)) };
    },
  };
  vm.createContext(context);
  vm.runInContext(`${source}\nthis.renderIssue = TrainingIssueEditor;`, context);
  const render = () => { cursor = 0; return context.renderIssue({ runs }); };
  return { render, requests };
}

function nodes(tree) {
  const found = [];
  const visit = item => {
    if (Array.isArray(item)) return item.forEach(visit);
    if (!item || typeof item !== 'object') return;
    found.push(item);
    item.children?.forEach(visit);
  };
  visit(tree);
  return found;
}

const run = (runId, target, purpose = 'business-training') => ({
  runId, mode: 'training', status: 'blocked', target, purpose,
});

test('DFT and statistic-only issue paths keep their fixed, verified owners', async () => {
  const runs = [run('dft', { kind: 'profile', profileId: 'ptc-dft-expert' }),
    run('statistic', { kind: 'pipeline' }, 'schematic-statistic-only')];
  const h = harness(runs);
  let tree = nodes(h.render());
  assert.deepEqual(tree.find(node => node.props['aria-label'] === '关联训练运行').children.map(item => item.props.value),
    ['dft', 'statistic']);
  tree.find(node => node.props['aria-label'] === '训练问题标题').props.onChange({ target: { value: 'DFT issue' } });
  tree.find(node => node.props['aria-label'] === '训练问题描述').props.onChange({ target: { value: 'DFT detail' } });
  tree = nodes(h.render());
  tree.find(node => node.type === 'button' && node.children[0] === '登记训练问题').props.onClick();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(h.requests[0].body, { runId: 'dft', profileId: 'ptc-dft-expert',
    title: 'DFT issue', description: 'DFT detail' });
  tree = nodes(h.render());
  tree.find(node => node.props['aria-label'] === '关联训练运行').props.onChange({ target: { value: 'statistic' } });
  tree.find(node => node.props['aria-label'] === '训练问题标题').props.onChange({ target: { value: 'Statistic issue' } });
  tree.find(node => node.props['aria-label'] === '训练问题描述').props.onChange({ target: { value: 'Statistic detail' } });
  tree = nodes(h.render());
  tree.find(node => node.type === 'button' && node.children[0] === '登记训练问题').props.onClick();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(h.requests[1].body, { runId: 'statistic', profileId: 'ptc-schematic-expert',
    sourceRole: 'schematic-expert', title: 'Statistic issue', description: 'Statistic detail' });
});

test('real pipeline requires run-local owner mapping and never registers framework rehearsal', async () => {
  const pipeline = run('pipeline', { kind: 'pipeline' });
  const rehearsal = run('rehearsal', { kind: 'pipeline' }, 'framework-rehearsal');
  const h = harness([pipeline, rehearsal]);
  let tree = nodes(h.render());
  assert.deepEqual(tree.find(node => node.props['aria-label'] === '关联训练运行').children.map(item => item.props.value),
    ['pipeline']);
  assert.ok(tree.some(node => node.props['data-testid'] === 'ptc-cp-issue-owner-required'));
  assert.equal(tree.find(node => node.type === 'button' && node.children[0] === '登记训练问题').props.disabled, true);
  assert.deepEqual(h.requests, []);

  pipeline.issueOwners = [{ sourceRole: 'dft-expert', profileId: 'ptc-dft-expert' },
    { sourceRole: 'schematic-expert', profileId: 'ptc-schematic-expert' }];
  tree = nodes(h.render());
  assert.equal(tree.some(node => node.props['data-testid'] === 'ptc-cp-issue-owner-required'), false);
  tree.find(node => node.props['aria-label'] === '问题归属专家').props.onChange({ target: { value: 'schematic-expert' } });
  tree.find(node => node.props['aria-label'] === '训练问题标题').props.onChange({ target: { value: 'Pipeline issue' } });
  tree.find(node => node.props['aria-label'] === '训练问题描述').props.onChange({ target: { value: 'Pipeline detail' } });
  tree = nodes(h.render());
  tree.find(node => node.type === 'button' && node.children[0] === '登记训练问题').props.onClick();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(h.requests[0].body, { runId: 'pipeline', sourceRole: 'schematic-expert',
    profileId: 'ptc-schematic-expert', title: 'Pipeline issue', description: 'Pipeline detail' });
});

test('case proposal submits only verified listed issue and expected behavior, never framework issue', async () => {
  const eligibleRun = run('dft', { kind: 'profile', profileId: 'ptc-dft-expert' });
  const framework = run('framework', { kind: 'pipeline' }, 'framework-rehearsal');
  const h = harness([eligibleRun, framework], url => {
    if (url.endsWith('/training-issues/list')) return { issues: [
      { issueId: 'issue-framework', runId: 'framework', title: 'nonbusiness', disposition: 'proposal-only' },
      { issueId: 'issue-dft', runId: 'dft', title: 'DFT mismatch', disposition: 'proposal-only' },
    ] };
    if (url.endsWith('/training-cases/list')) return { proposals: [] };
    if (url.endsWith('/training-cases/create')) return { proposal: {
      caseId: 'case-issue-dft', issueId: 'issue-dft', disposition: 'proposal-only',
    } };
    return { issue: { issueId: 'issue-dft' } };
  });
  let tree = nodes(h.render());
  assert.equal(tree.find(node => node.type === 'button' && node.children[0] === '登记回归案例候选').props.disabled, true);
  tree.find(node => node.type === 'button' && node.children[0] === '刷新问题与案例候选').props.onClick();
  await new Promise(resolve => setImmediate(resolve));
  tree = nodes(h.render());
  assert.deepEqual(tree.find(node => node.props['aria-label'] === '关联训练问题').children.map(item => item.props.value),
    ['issue-dft']);
  tree.find(node => node.props['aria-label'] === '回归案例预期行为').props.onChange({ target: { value: '  Gate passes  ' } });
  tree = nodes(h.render());
  tree.find(node => node.type === 'button' && node.children[0] === '登记回归案例候选').props.onClick();
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(h.requests.at(-1), { url: '/api/ptc-control/training-cases/create',
    body: { issueId: 'issue-dft', expectedBehavior: 'Gate passes' } });
  assert.equal(nodes(h.render()).some(node => node.children?.[0]?.includes?.('候选未采纳')), true);
});
