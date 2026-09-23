# -*- coding: utf-8 -*-
# TM641 追加编码修复: test.cpp 原文件 = UTF-8 BOM; 之前误按 GBK 追加 → 回退到追加前字节并按 UTF-8 重写
p = r'D:\PROJECT6-DALI\devel\source\test.cpp'
b = open(p, 'rb').read()
orig = b[:354750]  # 追加前原始大小 (含结尾 CRLF)
try:
    orig.decode('utf-8-sig')
    print('orig utf-8-sig OK, size', len(orig))
except Exception as e:
    print('orig decode FAIL:', e)
    raise SystemExit(1)

blk = open(r'D:\Newtest\CLAUDE_PROCESS\_archive\tm641_block.txt', 'rb').read().decode('utf-8')
blk = blk.replace('\r\n', '\n').replace('\n', '\r\n')
newb = orig + blk.encode('utf-8')
open(p, 'wb').write(newb)

b2 = open(p, 'rb').read()
b2.decode('utf-8-sig')  # 全文件必须干净解码
assert b2.count(b'TM641_BST_UV') == 1
print('rewritten UTF-8, size', len(b2), 'TM641 count', b2.count(b'TM641_BST_UV'), 'whole-file utf-8-sig decode OK')
