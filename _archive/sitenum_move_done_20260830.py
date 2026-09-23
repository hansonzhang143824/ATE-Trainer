# -*- coding: utf-8 -*-
# _sitenum_move.py — SITE_NUM 唯一定义迁移: treg.h:49 → StdAfx.h (2026-08-30 用户批准)
# 前置: D:/PROJECT6-DALI/devel/source/_backup_sitenum_20260830/ 已有 StdAfx.h.bak + treg.h.bak
# 回滚: 用 _sitenum_rollback.py
import hashlib

src = 'D:/PROJECT6-DALI/devel/source'
ws  = 'D:/Newtest/CLAUDE_PROCESS/Library-Functions/treg/treg.h'

# --- 1) StdAfx.h: L22 后插入 SITE_NUM 定义 ---
p = src + '/StdAfx.h'
d = open(p, 'rb').read()
anchor = b'using namespace std;\r\n'
assert d.count(anchor) == 1, 'StdAfx.h anchor not unique'
ins = b'#define SITE_NUM 12  // SITE_NUM sole authority (moved from treg.h 2026-08-30)\r\n'
d2 = d.replace(anchor, anchor + ins, 1)
open(p, 'wb').write(d2)
print('StdAfx.h edited:', len(d2), 'bytes md5=' + hashlib.md5(d2).hexdigest()[:12])

# --- 2) treg.h: 注释 L49 ---
p = src + '/treg.h'
t = open(p, 'rb').read()
old = b'#define SITE_NUM 12\r\n'
assert t.count(old) == 1, 'treg.h target not unique'
new = b'//#define SITE_NUM 12  // authority moved to StdAfx.h (2026-08-30)\r\n'
t2 = t.replace(old, new, 1)
open(p, 'wb').write(t2)
print('treg.h edited:', len(t2), 'bytes md5=' + hashlib.md5(t2).hexdigest()[:12])

# --- 3) 工作区 treg.h 同步 ---
open(ws, 'wb').write(t2)
w = open(ws, 'rb').read()
print('workspace treg.h == project treg.h:', w == t2)

# --- 4) 复核 ---
d3 = open(src + '/StdAfx.h', 'rb').read()
for i, line in enumerate(d3.split(b'\n'), 1):
    if 20 <= i <= 28:
        print('  StdAfx.h L%d: %s' % (i, line.decode()[:95]))
t3 = open(src + '/treg.h', 'rb').read()
for i, line in enumerate(t3.split(b'\n'), 1):
    if i == 49:
        print('  treg.h L49: %s' % line.decode()[:95])
print('StdAfx.h active define:', b'#define SITE_NUM 12' in d3)
print('treg.h active define count:', t3.count(b'#define SITE_NUM'))
print('spec.h still commented:', b'//#define SITE_NUM 12' in open(src + '/spec.h', 'rb').read())
print()
print('=== EDITS DONE. next: run fast_rebuild.ps1 ===')
