#!/usr/bin/env python3
"""Validate the declared vset target for one DFT item using plaintext Python I/O."""
from __future__ import annotations
import argparse,csv,re,sys
from pathlib import Path

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',required=True); ap.add_argument('--tm',required=True); ap.add_argument('--expected-pin',required=True); a=ap.parse_args()
 with Path(a.source).open('r',encoding='utf-8-sig',newline='') as f: rows=[r for r in csv.DictReader(f) if r.get('Item','').upper()==a.tm.upper()]
 if len(rows)!=1: print(f'BLOCKED: expected 1 row, found {len(rows)}'); return 2
 tokens=re.findall(r'\bvset\[([^,\]]+)',rows[0].get('Dynamic',''),flags=re.I)
 if not tokens: print(f'BLOCKED: no Dynamic vset target for {a.tm.upper()}'); return 2
 wrong=[x for x in tokens if x.lower()!=a.expected_pin.lower()]
 if wrong: print(f'BLOCKED: {a.tm.upper()} Dynamic targets={tokens}; expected={a.expected_pin}'); return 2
 print(f'PASS: {a.tm.upper()} Dynamic targets={tokens}; expected={a.expected_pin}; count={len(tokens)}'); return 0
if __name__=='__main__': raise SystemExit(main())