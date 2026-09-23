#!/usr/bin/env python3
"""One-command bounded incremental build for current PTC code."""
from __future__ import annotations
import argparse,hashlib,json,subprocess,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def main():
 p=argparse.ArgumentParser(); p.add_argument("--project",required=True); p.add_argument("--source",required=True); p.add_argument("--report",required=True); p.add_argument("--timeout-seconds",type=float,default=10.0); p.add_argument("--config",default="Both"); a=p.parse_args()
 started=time.perf_counter(); report={"stage":"COMPILE","mode":"incremental","timeoutSeconds":a.timeout_seconds,"source":a.source}
 command=["powershell","-NoProfile","-ExecutionPolicy","Bypass","-File",str(ROOT/"scripts"/"fast_rebuild.ps1"),a.project,"-Config",a.config,"-Incremental"]
 try:
  run=subprocess.run(command,capture_output=True,timeout=a.timeout_seconds)
  report.update(exitCode=run.returncode,elapsedSeconds=round(time.perf_counter()-started,3),stdout=(run.stdout or b'').decode('utf-8',errors='replace')[-12000:],stderr=(run.stderr or b'').decode('utf-8',errors='replace')[-4000:],sourceSha256=sha(Path(a.source)))
 except subprocess.TimeoutExpired as exc:
  report.update(exitCode=124,elapsedSeconds=round(time.perf_counter()-started,3),timeout=True,stdout=(exc.stdout or b'').decode('utf-8',errors='replace')[-12000:],stderr=(exc.stderr or b'').decode('utf-8',errors='replace')[-4000:],sourceSha256=sha(Path(a.source)))
 out=Path(a.report); out.parent.mkdir(parents=True,exist_ok=True); out.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
 print(json.dumps({k:report.get(k) for k in ["exitCode","elapsedSeconds","timeout","sourceSha256"]},ensure_ascii=False))
 raise SystemExit(0 if report["exitCode"]==0 else report["exitCode"])
if __name__=="__main__": main()
