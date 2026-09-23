#!/usr/bin/env python3
"""Generate bounded DFT products and semantic review input without reading old output."""
from __future__ import annotations
import argparse, hashlib, json, os, re, sys, tempfile
from pathlib import Path
import dft_source
import dft_test_condition
from material_plaintext_hash import sha256_plaintext

ROOT = Path(__file__).resolve().parents[1]

def byte_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def require_trial_manifest(path: Path, expected_source_sha: str, tm: str) -> dict:
    resolved = path.resolve(); artifacts = (ROOT / 'team' / 'artifacts').resolve()
    if resolved.name != 'input-manifest.json' or artifacts not in resolved.parents:
        raise ValueError('--manifest must be an input-manifest.json under team/artifacts')
    obj = json.loads(resolved.read_text(encoding='utf-8'))
    recorded = ((obj.get('canonicalInputs') or {}).get('dft') or {}).get('sha256')
    if recorded != expected_source_sha:
        raise ValueError('manifest canonical DFT plaintext hash does not match the workbook')
    text = json.dumps(obj, ensure_ascii=False)
    if f'dft\\{tm}' not in text and f'dft/{tm}' not in text:
        raise ValueError(f'manifest does not authorize DFT output for {tm}')
    return {'path': str(resolved), 'sha256': byte_sha256(resolved), 'canonicalInputsDftSha256': recorded}

def parse_vsets(row: dict) -> list[dict]:
    commands=[]
    for column in ('Code1','Code2','Code3','Dynamic'):
        for order,match in enumerate(re.finditer(r'vset\[([^,\]]+)\s*,\s*([^\]]*)\]',str(row.get(column,'')),flags=re.I),1):
            pin=match.group(1).strip(); values=[part.strip() for part in match.group(2).split(',')]
            commands.append({'column':column,'order':order,'pin':pin,'args':values,'raw':match.group(0),'powerOnDirect':len(values)>=2 and values[1]=='100e-6'})
    return commands

def yaml_scalar(value: object) -> str: return json.dumps(value, ensure_ascii=False)

def render_yaml(tm: str, source: Path, source_sha: str, row: dict, condition: dict) -> str:
    pins=[]
    for column in ('Code1','Code2','Code3','Dynamic'):
        pins.extend(re.findall(r'\bvset\[([^,\]]+)',str(row.get(column,'')),flags=re.I))
    lines=['schemaVersion: 1','artifact: "dft-conditions"','projectId: "DALI"',f'tm: {yaml_scalar(tm)}',f'sourcePath: {yaml_scalar(str(source))}',f'sourceSheet: {yaml_scalar(dft_source.OVERVIEW_SHEET)}',f'sourceSha256: {yaml_scalar(source_sha)}','rawIntent:']
    for key,value in row.items():
        if key: lines.append(f"  {str(key).replace(' ','_').replace(chr(10),'_')}: {yaml_scalar(value)}")
    lines += ['derivedTokens:',f'  vsetPins: {yaml_scalar(pins)}','testCondition:']
    for key,value in condition.items(): lines.append(f'  {key}: {yaml_scalar(value)}')
    return '\n'.join(lines)+'\n'

def atomic_write_pair(meta_path: Path, meta_text: str, yaml_path: Path, yaml_text: str) -> None:
    meta_path.parent.mkdir(parents=True,exist_ok=True); yaml_path.parent.mkdir(parents=True,exist_ok=True); staged=[]
    try:
        for destination,content in ((meta_path,meta_text),(yaml_path,yaml_text)):
            fd,name=tempfile.mkstemp(prefix=f'.{destination.name}.',suffix='.tmp',dir=destination.parent)
            with os.fdopen(fd,'w',encoding='utf-8',newline='') as handle:
                handle.write(content); handle.flush(); os.fsync(handle.fileno())
            staged.append((Path(name),destination))
        for source,destination in staged: os.replace(source,destination)
    finally:
        for source,_ in staged: source.unlink(missing_ok=True)

def output_path(value: Path, tm: str, filename: str) -> Path:
    resolved=value.resolve(); required=(ROOT/'project'/'DALI'/'Output_Global_Material'/'dft'/tm/filename).resolve()
    if resolved != required: raise ValueError(f'output path must be project/DALI/Output_Global_Material/dft/{tm}/{filename}')
    return resolved

def main() -> int:
    parser=argparse.ArgumentParser(); parser.add_argument('--source',type=Path,required=True); parser.add_argument('--tm',required=True); parser.add_argument('--meta',type=Path,required=True); parser.add_argument('--yaml',type=Path,required=True); parser.add_argument('--expected-sha',required=True); parser.add_argument('--manifest',type=Path,required=True); args=parser.parse_args(); tm=args.tm.upper()
    try:
        source=args.source.resolve(); dft_source.ensure_within(source,dft_source.INPUT_ROOT)
        if source != dft_source.discover_workbook().resolve(): raise ValueError('source is not the canonical DFT workbook')
        if not re.fullmatch(r'TM\d+',tm): raise ValueError('invalid TM')
        source_sha=sha256_plaintext(source)
        if source_sha != args.expected_sha.lower(): raise ValueError('workbook plaintext hash differs from --expected-sha')
        ruling=require_trial_manifest(args.manifest,source_sha,tm); rows=dft_source.rows_for(source,tm)
        if len(rows)!=1: raise ValueError(f'expected exactly one OVERVIEW row for {tm}; found {len(rows)}')
        meta_path=output_path(args.meta,tm,'dft-meta.json'); yaml_path=output_path(args.yaml,tm,'dft-conditions.yaml')
    except (OSError,ValueError,json.JSONDecodeError) as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr); return 2
    raw_intent={key:value for key,value in rows[0].items() if key}; derived=dft_test_condition.derive(raw_intent); condition=derived['testCondition']; vsets=parse_vsets(raw_intent); pins=list(dict.fromkeys(command['pin'] for command in vsets))
    meta={'schemaVersion':1,'artifactId':'dft-meta','projectId':'DALI','tm':tm,'sourceSha256':source_sha,'canonicalInput':str(source),'readSources':[{'path':str(source),'sha256':source_sha,'insideInputRoot':True}],'rawIntent':raw_intent,'parsedVsetCommands':vsets,'declaredPins':pins,'openItems':[],'generation':'deterministic OVERVIEW-only parse','ruling':ruling,**derived}
    meta_text=json.dumps(meta,ensure_ascii=False,indent=2)+'\n'; yaml_text=render_yaml(tm,source,source_sha,raw_intent,condition)
    try: atomic_write_pair(meta_path,meta_text,yaml_path,yaml_text)
    except OSError as exc: print(f'BLOCKED: cannot write DFT products: {exc}',file=sys.stderr); return 2
    review_input={'schemaVersion':1,'tm':tm,'canonicalSource':{'path':str(source),'sha256':source_sha,'withinInputRoot':True,'sheet':dft_source.OVERVIEW_SHEET},'manifest':ruling,'rawIntent':raw_intent,'testCondition':condition,'reviewedArtifacts':[{'path':str(meta_path),'sha256':byte_sha256(meta_path)},{'path':str(yaml_path),'sha256':byte_sha256(yaml_path)}],'reviewInstructions':'Review only these supplied canonical-source facts. Do not open an output, old product, another workbook sheet, or an engineering file. Return PASS only if rawIntent and testCondition preserve the supplied source facts; otherwise NEEDS_FIX.'}
    print(json.dumps({'status':'READY_FOR_SEMANTIC_REVIEW','semanticReviewInput':review_input},ensure_ascii=False,separators=(',',':'))); return 0
if __name__=='__main__': raise SystemExit(main())
