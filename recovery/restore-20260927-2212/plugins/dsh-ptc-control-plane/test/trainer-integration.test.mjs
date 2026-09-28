import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import * as projects from '../lib/trainer-project.js';
import * as bundles from '../lib/trainer-bundle.js';
import * as releases from '../lib/trainer-release.js';
import {validateJson} from '../lib/trainer-schema.js';
import {createFrameworkRunner} from '../lib/framework-agent-run.js';
import {createTrainerService} from '../lib/trainer-service.js';

test('service + real assets/runner: failure, candidate repair, frozen release and isolated replay (fake model)',async t=>{
  const root=fs.mkdtempSync(path.join(os.tmpdir(),'trainer-integration-'));t.after(()=>fs.rmSync(root,{recursive:true,force:true}));
  let children=0;
  const adapter={async dispatch({step,input,bundle,onStart}){
    const childSessionId=`fake-child-${++children}`;onStart({childSessionId,parentSessionId:'fake-parent'});
    const marker=JSON.parse(bundle.files.find(f=>f.path==='skills/lab-marker/references/marker.json')?.content || '{}').marker;
    return {output:step.agentId==='lab-producer'?{value:input.seed+1,marker,scriptMarker:'script-v1'}:{receivedValue:input.receivedValue},childSessionId,childTerminationConfirmed:true,stopReason:'completed'};
  }};
  const runner=createFrameworkRunner({workspaceRoot:root,adapter,verifyBundle:bundles.verifyBundle,validateJson});
  const service=createTrainerService({workspaceRoot:root,runner,repositories:{...projects,...bundles,...releases},modelResolver:()=>({provider:'fake',model:'fake'}),sessionVerifier:()=>true});
  let counter=0;
  const target={projectId:'synthetic-lab',targetKind:'workflow',targetId:'lab-pair'};
  async function invoke(op,args={}) {const result=await service.invoke(op,{...target,...args},{kind:'page'});assert.equal(result.ok,true,JSON.stringify(result));return result.value;}
  const project=(await invoke('context')).project;
  const files=(await invoke('assets')).files;
  const original=JSON.parse(files['workflows/lab-pair.json']);
  const broken=structuredClone(original);broken.steps[1].inputBindings['/receivedValue'].pointer='/missing';
  const bad=await invoke('apply-changes',{requestId:'break',baseRevision:project.revisionId,changes:[{path:'workflows/lab-pair.json',content:JSON.stringify(broken)}],reason:'synthetic fault'});
  const start=await invoke('run',{requestId:'bad-run',input:{seed:7}});await runner.waitForRun({runId:start.runId});
  const failed=await invoke('runs',{runId:start.runId});assert.equal(failed.status,'failed');assert.equal(children,1);
  const saved=await invoke('apply-changes',{requestId:'repair',baseRevision:bad.revisionId,changes:[{path:'workflows/lab-pair.json',content:JSON.stringify(original)}],reason:'repair missing field',linkedRunId:start.runId});
  const retry=await invoke('run',{requestId:'retry',input:{seed:7},derivedFromRunId:start.runId,changeSetId:saved.changeSetId});await runner.waitForRun({runId:retry.runId});
  const good=await invoke('runs',{runId:retry.runId});assert.equal(good.status,'completed');assert.deepEqual(good.steps[1].output,{receivedValue:8});
  assert.equal((await invoke('runs',{runId:start.runId})).status,'failed');
  const frozen=await invoke('freeze',{requestId:'freeze',runId:retry.runId});
  const release=await invoke('stage-release',{requestId:'stage',mode:'published',frozenVersionId:frozen.frozenVersionId,runId:retry.runId});
  await invoke('activate-release',{requestId:'activate',mode:'published',releaseId:release.releaseId});
  await invoke('apply-changes',{requestId:'later',baseRevision:saved.revisionId,changes:[{path:'skills/lab-marker/references/marker.json',content:'{"marker":"v2"}'}],reason:'future revision'});
  const replay=await invoke('run',{requestId:'replay',mode:'engineering',input:{seed:19}});await runner.waitForRun({runId:replay.runId});
  const replayed=await invoke('runs',{runId:replay.runId});assert.equal(replayed.status,'completed');assert.equal(replayed.releaseId,release.releaseId);assert.equal(replayed.bundleSha256,good.bundleSha256);assert.equal(replayed.steps[0].output.marker,'v1');assert.equal(replayed.steps[1].output.receivedValue,20);
  assert.equal(replayed.businessGatePassed,false);
});
