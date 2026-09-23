#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从旧会话 transcript 中恢复 StdAfx.h 原始内容 (Read tool result)."""
import json
import re

TRANSCRIPT = r"C:\Users\nvt10241\.claude\projects\C--Users-nvt10241\66ce802c-bcf6-4d0b-b6f2-6900e4ae087e.jsonl"
TARGET = r"D:\PROJECT6-DALI\devel\source\StdAfx.h"
OUT = r"D:\Newtest\CLAUDE_PROCESS\Project\DALI\input\recover_stdafx.h.txt"

tool_uses = {}  # tool_use_id -> {"path":..., "block": idx}
tool_results = {}  # tool_use_id -> text
with open(TRANSCRIPT, "rb") as f:
    data = f.read().decode("utf-8", errors="replace")

for i, ln in enumerate(data.splitlines()):
    try:
        rec = json.loads(ln)
    except Exception:
        continue
    msg = rec.get("message") or {}
    content = msg.get("content")
    if not isinstance(content, list):
        continue
    for block in content:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "tool_use":
            if block.get("name") == "Read" and TARGET in str(block.get("input", {}).get("file_path", "")):
                tool_uses[block.get("id")] = {"path": block["input"]["file_path"], "block": i}
        elif block.get("type") == "tool_result":
            tuid = block.get("tool_use_id")
            if tuid in tool_uses:
                c = block.get("content")
                if isinstance(c, list):
                    text = "\n".join(x.get("text", "") for x in c if isinstance(x, dict) and "text" in x)
                else:
                    text = str(c)
                tool_results[tuid] = text

print("StdAfx.h Read tool_use blocks:", len(tool_uses))
print("matching tool_results:", len(tool_results))

best = None
for tuid, meta in tool_uses.items():
    if tuid in tool_results:
        txt = tool_results[tuid]
        # cat -n format: lines like "1\t#..."; prefer the block containing the guard
        if "AFX_STDAFX_H__" in txt or "K46_BUS0_FH_SW1" in txt:
            best = (tuid, txt, meta)
            print("FOUND block with content at line", meta["block"], "id", tuid[:8])

if best is None and tool_results:
    best = (next(iter(tool_results)), tool_results[next(iter(tool_results))],
            tool_uses[next(iter(tool_results))])

if best is None:
    print("NO CONTENT FOUND")
    raise SystemExit(1)

tuid, txt, meta = best
# strip cat -n line-number prefix "N\t"
lines = []
for raw in txt.splitlines():
    m = re.match(r"^\s*\d+\t(.*)$", raw)
    if m:
        lines.append(m.group(1))
    else:
        lines.append(raw)
# skip trailing empty from output wrappers
while lines and not lines[-1].strip():
    lines.pop()
content = "\n".join(lines) + "\n"
with open(OUT, "wb") as f:
    f.write(content.encode("utf-8"))
print("WROTE %d lines -> %s" % (len(lines), OUT))
print("HEAD:")
print("\n".join(lines[:5]))
print("TAIL:")
print("\n".join(lines[-3:]))
