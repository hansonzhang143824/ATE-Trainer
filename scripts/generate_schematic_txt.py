#!/usr/bin/env python3
"""Publish lossless schematic JSON for AI and matching TXT for human review."""
from __future__ import annotations
import argparse, base64, contextlib, hashlib, json, os, re, secrets, shutil, subprocess, sys
from pathlib import Path
import dft_source
from material_plaintext_hash import sha256_plaintext
ROOT=dft_source.ROOT; INPUT_ROOT=dft_source.INPUT_ROOT.resolve()
PAIRS=(("SCH-Connect-Map.txt","SCH-Connect-Map.json","SCH-Connect-Map"),("Component-Statistic.txt","Components-Statistic.json","Components-Statistic"))
PATH_PROOFS=("Path-Proofs.txt","Path-Proofs.json")
def inside_input(path: Path)->Path:
    path=path.resolve()
    if not path.is_relative_to(INPUT_ROOT): raise ValueError(f"source is outside Input_GlobalMaterial: {path}")
    if not path.is_file(): raise FileNotFoundError(path)
    return path
def sha(path: Path)->str: return hashlib.sha256(path.read_bytes()).hexdigest()
def relative(path:Path)->str: return path.resolve().relative_to(ROOT.resolve()).as_posix()
def read_source(path:Path)->dict: return {"path":relative(path),"sha256":sha256_plaintext(path),"insideInputRoot":True}
def sections(text:str)->list[dict]:
    lines=text.splitlines(); result=[]; start=1; title="preamble"; bucket=[]
    for number,line in enumerate(lines,1):
        if line.startswith("## ") and bucket:
            result.append({"title":title,"startLine":start,"endLine":number-1,"lines":bucket}); title=line[3:].strip(); start=number; bucket=[line]
        else: bucket.append(line)
    result.append({"title":title,"startLine":start,"endLine":len(lines),"lines":bucket})
    return result
def semantic_index(kind:str,text:str)->dict:
    result={"lineCount":len(text.splitlines())}
    if kind=="Components-Statistic":
        marker=text.find("DUT PIN")
        chapter=text[marker:] if marker >= 0 else ""
        chapter=chapter.split("\n## ", 1)[0]
        result["dutKelvinPins"]=re.findall(r"([A-Za-z][A-Za-z0-9_]*)\(Kelvin\)", chapter)
    else:
        result["needCloseCount"]=text.count("需闭合:"); result["hasRelayOn"]="Relay-ON=" in text; result["hasRelayNc"]="Relay-NC=" in text
    return result
@contextlib.contextmanager
def staging_directory(parent:Path):
    """A staging directory the write-restricted sandbox can actually use.

    `tempfile.mkdtemp` is deliberately NOT used: its 0o700 mode becomes an explicit,
    PROTECTED DACL on Windows (SE_DACL_PROTECTED), which blocks the parent's
    inheritable sandbox write grant and leaves the directory unwritable and
    undeletable for a confined process. A default-mode directory inherits normally.
    Cleanup is best effort so a removal failure can never decide the outcome.
    """
    stage=Path(parent)/f"schematic-full-{secrets.token_hex(4)}"
    stage.mkdir(parents=True,exist_ok=False)
    try:
        yield stage
    finally:
        shutil.rmtree(stage,ignore_errors=True)
def make_json(txt:Path,json_path:Path,kind:str,reads:list[dict])->dict:
    raw=txt.read_bytes(); text=raw.decode("utf-8")
    payload={"schemaVersion":1,"artifactId":kind,"artifactKind":kind,"format":"lossless-text-projection","readSources":reads,"sourceTxt":{"path":txt.name,"sha256":hashlib.sha256(raw).hexdigest(),"bytes":len(raw),"encoding":"utf-8"},"rawBytesBase64":base64.b64encode(raw).decode("ascii"),"rawText":text,"sections":sections(text),"semanticIndex":semantic_index(kind,text)}
    json_path.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    return {"sha256":sha(json_path),"bytes":json_path.stat().st_size,"sourceTxtSha256":payload["sourceTxt"]["sha256"]}
