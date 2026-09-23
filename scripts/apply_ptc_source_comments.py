#!/usr/bin/env python3
"""Apply fixed PTC maintenance comments from signed trial contracts."""
from __future__ import annotations
import argparse,json,re
from pathlib import Path
def body_end(text,start):
 open_at=text.find("{",start); depth=1; i=open_at+1
 while i<len(text) and depth:
  if text[i]=="{": depth+=1
  elif text[i]=="}": depth-=1
  i+=1
 return i
def main():
 p=argparse.ArgumentParser(); p.add_argument("--trial",required=True); p.add_argument("--source",required=True); p.add_argument("--dry-run",action="store_true"); a=p.parse_args()
 trial=Path(a.trial); impl=json.loads((trial/"implementation"/"implementation-manifest.json").read_text(encoding="utf-8"))
 method=json.loads(next((trial/"method").glob("*-test-method-contract.json")).read_text(encoding="utf-8"))
 strategy=json.loads(next((trial/"strategy").glob("*-resource-config-contract.json")).read_text(encoding="utf-8"))
 evidence=json.loads((trial/"strategy"/"register-config-evidence.json").read_text(encoding="utf-8"))
 source=Path(a.source); text=source.read_text(encoding="utf-8")
 symbol=(impl.get("changes") or [{}])[0].get("symbols",[None])[0]
 if not symbol: raise SystemExit("implementation manifest has no symbol")
 match=re.search(r"DUT_API\s+int\s+"+re.escape(symbol)+r"\s*\(",text)
 if not match: raise SystemExit("signed function is absent from source")
 tables=(method.get("resourceBoundary") or {}).get("sourceTablesByEndpoint") or {}
 sweeps=(method.get("measurementPlan") or {}).get("sweeps") or []
 sweep=sweeps[0] if sweeps else {}
 pin=sweep.get("rampPin","DYNAMIC"); low=sweep.get("startV","?"); high=sweep.get("stopV","?")
 monitor=(method.get("resourceBoundary") or {}).get("monitorPhysicalPin","monitor")
 relays=(strategy.get("setOnClosure") or {}).get("relays") or []
 fields=(evidence.get("dftBinding") or {}).get("code2Fields") or []
 loop=" + ".join(tables.values())
 header=("// [PTC-AUTO] "+method.get("tm","TM")+": "+symbol+"\n"
         "// [PTC-AUTO] DFT: en_tm[] -> field["+("; ".join(fields))+"] -> "+pin+" "+str(low)+"->"+str(high)+"V scan\n"
         "// [PTC-AUTO] Monitor: V(DTEST0)="+monitor+"; relay closure="+str(relays)+"\n"
         "// [PTC-AUTO] Loop: "+loop+"\n")
 # Replace only a previous generated header; otherwise insert one immediately before the function.
 hstart=text.rfind("// [PTC-AUTO]",0,match.start())
 if hstart>=0 and text[hstart:match.start()].count("\n")<=5:
  text=text[:hstart]+header+text[match.start():]
 else:
  text=text[:match.start()]+header+text[match.start():]
 match=re.search(r"DUT_API\s+int\s+"+re.escape(symbol)+r"\s*\(",text); end=body_end(text,match.start()); block=text[match.start():end]
 inverse={table:endpoint for endpoint,table in tables.items()}
 for table,endpoint in inverse.items():
  pattern=r"(?m)^(\s*)("+re.escape(table)+r"\.Set\(FV,\s*([0-9.]+))"
  def annotate(m):
   prior=block[max(0,m.start()-120):m.start()]
   if "[PTC-AUTO] "+endpoint+"=" in prior: return m.group(0)
   value=m.group(3); purpose="zero before relay release" if float(value)==0 else "signed source power"
   return m.group(1)+"// [PTC-AUTO] "+endpoint+"="+value+"V via "+table+": "+purpose+".\n"+m.group(0)
  block=re.sub(pattern,annotate,block)
 ramp_table=(method.get("measurementPlan") or {}).get("rampSourceTable")
 if ramp_table:
  pattern=r"(?m)^(\s*)(test_method\.rampv_capv\()"
  index=0
  def ramp_note(m):
   nonlocal index
   prior=block[max(0,m.start()-180):m.start()]
   if "[PTC-AUTO] "+pin+"=" in prior: return m.group(0)
   direction=(str(low)+"V -> "+str(high)+"V") if index==0 else (str(high)+"V -> "+str(low)+"V")
   index+=1
   return m.group(1)+"// [PTC-AUTO] "+pin+"="+direction+" via "+ramp_table+": signed scan.\n"+m.group(0)
  block=re.sub(pattern,ramp_note,block)
 text=text[:match.start()]+block+text[end:]
 if a.dry_run: print(json.dumps({"status":"DRY_RUN","symbol":symbol,"sourceTables":tables,"sweeps":sweeps},ensure_ascii=False,indent=2))
 else: source.write_text(text,encoding="utf-8"); print(json.dumps({"status":"APPLIED","symbol":symbol},ensure_ascii=False))
if __name__=="__main__": main()
