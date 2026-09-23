import sys,io,os,json,hashlib,time
sys.stdout=io.TextIOWrapper(sys.stdout.buffer,encoding='utf-8',errors='replace')
d=r'D:\Newtest\DSH\ATE-Coding-Plat\team\artifacts\acceptance-20260916-dali10'
mp=os.path.join(d,'implementation-manifest.json')
before=open(mp,'rb').read()
M=json.loads(before.decode('utf-8-sig'))
M['handoffCitationRisk']['citationModel']={
 'why':('Added because a reviewer reported that the L1/L2 mix in this document could not be mechanically recovered: '
   'a string is structurally identical whether it is a reference or a status. Declaring the convention below makes the '
   'structure readable without inventing a value. No existing value was changed.'),
 'referencePredicate':('A string counts as a REFERENCE only if it names an artefact or an artefact path. Judged by the '
   'FIELD NAME that carries it (artefact, path, payloadPath, original, applicationProcedure, command) - never by the '
   'value shape, because runId / status / authoredBy / note are also strings and are NOT references.'),
 'L1_definition':'A citation carrying the artefact identity AND a numeric measurement of it (size, sha256, mtime) in the same object.',
 'L2_definition':'A citation carrying the artefact identity (path or name) with NO numeric measurement; the reader must recompute.',
 'whereEachIsUsed':[
   'L1: authoritativeCurrentValues[*] - each entry pairs an artefact with size/sha256/mtime and qualifier fields.',
   'L2: frozenInputs[*] and changes[*] - inputs and backups are cited by path only; recompute before relying on them.',
   'L2 (with a value recorded as an anomaly, not as a citation): withdrawnFromAuthoritativeList[*].why, which quotes a '
   'recorded-versus-actual mismatch as EVIDENCE for removal rather than as a current identity.'],
 'consequence':('Under an L2 citation a value-level qualifier (L-a) does not travel, so the sibling field is the only '
   'qualifier that survives; under L1 it does travel. That is why the fields in this document are named for their instant '
   'where possible, and why the reader is told to recompute.')}
open(mp,'wb').write((json.dumps(M,ensure_ascii=False,indent=2)+'\n').encode('utf-8'))
after=open(mp,'rb').read()
print('manifest %d B -> %d B / %s'%(len(before),len(after),hashlib.sha256(after).hexdigest()))
J=json.loads(after.decode('utf-8'))
cm=J['handoffCitationRisk']['citationModel']
print('  added citationModel with keys:',list(cm.keys()))
p=os.path.join(d,'implementation-payload-TM600-TM601.cpp'); pr=open(p,'rb').read()
print('  payload untouched:', hashlib.sha256(pr).hexdigest()=='66abc088ae6bd5f9b9d7201673003fc0be2450fd6f1f222c6a4a902cbe4f0cc4')