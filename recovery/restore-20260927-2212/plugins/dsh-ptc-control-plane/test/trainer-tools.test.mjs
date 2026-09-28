import test from 'node:test';
import assert from 'node:assert/strict';
import path from 'node:path';
import fs from 'node:fs';
import {pathToFileURL} from 'node:url';
import {createRequire} from 'node:module';
import {createTrainerTools} from '../lib/trainer-tools.js';
const host=process.env.DSH_TEST_HOST_PACKAGE || path.join(process.env.APPDATA || '', 'npm/node_modules/@deepseek-ai/dsh/package.json');
test('real installed DSH defineTool accepts Trainer schemas and returns canonical service JSON',{skip:!fs.existsSync(host)},async()=>{
  const require=createRequire(pathToFileURL(host));
  const {defineTool}=await import(pathToFileURL(require.resolve('@deepseek-ai/dsh-tools')).href);
  const calls=[];const principal={kind:'tool',sessionId:'trainer-session',presetId:'agent-trainer'};
  const tools=createTrainerTools({invoke:async(op,args,p)=>{calls.push({op,args,p});return {ok:true,value:{runId:'synthetic-run'}};}},{defineTool,principalOf:()=>principal});
  assert.equal(tools.length,9);assert.equal(tools.some(t=>/publish|freeze|activate/.test(t.name)),false);
  const result=await tools.find(t=>t.name==='trainer_run').execute({requestId:'request-1',targetKind:'agent',targetId:'producer',input:{seed:7}},{});
  assert.equal(result.value.runId,'synthetic-run');assert.equal(calls[0].p,principal);
  const content=tools.find(t=>t.name==='trainer_run').output.render({},result);
  assert.deepEqual(content,[{type:'text',text:JSON.stringify(result)}]);
  const expert=createTrainerTools({},{defineTool,principalOf:()=>principal,role:'framework-expert'});
  assert.equal(expert.some(t=>t.name==='trainer_apply_changes'),false);
});


// Real registry layering: a standing preset is inherited by each session.
test('real DSH scope keeps role tools visible while filtering global tools', {skip:!fs.existsSync(host)}, async()=>{
  const require=createRequire(pathToFileURL(host));
  const load=async name=>import(pathToFileURL(require.resolve(name)).href);
  const {Context}=await load('@deepseek-ai/cordis');
  const {createScope}=await load('@deepseek-ai/dsh-scope');
  const {SystemPrompt}=await load('@deepseek-ai/dsh-system-prompt');
  const {ToolRuntime,defineTool}=await load('@deepseek-ai/dsh-tools');
  const {restrictTrainerSessionTools}=await import('../lib/trainer-preset.js');
  const ctx=new Context();
  new SystemPrompt(ctx,{});
  new ToolRuntime(ctx,{mode:'native'});
  const presetKey={};const preset=createScope(ctx,presetKey);
  const agent={};const scoped=createScope(ctx,agent,{parent:presetKey});agent.ctx=scoped.ctx;
  const tool=name=>defineTool({name,description:name,parameters:{},output:{schema:{type:'json'},render:()=>[]},execute:async()=>({})});
  ctx.tools.register(tool('global_unrelated'));
  const definitions=createTrainerTools({}, {defineTool,principalOf:()=>({}),role:'framework-expert'});
  for(const definition of definitions)preset.ctx.tools.register(definition);
  // Regression proof: restricting at the standing scope hides its own catalog from descendants.
  const undoOld=preset.ctx.tools.restrict({allow:[]});
  assert.deepEqual(agent.ctx.tools.schemas(agent),[]);undoOld();
  const names=definitions.map(t=>t.name);
  assert.deepEqual(restrictTrainerSessionTools(agent,names),[...names].sort());
  assert.equal(agent.ctx.tools.schemas(agent).some(t=>t.name==='global_unrelated'),false);
  assert.equal(ctx.tools.schemas().some(t=>t.name==='global_unrelated'),true);
  await scoped.dispose();await preset.dispose();
});
