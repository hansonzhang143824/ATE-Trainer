# -*- coding: utf-8 -*-
"""清理 §2.1 表格中与被更正行矛盾/冗余的旧行（幂等）。"""
import hashlib
import io
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ATTR = os.path.join(HERE, 't33-revision-attribution.md')
OLD = '| TM600 段 `SW12_U1REF_BST_ACM.Set(` 调用 | 10（`FV 0/5/10/15/20` 与回落 `15/10/5`，全部 `ACM200_RELAY_ON`） |\n'
NEW = ('| TM600 段 `.Set` 的 FV 序列 | `0,5,10,15,20,15,10,5,0`（`ACM200_RELAY_ON`）→ 末次 `0`（`ACM200_RELAY_OFF`） |\n'
       '| TM601 段 `SW12_U1REF_BST_ACM` 引用 | 3（**全部**为 `.Set` 调用） |\n')


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


t = io.open(ATTR, encoding='utf-8-sig').read()
if OLD not in t:
    print('无需清理（幂等）: %d B / %s' % (os.path.getsize(ATTR), sha(ATTR)))
else:
    old2 = '| TM601 段 `SW12_U1REF_BST_ACM.Set(` 调用 | 3 |\n'
    t = t.replace(OLD, NEW, 1)
    if old2 in t:
        t = t.replace(old2, '', 1)
    io.open(ATTR, 'w', encoding='utf-8', newline='').write(t)
    print('已清理: %d B / %s' % (os.path.getsize(ATTR), sha(ATTR)))
