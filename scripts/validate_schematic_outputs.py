#!/usr/bin/env python3
"""Validate matching, lossless schematic TXT and JSON products."""
from __future__ import annotations
import argparse,base64,hashlib,json
from pathlib import Path
import dft_source
from material_plaintext_hash import sha256_plaintext
ROOT=dft_source.ROOT; INPUT=dft_source.INPUT_ROOT.resolve(); OUT=dft_source.schematic_output_dir(); PAIRS=(("SCH-Connect-Map.txt","SCH-Connect-Map.json"),("Component-Statistic.txt","Components-Statistic.json")); PATH_PROOFS=("Path-Proofs.txt","Path-Proofs.json")
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def resolve(value):
 p=Path(value); return (p if p.is_absolute() else ROOT/p).resolve()
def validate(source=None,confirmed=None):
 source=(source or dft_source.discover_schematic()).resolve(); confirmed=(confirmed or INPUT/'sch_confirmed.json').resolve(); cbit=(INPUT/'CBIT表-DALI.xlsx').resolve(); stale=[]; receipt_path=OUT/'schematic-receipt.json'
 try:
  receipt=json.loads(receipt_path.read_text(encoding='utf-8-sig')); expected={source:sha256_plaintext(source),confirmed:sha256_plaintext(confirmed),cbit:sha256_plaintext(cbit)}; reads=receipt.get('readSources'); actual={}
  if not isinstance(reads,list) or len(reads)!=len(expected): raise ValueError('readSources is incomplete')
  for item in reads:
   path=resolve(item.get('path',''))
   if item.get('insideInputRoot') is not True or not path.is_relative_to(INPUT) or path not in expected or item.get('sha256')!=expected[path]: raise ValueError('readSources contains an unapproved or stale source')
   actual[path]=item['sha256']
  if actual!=expected or receipt.get('parserStatus')!='PASS': raise ValueError('receipt does not bind approved inputs and a passing parser')
  outputs=receipt.get('outputs',{})
  for txt_name,json_name in PAIRS:
   txt,json_file=OUT/txt_name,OUT/json_name
   if not txt.is_file() or not json_file.is_file() or outputs.get(txt_name,{}).get('sha256')!=sha(txt) or outputs.get(json_name,{}).get('sha256')!=sha(json_file): raise ValueError(f'{txt_name} or {json_name} is missing or changed')
   data=json.loads(json_file.read_text(encoding='utf-8-sig')); raw=base64.b64decode(data.get('rawBytesBase64',''),validate=True)
   if raw!=txt.read_bytes() or data.get('sourceTxt',{}).get('sha256')!=sha(txt): raise ValueError(f'{json_name} is not a lossless copy of {txt_name}')
   lines=txt.read_bytes().decode('utf-8').splitlines(); restored=[line for section in data.get('sections',[]) for line in section.get('lines',[])]
   if restored!=lines: raise ValueError(f'{json_name} sections do not cover every TXT line')
  comp=json.loads((OUT/'Components-Statistic.json').read_text(encoding='utf-8-sig'))
  if not comp.get('semanticIndex',{}).get('dutKelvinPins'): raise ValueError('Components JSON lacks DUT pin index')
  mapping=json.loads((OUT/'SCH-Connect-Map.json').read_text(encoding='utf-8-sig'))
  index=mapping.get('semanticIndex',{})
  if not index.get('needCloseCount') or not index.get('hasRelayOn') or not index.get('hasRelayNc'): raise ValueError('connect-map JSON lacks relay path facts')
  proof_txt,proof_json=OUT/PATH_PROOFS[0],OUT/PATH_PROOFS[1]
  if not proof_txt.is_file() or not proof_json.is_file() or outputs.get(PATH_PROOFS[0],{}).get('sha256')!=sha(proof_txt) or outputs.get(PATH_PROOFS[1],{}).get('sha256')!=sha(proof_json): raise ValueError('Path-Proofs output is missing or changed')
  proof=json.loads(proof_json.read_text(encoding='utf-8-sig'))
  if proof.get('status')!='PASS' or not proof.get('accepted_path_proofs'): raise ValueError('Path-Proofs has no passing accepted paths')
  if proof.get('readSources')!=reads or proof.get('input',{}).get('sha256')!=expected[source] or proof.get('cbit',{}).get('sha256')!=expected[cbit]: raise ValueError('Path-Proofs is not bound to approved plaintext inputs')
  if 'status=PASS' not in proof_txt.read_text(encoding='utf-8',errors='replace'): raise ValueError('Path-Proofs text summary is not passing')
 except (OSError,ValueError,TypeError,json.JSONDecodeError) as exc: stale.append(f'{receipt_path}: {exc}')
 return {'role':'schematic-expert','gate':'SCHEMATIC_OUTPUT','status':'ready' if not stale else 'stale','canonicalInput':{'path':str(source),'sha256':sha256_plaintext(source)},'requiredOutputs':[str(OUT/name) for pair in PAIRS for name in pair]+[str(OUT/name) for name in PATH_PROOFS]+[str(receipt_path)],'missingOrStaleOutputs':stale}
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path); ap.add_argument('--confirmed',type=Path); args=ap.parse_args(); report=validate(args.source,args.confirmed); print(json.dumps(report,ensure_ascii=False,indent=2)); return 0 if report['status']=='ready' else 2
if __name__=='__main__': raise SystemExit(main())
