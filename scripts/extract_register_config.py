#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
FIELD=re.compile(r"field\[([^]]+)\]",re.I)
ITEM=re.compile(r"Test Item:\s*(TM\d+)\b",re.I)
WRITE=re.compile(r"I2CWriteSameData\s*\(\s*DEV_ADDR\s*,\s*0x[0-9A-Fa-f]+\s*,\s*0x[0-9A-Fa-f]+\s*\)")
def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("--tm",required=True); p.add_argument("--manifest",required=True); p.add_argument("--out",required=True); a=p.parse_args()
 tm=a.tm.upper(); manifest=json.loads(Path(a.manifest).read_text(encoding="utf-8"))
 dft_path=Path(manifest["materialRoots"]["output"])/"dft"/tm/"dft-meta.json"
 dft=json.loads(dft_path.read_text(encoding="utf-8")); fields=FIELD.findall(str((dft.get("rawIntent") or {}).get("Code2") or ""))
 if not fields: raise SystemExit(tm+": DFT Code2 has no field declaration")
 source=ROOT/"project"/"DALI"/"reg_config"/(tm.lower()+".sv")
 if not source.is_file(): raise SystemExit(tm+": register configuration is missing")
 text=source.read_text(encoding="utf-8"); item=ITEM.search(text)
 if not item or item.group(1).upper()!=tm: raise SystemExit(tm+": source Test Item does not match")
 if any(field not in FIELD.findall(text) for field in fields): raise SystemExit(tm+": DFT field declaration is not present in source")
 start=text.find("entertestmode()")
 if start<0: raise SystemExit(tm+": source has no entertestmode")
 lines=[]
 for number,line in enumerate(text[start:].splitlines(),text[:start].count("\n")+1):
  if WRITE.search(line): lines.append({"sourceLine":number,"sourceText":line,"address":re.search(r"0x[0-9A-Fa-f]+",line).group(0).upper(),"value":re.findall(r"0x[0-9A-Fa-f]+",line)[1].upper()})
 if not lines: raise SystemExit(tm+": source has no I2C writes after entertestmode")
 out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
 result={"schemaVersion":1,"tm":tm,"status":"verified","source":{"path":"project/DALI/reg_config/"+tm.lower()+".sv","sha256":digest(source),"testItem":tm},"dftBinding":{"path":str(dft_path),"code2Fields":fields,"verifiedAgainstDftCode2":True},"orderedWrites":lines,"implementation":{"renderer":"scripts/render_register_writes.py","rule":"Copy sourceText verbatim in order after signed entertestmode()."}}
 out.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8"); print(json.dumps({"status":"PASS","tm":tm,"writes":len(lines),"out":str(out)},ensure_ascii=False))
if __name__=="__main__": main()
