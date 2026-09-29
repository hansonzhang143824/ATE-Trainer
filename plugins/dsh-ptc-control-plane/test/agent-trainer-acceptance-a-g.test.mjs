import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';
import test from 'node:test';
const root=process.cwd();
const read=r=>JSON.parse(fs.readFileSync(path.join(root,r),'utf8'));
const exists=r=>fs.existsSync(path.join(root,r));
const run=(id,where='Training_Materials/runs')=>read(path.join(where,id,'framework-run.json'));
const evidence=read('docs/agent-trainer-empty-system-acceptance-evidence-20260930.json');
const sha=v=>assert.match(v,/^[0-9a-f]{64}$/);
test('A-G evidence is real, persisted, and smoke-only',()=>{
 const registry=read('team/ptc/ptc_stage_registry.json'); assert.deepEqual(registry.stateMachine,[]); assert.deepEqual(registry.stages,{});
 assert.equal(evidence.scope,'SMOKE_ONLY'); assert.equal(evidence.businessGatePassed,false); assert.equal(evidence.status,'passed_with_real_native_host_and_release_isolation');
 const A=run('framework-a737a636-f6bd-414d-b71b-170ca4d5519b'); assert.equal(A.status,'completed'); assert.deepEqual(A.steps.map(s=>s.agentId),['agent-T1']); assert.equal(A.output.answer,3); assert.equal(A.validation.ok,true);
 const baseline=run('framework-b5f8877f-967c-4a3f-8498-6d888507468e'); const optimized=run('framework-34807056-f7ab-4c93-a9da-7a59df98567a'); assert.equal(baseline.output.answer,5); assert.equal(optimized.output.answer,5); assert.notEqual(baseline.revisionId,optimized.revisionId); assert.equal(optimized.derivedFromRunId,baseline.runId); assert.equal(optimized.changeSetId,'change-60beed1e-f93a-415d-873c-434150bab23e');
 const native=read('Training_Materials/framework/control/bindings/session-c8583eac-c9fc-49fa-b565-debaa0b52bd9.json'); assert.equal(native.presetId,'agent-trainer'); assert.match(native.sessionId,/^session-/); assert.equal(native.effectiveTools.length,9); assert.ok(native.effectiveTools.includes('trainer_context')); assert.ok(native.effectiveTools.includes('trainer_apply_changes')); assert.ok(native.effectiveTools.includes('trainer_compare'));
 const single=run('framework-a737a636-f6bd-414d-b71b-170ca4d5519b'); const two=run('framework-3a5862f0-d4d3-44f6-916e-55f1939eac44'); const three=run('framework-d4511fc1-6cd4-4534-8996-3d2a6d1b4984'); const swapped=run('framework-2cd9b916-b5c0-4942-b965-4993774f7249');
 assert.deepEqual(single.steps.map(s=>s.output.answer),[3]); assert.deepEqual(two.steps.map(s=>s.output.answer),[3,5]); assert.deepEqual(three.steps.map(s=>s.output.answer),[3,5,7]); assert.deepEqual(swapped.steps.map(s=>s.agentId),['agent-T3','agent-T1','agent-T2']); assert.deepEqual(swapped.steps.map(s=>s.output.answer),[7,3,5]); assert.notEqual(three.workflowRevision,swapped.workflowRevision);
 const release=read('publish/versions/release-80b3d739-627b-4b27-b643-828d2066e7ea/release.json'); assert.equal(release.targetId,'workflow-T5'); assert.equal(release.businessGatePassed,false); sha(release.bundleSha256); sha(release.evidenceSha256); assert.deepEqual(release.agentBindings.map(x=>x.agentId),['agent-T3','agent-T1','agent-T2']);
 for(const id of ['framework-ee0630b3-46ac-4477-8c7e-8c0e4732aa41','framework-50d1f194-86ba-44e4-ad6e-49c2f7a7f920']){const p=run(id,'publish/runs'); assert.equal(p.mode,'published'); assert.equal(p.releaseId,release.releaseId); assert.equal(p.status,'completed'); assert.deepEqual(p.steps.map(s=>s.agentId),['agent-T3','agent-T1','agent-T2']); assert.deepEqual(p.steps.map(s=>s.output.answer),[7,3,5]); assert.equal(p.validation.ok,true); assert.equal(p.businessGatePassed,false);}
 assert.equal(evidence.actualUiClicks.G.isolationVerified,true); assert.equal(evidence.actualUiClicks.G.candidateMutationRevision,'revision-f596dcf0-4e52-411a-9c46-8e1d5dc6c2bf'); assert.notEqual(evidence.actualUiClicks.G.candidateMutationRevision,release.revisionId);
 for(const file of evidence.d7.checkpointFiles) assert.equal(exists(file),true,file);
 for(const file of Object.values(evidence.artifacts).flat()) { if(typeof file==='string'&&file.endsWith('.json')) assert.equal(exists(file),true,file); }
 const bytes=fs.readFileSync('docs/agent-trainer-empty-system-acceptance-evidence-20260930.json'); const expected=fs.readFileSync('docs/agent-trainer-empty-system-acceptance-evidence-20260930.json.sha256','utf8').trim().split(/\s+/)[0]; assert.equal(createHash('sha256').update(bytes).digest('hex'),expected);
});
test('D5-D6 output mapping and release records are verifiable',()=>{
 const release=read('publish/versions/release-80b3d739-627b-4b27-b643-828d2066e7ea/verification.json'); assert.equal(release.status,'completed'); assert.equal(release.validation.ok,true);
});
