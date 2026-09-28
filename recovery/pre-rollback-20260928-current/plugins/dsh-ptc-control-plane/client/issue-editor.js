import { createElement, useState } from 'react';

const issueElement = createElement;

function issueOwner(run) {
  if (run.target?.kind === 'profile' && run.target.profileId === 'ptc-dft-expert') {
    return { profileId: 'ptc-dft-expert' };
  }
  if (run.purpose === 'schematic-statistic-only') {
    return { profileId: 'ptc-schematic-expert', sourceRole: 'schematic-expert' };
  }
  return null;
}

function isIssueCandidate(run) {
  if (run.mode !== 'training' || !['blocked', 'completed'].includes(run.status)
      || run.purpose === 'framework-rehearsal') return false;
  return !!issueOwner(run) || (run.purpose === 'business-training' && run.target?.kind === 'pipeline');
}

async function post(resource, action, input) {
  const response = await fetch(`/api/ptc-control/${resource}/${action}`, {
    method: 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(input),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
  return body;
}

/** Local training proposals only; no draft write, case promotion or release. */
export function TrainingIssueEditor({ runs }) {
  const eligible = runs.filter(isIssueCandidate);
  const [runId, setRunId] = useState('');
  const [sourceRole, setSourceRole] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  const [issues, setIssues] = useState([]);
  const [caseIssueId, setCaseIssueId] = useState('');
  const [expectedBehavior, setExpectedBehavior] = useState('');
  const [proposals, setProposals] = useState([]);
  const selected = eligible.find(run => run.runId === runId) ?? eligible[0];
  const pipelineOwners = selected?.purpose === 'business-training' && selected.target?.kind === 'pipeline'
    ? (Array.isArray(selected.issueOwners) ? selected.issueOwners : []).filter(entry =>
      entry && typeof entry.sourceRole === 'string' && typeof entry.profileId === 'string') : [];
  const owner = selected && (issueOwner(selected)
    ?? (pipelineOwners.find(entry => entry.sourceRole === sourceRole) ?? pipelineOwners[0] ?? null));
  // Only the backend can verify run-local frozen materials and participating roles.
  // Never infer pipeline ownership from the current stage registry or profile list.
  const needsPipelineOwner = selected?.purpose === 'business-training'
    && selected.target?.kind === 'pipeline' && !owner;
  const caseIssues = issues.filter(issue => issue?.disposition === 'proposal-only'
    && eligible.some(run => run.runId === issue.runId));
  const selectedIssue = caseIssues.find(issue => issue.issueId === caseIssueId) ?? caseIssues[0];
  const refresh = async () => {
    setBusy(true); setNotice('');
    try {
      const [issueList, caseList] = await Promise.all([
        post('training-issues', 'list', {}), post('training-cases', 'list', {}),
      ]);
      setIssues(issueList.issues);
      setProposals(caseList.proposals);
    }
    catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  const create = async () => {
    if (!selected || !owner || !title.trim() || !description.trim()) return;
    setBusy(true); setNotice('');
    try {
      const result = await post('training-issues', 'create', { runId: selected.runId, ...owner,
        title: title.trim(), description: description.trim() });
      setTitle(''); setDescription('');
      setIssues(current => [result.issue, ...current]);
      setNotice(`已登记训练问题 ${result.issue.issueId}；仅作提案，不会修改草稿、门禁或发布版本。`);
    } catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  const createCase = async () => {
    if (!selectedIssue || !expectedBehavior.trim()) return;
    setBusy(true); setNotice('');
    try {
      const result = await post('training-cases', 'create', {
        issueId: selectedIssue.issueId, expectedBehavior: expectedBehavior.trim(),
      });
      setExpectedBehavior('');
      setProposals(current => [result.proposal, ...current]);
      setNotice(`已登记回归案例候选 ${result.proposal.caseId}；尚未采纳，不会修改回归集或发布版本。`);
    } catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  return issueElement('details', { className: 'ptc-cp-training-issues' },
    issueElement('summary', null, '训练问题与提案'),
    issueElement('p', null, '问题绑定训练运行的 SHA-256；登记不会自动更改专家、编排或回归案例。'),
    issueElement('label', null, '关联运行 ', issueElement('select', { value: selected?.runId ?? '', disabled: busy || !eligible.length,
      onChange: event => { setRunId(event.target.value); setSourceRole(''); }, 'aria-label': '关联训练运行' },
      ...eligible.map(run => issueElement('option', { key: run.runId, value: run.runId }, `${run.runId} · ${run.status}`)))),
    pipelineOwners.length ? issueElement('label', null, '问题归属专家 ', issueElement('select', {
      value: owner?.sourceRole ?? '', disabled: busy,
      onChange: event => setSourceRole(event.target.value), 'aria-label': '问题归属专家' },
    ...pipelineOwners.map(entry => issueElement('option', { key: entry.sourceRole, value: entry.sourceRole },
      `${entry.sourceRole} · ${entry.profileId}`)))) : null,
    needsPipelineOwner ? issueElement('p', { role: 'status', 'data-testid': 'ptc-cp-issue-owner-required' },
      '此真实流程训练运行缺少经该运行冻结材料验证的专家角色与 profile 映射；当前无法安全登记，请勿按现行阶段配置猜测归属。') : null,
    issueElement('input', { type: 'text', value: title, disabled: busy || !owner, maxLength: 120,
      placeholder: '问题标题', 'aria-label': '训练问题标题', onChange: event => setTitle(event.target.value) }),
    issueElement('textarea', { value: description, disabled: busy || !owner, maxLength: 4000,
      rows: 5, placeholder: '现象、期望及复现步骤', 'aria-label': '训练问题描述',
      onChange: event => setDescription(event.target.value) }),
    issueElement('button', { type: 'button', disabled: busy || !owner || !title.trim() || !description.trim(),
      onClick: () => void create() }, '登记训练问题'),
    issueElement('button', { type: 'button', disabled: busy, onClick: () => void refresh() }, '刷新问题与案例候选'),
    issueElement('p', null, '回归案例仅从已核验的训练问题生成候选；需要具体运行证据，登记后不会自动采纳。'),
    issueElement('label', null, '关联训练问题 ', issueElement('select', {
      value: selectedIssue?.issueId ?? '', disabled: busy || !caseIssues.length,
      onChange: event => setCaseIssueId(event.target.value), 'aria-label': '关联训练问题' },
    ...caseIssues.map(issue => issueElement('option', { key: issue.issueId, value: issue.issueId },
      `${issue.issueId} · ${issue.title}`)))),
    issueElement('textarea', { value: expectedBehavior, disabled: busy || !selectedIssue, maxLength: 4000,
      rows: 4, placeholder: '写明期望行为和可判定的通过条件', 'aria-label': '回归案例预期行为',
      onChange: event => setExpectedBehavior(event.target.value) }),
    issueElement('button', { type: 'button', disabled: busy || !selectedIssue || !expectedBehavior.trim(),
      onClick: () => void createCase() }, '登记回归案例候选'),
    notice ? issueElement('p', { role: 'status' }, notice) : null,
    ...issues.slice(0, 20).map(issue => issueElement('div', { key: issue.issueId },
      `${issue.issueId} · ${issue.profileId} · ${issue.title} · 仅提案`)),
    ...proposals.slice(0, 20).map(proposal => issueElement('div', { key: proposal.caseId },
      `${proposal.caseId} · ${proposal.issueId} · 候选未采纳`)));
}
