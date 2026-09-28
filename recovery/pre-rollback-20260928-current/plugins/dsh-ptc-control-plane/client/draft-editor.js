import { createElement, useEffect, useState } from 'react';
const h = createElement;

async function draftRequest(action, input) {
  const response = await fetch(`/api/ptc-control/training-drafts/${action}`, {
    method: 'POST', credentials: 'same-origin',
    headers: { 'Content-Type': 'application/json', Accept: 'application/json' },
    body: JSON.stringify(input),
  });
  const body = await response.json().catch(() => ({}));
  if (!response.ok) throw new Error(body.detail ?? body.error ?? `HTTP ${response.status}`);
  return body;
}

/** Only mounted in the training view; immutable run snapshots never change. */
export function DraftEditor({ profileId }) {
  const [file, setFile] = useState('instructions.md');
  const [loaded, setLoaded] = useState(null);
  const [content, setContent] = useState('');
  const [busy, setBusy] = useState(false);
  const [notice, setNotice] = useState('');
  useEffect(() => { setLoaded(null); setContent(''); setNotice(''); }, [profileId, file]);
  const read = async () => {
    setBusy(true); setNotice('');
    try {
      const value = await draftRequest('read', { profileId, file });
      setLoaded(value); setContent(value.content);
    } catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  const save = async () => {
    if (!loaded || loaded.profileId !== profileId || loaded.file !== file) return;
    setBusy(true); setNotice('');
    try {
      const result = await draftRequest('save', { mode: 'training', profileId, file, content, expectedSha256: loaded.sha256 });
      setLoaded({ ...loaded, content, sha256: result.sha256 });
      setNotice(result.changed ? `草稿已保存；历史记录 ${result.historyId}。需新建训练复测，已有运行和发布快照不变。` : '内容未变化，无需保存。');
    } catch (error) { setNotice(String(error.message ?? error)); }
    finally { setBusy(false); }
  };
  return h('details', { className: 'ptc-cp-draft' },
    h('summary', null, '训练草稿编辑'),
    h('p', null, '这里只修改候选专家。保存不会修改已启动训练，也不会自动发布。'),
    h('select', { 'aria-label': '草稿文件', value: file, disabled: busy, onChange: event => setFile(event.target.value) },
      ...['instructions.md', 'profile.yaml', 'output-contract.schema.json'].map(name => h('option', { key: name, value: name }, name))),
    h('button', { type: 'button', disabled: busy || !profileId, onClick: () => void read() }, '读取草稿'),
    loaded ? h('div', null,
      h('div', null, `SHA-256：${loaded.sha256}`),
      h('textarea', { 'aria-label': '专家草稿内容', value: content, disabled: busy, rows: 18,
        style: { width: '100%', fontFamily: 'monospace' }, onChange: event => setContent(event.target.value) }),
      h('button', { type: 'button', disabled: busy || content === loaded.content, onClick: () => void save() }, '保存训练草稿')) : null,
    notice ? h('p', { role: 'status' }, notice) : null);
}
