#!/usr/bin/env python3
from __future__ import annotations
import argparse,json
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument("--evidence",required=True); p.add_argument("--out",required=True); a=p.parse_args()
 d=json.loads(Path(a.evidence).read_text(encoding="utf-8"))
 if d.get("status")!="verified" or not d.get("dftBinding",{}).get("verifiedAgainstDftCode2"): raise SystemExit("register evidence is not verified")
 rows=d.get("orderedWrites") or []
 if not rows or not all(isinstance(x.get("sourceText"),str) and "I2CWriteSameData" in x["sourceText"] for x in rows): raise SystemExit("verified verbatim register lines are missing")
 out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True); out.write_text("\n".join(x["sourceText"] for x in rows)+"\n",encoding="utf-8"); print(json.dumps({"status":"PASS","tm":d.get("tm"),"out":str(out),"copiedWrites":len(rows)},ensure_ascii=False))
if __name__=="__main__": main()
