import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { createTrainerService } from '../lib/trainer-service.js';

function fixture(t) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'trainer-service-'));
  t.after(() => fs.rmSync(root, { recursive: true, force: true }));
  let starts = 0, edits = 0;
  const runs = new Map();
  const project = { projectId: 'synthetic-lab', revisionId: 'rev-1', agents: [{agentId:'producer'},{agentId:'consumer'}], workflows:[{workflowId:'pair'}] };
  const bundle = { ...project, targetKind:'agent',targetId:'producer',bundleSha256:'a'.repeat(64) };
  const repositories = {
    ensureTrainerProject: () => project, readProject: () => project, resolveBundle: () => bundle,
    applyChanges: (_root,args) => { edits++; return {revisionId:'rev-2',changes:args.changes}; },
    readAssets: () => ({revisionId:'rev-1',files:{'agents/producer/instructions.md':'synthetic'}}),
    freezeTarget: (_root,args) => ({bundleSha256:args.bundle.bundleSha256,frozenVersionId:'frozen-1'}),
  };
  const runner = { startRun: args => { starts++; const run={...args,...bundle,status:'running',businessGatePassed:false}; runs.set(args.runId,run); return run; },
    readRun: ({runId})=>runs.get(runId), listRuns:()=>({runs:[...runs.values()],nextCursor:null}),
    readEvents:()=>({events:[]}),controlRun:()=>({status:'stopping',childTerminationConfirmed:false}) };
  const options={workspaceRoot:root,runner,repositories,modelResolver:()=>({provider:'test',model:'test'}),sessionVerifier:async (sid,preset)=>sid.startsWith(preset)};
  const service=createTrainerService(options);
  const page=(op,args={})=>service.invoke(op,{projectId:'synthetic-lab',...args},{kind:'page'});
  async function bind(preset='agent-trainer',mode='training') {
    const sessionId=`${preset}-session`;
    const response=await page('bind-session',{sessionId,presetId:preset,mode,targetKind:'agent',targetId:'producer'});
    assert.equal(response.ok,true,JSON.stringify(response));
    return {kind:'tool',sessionId,presetId:preset};
  }
  return {root,service,options,page,bind,runs,counts:()=>({starts,edits})};
}

test('duplicate simultaneous run requests and service restart never dispatch twice',async t=>{
  const f=fixture(t),args={requestId:'same',targetKind:'agent',targetId:'producer',input:{value:7}};
  const [a,b]=await Promise.all([f.page('run',args),f.page('run',args)]);
  assert.equal(a.ok,true); assert.deepEqual(a,b); assert.equal(f.counts().starts,1);
  const restored=createTrainerService(f.options);
  assert.deepEqual(await restored.invoke('run',{projectId:'synthetic-lab',...args},{kind:'page'}),a);
  assert.equal(f.counts().starts,1);
  const conflict=await f.page('run',{...args,input:{value:8}});
  assert.equal(conflict.error.code,'request_conflict');
});
test('diagnostic reads preserve candidate and do not dispatch',async t=>{
  const f=fixture(t),p=await f.bind();
  for(const op of ['context','assets','runs']) assert.equal((await f.service.invoke(op,{},p)).ok,true);
  assert.deepEqual(f.counts(),{starts:0,edits:0});
});
test('history listing remains available after a tool run binds its result',async t=>{
  const f=fixture(t),p=await f.bind();
  const started=await f.service.invoke('run',{requestId:'first-run'},p);assert.equal(started.ok,true);
  const listed=await f.service.invoke('runs',{limit:10},p);assert.equal(listed.ok,true);assert.equal(listed.value.runs.length,1);
  assert.equal(listed.value.runs[0].runId,started.value.runId);
  const selected=await f.service.invoke('context',{},p);assert.equal(selected.value.selectedRun.runId,started.value.runId);
});
test('tool cannot forge training mode, project, or explicit release action',async t=>{
  const f=fixture(t),p=await f.bind('framework-observer','engineering');
  for(const [op,args,code] of [
    ['apply-changes',{requestId:'edit',mode:'training'},'mode_forbidden'],
    ['run',{requestId:'run',projectId:'other'},'project_forbidden'],
    ['freeze',{requestId:'freeze'},'page_action_required'],
    ['apply-changes',{requestId:'edit'},'expert_management_forbidden'],
  ]) assert.equal((await f.service.invoke(op,args,p)).error.code,code);
  assert.deepEqual(f.counts(),{starts:0,edits:0});
});
test('ordinary expert only dispatches its bound target and cannot edit',async t=>{
  const f=fixture(t),p=await f.bind('framework-expert');
  assert.equal((await f.service.invoke('run',{requestId:'run',targetId:'consumer'},p)).error.code,'target_forbidden');
  assert.equal((await f.service.invoke('apply-changes',{requestId:'edit'},p)).error.code,'expert_management_forbidden');
  assert.equal((await f.service.invoke('run',{requestId:'own'},p)).ok,true);
  assert.equal(f.counts().starts,1);
});
test('native binding requires actual dedicated preset and rejects stale selection',async t=>{
  const f=fixture(t),args={sessionId:'standard-session',presetId:'agent-trainer',mode:'training',targetKind:'agent',targetId:'producer'};
  assert.equal((await f.page('bind-session',args)).error.code,'session_identity_mismatch');
  await f.bind(); args.sessionId='agent-trainer-session';
  assert.equal((await f.page('bind-session',{...args,baseBindingRevision:0})).error.code,'binding_conflict');
  assert.equal((await f.page('bind-session',{...args,baseBindingRevision:1})).value.bindingRevision,2);
  assert.equal((await f.page('bind-session',{...args,targetId:'consumer',baseBindingRevision:2})).error.code,'session_binding_conflict');
});
test('candidate mutation is idempotent and published page rejects edits',async t=>{
  const f=fixture(t),p=await f.bind();
  const args={requestId:'edit',baseRevision:'rev-1',changes:[{path:'agents/producer/instructions.md',content:'v2'}],reason:'repair'};
  assert.equal((await f.service.invoke('apply-changes',args,p)).ok,true);
  assert.equal((await f.service.invoke('apply-changes',args,p)).ok,true);
  assert.equal(f.counts().edits,1);
  assert.equal((await f.page('apply-changes',{...args,requestId:'engineering-edit',mode:'engineering'})).error.code,'read_only_mode');
});
test('cross-project history and control are rejected',async t=>{
  const f=fixture(t),p=await f.bind();
  f.runs.set('other-run',{runId:'other-run',projectId:'other'});
  assert.equal((await f.service.invoke('control',{requestId:'stop',runId:'other-run',action:'stop'},p)).error.code,'run_not_found');
});
