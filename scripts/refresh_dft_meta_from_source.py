#!/usr/bin/env python3
"""Generate one DFT metadata artifact directly from the canonical workbook OVERVIEW row."""
from __future__ import annotations
import argparse,hashlib,json,re,sys
from pathlib import Path
import dft_source
import dft_test_condition
from material_plaintext_hash import sha256_plaintext
from ptc_contract_schema import validate_test_condition

ROOT = Path(__file__).resolve().parents[1]


def byte_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load_ruling(path: Path, digest: str) -> dict:
    """Bind this regeneration to the trial manifest that authorizes it.

    The role boundary permits this generator only together with its trial
    manifest, so the manifest is validated against the canonical workbook hash
    and recorded as provenance instead of being ignored.
    """
    resolved = path.resolve()
    artifacts = (ROOT / 'team' / 'artifacts').resolve()
    if resolved.name != 'input-manifest.json' or artifacts not in resolved.parents:
        raise ValueError('--ruling must be a trial input-manifest.json under team/artifacts')
    manifest = json.loads(resolved.read_text(encoding='utf-8'))
    recorded = ((manifest.get('canonicalInputs') or {}).get('dft') or {}).get('sha256')
    if recorded != digest:
        raise ValueError(f'ruling manifest DFT sha256 {recorded} differs from the canonical workbook hash {digest}')
    return {'path': str(resolved), 'sha256': byte_sha256(resolved), 'canonicalInputsDftSha256': recorded}

def parse_vsets(row:dict)->list[dict]:
    commands=[]
    for column in ('Code1','Code2','Code3','Dynamic'):
        for order,match in enumerate(re.finditer(r'vset\[([^,\]]+)\s*,\s*([^\]]*)\]',str(row.get(column,'')),flags=re.I),1):
            pin=match.group(1).strip(); args=[x.strip() for x in match.group(2).split(',')]
            commands.append({'column':column,'order':order,'pin':pin,'args':args,'raw':match.group(0),'powerOnDirect':len(args)>=2 and args[1]=='100e-6'})
    return commands

def source_row_number(workbook: Path, tm: str) -> int:
    wb = dft_source.openpyxl.load_workbook(workbook, read_only=True, data_only=True)
    try:
        if dft_source.OVERVIEW_SHEET not in wb.sheetnames:
            raise ValueError(f"workbook has no {dft_source.OVERVIEW_SHEET} sheet")
        for row_number, values in enumerate(wb[dft_source.OVERVIEW_SHEET].iter_rows(values_only=True), start=1):
            if values and str(values[0]).strip().upper() == tm:
                return row_number
    finally:
        wb.close()
    raise ValueError(f"no {dft_source.OVERVIEW_SHEET} row for {tm}")


def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--tm',required=True); ap.add_argument('--meta',type=Path,required=True); ap.add_argument('--expected-sha',required=True); ap.add_argument('--ruling',type=Path); ap.add_argument('--input-root',type=Path); args=ap.parse_args()
    source=args.source.resolve(); tm=args.tm.upper()
    try:
        if args.input_root is not None:
            input_root=args.input_root.resolve()
            dft_source.ensure_within(source,input_root)
            if source!=dft_source.discover_workbook(input_root).resolve(): raise ValueError('source is not the canonical workbook under --input-root')
            material_root=input_root.parent if input_root.name=='Input_GlobalMaterial' else input_root
            dft_source.ensure_within(args.meta,material_root)
        else:
            dft_source.ensure_within(source,dft_source.INPUT_ROOT)
            if source!=dft_source.discover_workbook().resolve(): raise ValueError('source is not the canonical workbook')
        digest=sha256_plaintext(source)
        if digest!=args.expected_sha.lower(): raise ValueError('workbook plaintext hash differs from --expected-sha')
        rows=dft_source.rows_for(source,tm)
        if len(rows)!=1: raise ValueError(f'expected one OVERVIEW row for {tm}; found {len(rows)}')
        ruling=load_ruling(args.ruling,digest) if args.ruling else None
    except ValueError as exc:
        print(f'BLOCKED: {exc}',file=sys.stderr); return 2
    row={key:value for key,value in rows[0].items() if key}; commands=parse_vsets(row); condition=dft_test_condition.derive(row)
    condition_errors=validate_test_condition(condition.get('testCondition'))
    open_items=[{'type':'unparsable','description':error} for error in condition_errors]
    pins=[]
    for command in commands:
        if command['pin'] not in pins: pins.append(command['pin'])
    meta={'schemaVersion':1,'artifactId':'dft-meta','projectId':'DALI','tm':tm,'sourceSha256':digest,'canonicalInput':str(source),'readSources':[{'path':str(source),'sha256':digest,'insideInputRoot':True}],'sourceLocation':{'sheet':dft_source.OVERVIEW_SHEET,'row':source_row_number(source,tm)},'parseStatus':'ok' if not open_items else 'pendingUser','rawIntent':row,'parsedVsetCommands':commands,'declaredPins':pins,'openItems':open_items,'generation':'deterministic OVERVIEW-only parse', **condition}
    if ruling is not None: meta['ruling']=ruling
    args.meta.parent.mkdir(parents=True,exist_ok=True); args.meta.write_text(json.dumps(meta,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'DONE: {args.meta}; tm={tm}; sourceSha256={digest}; metaSha256={byte_sha256(args.meta)}')
    print('rawIntent='+json.dumps(row,ensure_ascii=False,sort_keys=True))
    print('testCondition='+json.dumps(meta.get('testCondition',{}),ensure_ascii=False,sort_keys=True)); return 0
if __name__=='__main__': raise SystemExit(main())