def main()->int:
    ap=argparse.ArgumentParser(); ap.add_argument("--source",type=Path,required=True); ap.add_argument("--confirmed",type=Path,required=True); ap.add_argument("--cbit",type=Path,required=True); ap.add_argument("--out-dir",type=Path,required=True); ap.add_argument("--expected-source-sha",required=True); ap.add_argument("--expected-confirmed-sha",required=True); ap.add_argument("--expected-cbit-sha",required=True); args=ap.parse_args()
    source,confirmed,cbit=inside_input(args.source),inside_input(args.confirmed),inside_input(args.cbit)
    if sha256_plaintext(source)!=args.expected_source_sha.lower(): raise ValueError("canonical CSV plaintext hash differs from --expected-source-sha")
    if sha256_plaintext(confirmed)!=args.expected_confirmed_sha.lower(): raise ValueError("confirmation plaintext hash differs from --expected-confirmed-sha")
    if sha256_plaintext(cbit)!=args.expected_cbit_sha.lower(): raise ValueError("CBIT plaintext hash differs from --expected-cbit-sha")
    out=args.out_dir.resolve()
    if out!=dft_source.schematic_output_dir().resolve(): raise ValueError(f"out-dir must be {dft_source.schematic_output_dir()}")
    out.mkdir(parents=True,exist_ok=True); reads=[read_source(source),read_source(confirmed),read_source(cbit)]
    # The staging tree lives INSIDE the output dir so the staged parser sees the real
    # deployment layout. It must ALSO be created with the process DEFAULT mode:
    # `tempfile.mkdtemp` creates 0o700, and on Windows CPython implements that as an
    # explicit, PROTECTED DACL (`SE_DACL_PROTECTED`) whose only ACEs are OWNER
    # RIGHTS / SYSTEM / Administrators. A protected DACL blocks inheritance, so the
    # directory never receives the parent's inheritable sandbox write grant and a
    # write-restricted process can neither write nor delete inside it — the exact
    # failure this script hit under the workspace-write sandbox. Creating it with the
    # default mode keeps the inherited ACEs. `PTC_SCHEMATIC_STAGE_DIR` relocates only
    # the staging PARENT (unset = the output dir).
    stage_parent=Path(os.environ.get("PTC_SCHEMATIC_STAGE_DIR") or out)
    with staging_directory(stage_parent) as stage:
        shutil.copy2(ROOT/"project_config.json",stage/"project_config.json"); shutil.copytree(ROOT/"scripts",stage/"scripts")
        stage_dali=stage/"Project"/"DALI"; stage_dali.mkdir(parents=True); stage_out=stage/"project"/"DALI"/"Output_Global_Material"/"schematic"; stage_out.mkdir(parents=True,exist_ok=True)
        staged_csv=stage_dali/source.name; staged_cbit=stage_dali/cbit.name; shutil.copy2(source,staged_csv); shutil.copy2(confirmed,stage_dali/"sch_confirmed.json"); shutil.copy2(cbit,staged_cbit)
        adapter=stage/"scripts"/"schematic_parse"/"scripts"/"csv_schematic_adapter_v2.py"; cmd=[sys.executable,str(adapter),"--workspace",str(stage),"--project-config",str(stage/"project_config.json"),"--input",str(staged_csv),"--out-dir",str(stage_dali)]
        done=subprocess.run(cmd,cwd=stage,text=True,encoding="utf-8",errors="replace",capture_output=True)
        if done.returncode: raise RuntimeError("legacy parser failed:\n"+done.stdout+done.stderr)
        manifest=json.loads((stage_dali/"validation_manifest.json.txt").read_text(encoding="utf-8"))
        if manifest.get("status")!="PASS": raise RuntimeError("legacy parser did not pass")
        proof_cmd=[sys.executable,str(stage/"scripts"/"schematic_parse"/"scripts"/"csv_pathproof_v2.py"),"--input",str(staged_csv),"--cbit",str(staged_cbit),"--out-dir",str(stage_dali)]
        proof_run=subprocess.run(proof_cmd,cwd=stage,text=True,encoding="utf-8",errors="replace",capture_output=True)
        if proof_run.returncode: raise RuntimeError("path-proof generator failed:\n"+proof_run.stdout+proof_run.stderr)
        proof_data=json.loads((stage_dali/"path_proofs.json.txt").read_text(encoding="utf-8"))
        if proof_data.get("status")!="PASS": raise RuntimeError("path-proof generator did not pass")
        outputs={}
        for txt_name,json_name,kind in PAIRS:
            staged=stage_out/txt_name
            if not staged.is_file() or not staged.stat().st_size: raise RuntimeError(f"missing {txt_name}")
            txt=out/txt_name; shutil.copy2(staged,txt); outputs[txt_name]={"sha256":sha(txt),"bytes":txt.stat().st_size}; outputs[json_name]=make_json(txt,out/json_name,kind,reads)
        proof_data["schemaVersion"]=1; proof_data["artifactId"]="Path-Proofs"; proof_data["readSources"]=reads
        proof_data["input"]={"path":relative(source),"sha256":sha256_plaintext(source)}
        proof_data["cbit"]={"path":relative(cbit),"sha256":sha256_plaintext(cbit)}
        proof_json=out/PATH_PROOFS[1]; proof_json.write_text(json.dumps(proof_data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
        proof_txt=out/PATH_PROOFS[0]; shutil.copy2(stage_dali/"PATHPROOF-VALIDATION.txt",proof_txt)
        outputs[PATH_PROOFS[1]]={"sha256":sha(proof_json),"bytes":proof_json.stat().st_size,"status":proof_data["status"]}
        outputs[PATH_PROOFS[0]]={"sha256":sha(proof_txt),"bytes":proof_txt.stat().st_size,"status":proof_data["status"]}
        receipt={"schemaVersion":2,"generator":"scripts/generate_schematic_txt.py","parser":"scripts/schematic_parse/scripts/csv_schematic_adapter_v2.py","parserStatus":"PASS","readSources":reads,"outputs":outputs}
        (out/"schematic-receipt.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("SCHEMATIC TXT+JSON READY"); return 0
if __name__=="__main__": raise SystemExit(main())
