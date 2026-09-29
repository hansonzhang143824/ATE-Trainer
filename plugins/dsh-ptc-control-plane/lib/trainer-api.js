export function createTrainerApiHandler(service,operation) {
  return async (request,response) => {
    const reply=(status,body)=>{response.writeHead(status,{'Content-Type':'application/json; charset=utf-8','Cache-Control':'no-store'});response.end(JSON.stringify(body));};
    if (request.method !== 'POST') return reply(405,{ok:false,error:{code:'method_not_allowed',message:'Use POST'}});
    if (String(request.headers?.['content-type']||'').split(';')[0].trim().toLowerCase() !== 'application/json') return reply(415,{ok:false,error:{code:'invalid_content_type',message:'Use application/json'}});
    // Same-origin local workbench only; cross-origin forms cannot mutate state.
    const origin=request.headers?.origin;
    if (origin) {
      try { if (new URL(origin).host !== request.headers.host) throw new Error('origin mismatch'); }
      catch { return reply(403,{ok:false,error:{code:'origin_forbidden',message:'Workbench origin mismatch'}}); }
    }
    try {
      let size=0;const chunks=[];
      for await(const chunk of request){const b=Buffer.from(chunk);size+=b.length;if(size>2*1024*1024)throw new Error('Request exceeds 2 MiB');chunks.push(b);}
      const args=JSON.parse(Buffer.concat(chunks).toString('utf8'));
      if(!args || typeof args!=='object' || Array.isArray(args))throw new Error('Expected JSON object');
      const principal=operation==='session-tool'
        ? {kind:'tool',sessionId:args.sessionId,presetId:args.presetId}
        : {kind:'page'};
      const result=operation==='session-tool'
        ? await service.invoke('session-tool',args,principal)
        : await service.invoke(operation,args,principal);
      return reply(result.ok?200:400,result);
    }catch(error){return reply(400,{ok:false,error:{code:'invalid_request',message:error.message}});}
  };
}
export const TRAINER_API_OPERATIONS=['context','assets','apply-changes','validate','run','runs','events','control','compare','changes','freeze','stage-release','activate-release','releases','bind-session','open-native-session','session-workspace','session-tool'];
