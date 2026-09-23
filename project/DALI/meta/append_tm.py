# -*- coding: utf-8 -*-
"""将 gen_tm000_102.cpp 的 7 个 TM 函数追加到 DALI test.cpp (保持 UTF-8 BOM + CRLF)"""
import io

GEN = r'D:\Newtest\CLAUDE_PROCESS\Project\DALI\meta\gen_tm000_102.cpp'
TGT = r'D:\PROJECT6-DALI\devel\source\test.cpp'

gen = io.open(GEN, encoding='utf-8').read()
# 统一行尾为 CRLF (test.cpp 是 CRLF 文件)
gen = gen.replace('\r\n', '\n').replace('\n', '\r\n')

data = io.open(TGT, encoding='utf-8-sig').read()
# 检查是否已有 TM 函数 (幂等保护)
if 'TM000_IQ_STANDBY' in data:
    print('[SKIP] test.cpp 已含 TM000_IQ_STANDBY, 未追加 (防重复)')
    raise SystemExit(0)

# 清理末尾, 追加
data = data.rstrip('\r\n \t')
data += '\r\n\r\n'
data += gen

# 写回 (utf-8-sig 自动加 BOM, newline='' 防换行重写)
io.open(TGT, 'w', encoding='utf-8-sig', newline='').write(data)
print('[OK] 已追加 7 个 TM 函数到 test.cpp')
print('    新文件大小: %d bytes' % io.open(TGT, 'rb').read().__len__())
