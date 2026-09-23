# -*- coding: utf-8 -*-
# _sitenum_rollback.py — 从备份恢复 StdAfx.h / treg.h + 同步工作区 treg.h
import hashlib

src = 'D:/PROJECT6-DALI/devel/source'
bak = src + '/_backup_sitenum_20260830'
ws  = 'D:/Newtest/CLAUDE_PROCESS/Library-Functions/treg/treg.h'

for fn in ['StdAfx.h', 'treg.h']:
    d = open(bak + '/' + fn + '.bak', 'rb').read()
    open(src + '/' + fn, 'wb').write(d)
    print('restored', fn, len(d), 'bytes md5=' + hashlib.md5(d).hexdigest()[:12])

# 工作区 treg.h 同步为工程原始版
t = open(src + '/treg.h', 'rb').read()
open(ws, 'wb').write(t)
print('workspace treg.h == project treg.h:', open(ws, 'rb').read() == t)

# 复核原始状态
d = open(src + '/StdAfx.h', 'rb').read()
t = open(src + '/treg.h', 'rb').read()
print('StdAfx.h no define (original):', b'#define SITE_NUM' not in d)
print('treg.h L49 active define (original):', b'\r\n#define SITE_NUM 12\r\n' in t)
print('=== ROLLBACK DONE ===')
