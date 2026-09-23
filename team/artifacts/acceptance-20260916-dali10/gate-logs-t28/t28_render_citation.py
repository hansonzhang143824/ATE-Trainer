# -*- coding: utf-8 -*-
"""从 t28-anchors.json 生成"最终引用通告"文本（消息里不出现任何手抄哈希）。

用法: python t28_render_citation.py
输出: .agent-teams 之外的普通文本文件 + stdout（供复制进消息；哈希均由本脚本从 JSON 读入）
"""
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
ANCHORS = os.path.join(HERE, 't28-anchors.json')

doc = json.load(io.open(ANCHORS, encoding='utf-8-sig'))
lines = []
lines.append('【最终引用通告（本段由脚本从 t28-anchors.json 直接渲染，无任何人工转录）】')
lines.append('')
lines.append('① 作废声明：我在此前两条消息里对哈希的字面引用**全部作废**（我两次手抄都出错，'
             '其中一次甚至在"更正"里又抄了同一个错值）。**请勿以我的消息文本作为哈希来源。**')
lines.append('')
lines.append('② 唯一真源：`team/artifacts/acceptance-20260916-dali10/gate-logs-t28/t28-anchors.json`')
lines.append('   （%d 条锚点，每条 = path / size / sha256 / readAt / note；生成时刻 %s）'
             % (len(doc['anchors']), doc['generatedAt']))
lines.append('   读取方式：python 一行现算 —— `hashlib.sha256(open(path,"rb").read()).hexdigest()`')
lines.append('   （本工作区源受 DLP 保护，**必须用 python 读**，不得用 pwsh 文本工具。）')
lines.append('')
lines.append('③ 本节按你复核所需列出条目（**哈希由脚本直读，可逐条与现算比对**）：')
lines.append('')
for a in doc['anchors']:
    if a.get('missing'):
        lines.append('- MISSING  %s (%s)' % (a['label'], a['path']))
        continue
    lines.append('- %-20s %-46s %8d B' % (a['label'], a['path'], a['size']))
    lines.append('    sha256 = %s' % a['sha256'])
    if '报告类文档' in (a.get('note') or '') or 'summ' in a['path']:
        lines.append('    ⚠️ 报告类文档：会随作者更正漂移 ⇒ 引用请**现算 + 标时刻**')
lines.append('')
lines.append('④ 制度性止损（写入 t28-summary.md §8 漂移登记）：')
lines.append('   1) 我不再在消息里手抄任何长哈希；需要引用时只给「路径 + size」，请你从本 JSON 读取或一行 python 现算；')
lines.append('   2) 一切读取/哈希一律用 python（DLP 保护），不用 pwsh 文本工具；')
lines.append('   3) 写文档的脚本必须证明幂等（我这次的"定稿脚本"第一版非幂等，两次运行产生两个哈希，已修并连跑三次验证稳定）。')
lines.append('')
lines.append('⑤ 结论不变：t28 / t30 均已被你 ACCEPT；我不再改任何被审文件；'
             'R1 修法倾向 (ii) 且须 Captain 另开任务；reviewStatus 的 t24 部分撤回登记保留；'
             'B-6 三例我已全文采纳。边界：无电性结论；未做机台验证；编译成功 ≠ 电性正确。')

txt = '\n'.join(lines) + '\n'
out = os.path.join(HERE, 't28-citation-notice.txt')
io.open(out, 'w', encoding='utf-8').write(txt)
print(txt)
print('WROTE', out)
