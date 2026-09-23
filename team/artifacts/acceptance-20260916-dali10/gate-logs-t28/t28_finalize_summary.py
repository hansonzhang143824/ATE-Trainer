# -*- coding: utf-8 -*-
"""t28-summary.md §8 定稿（幂等）：先把已存在的定稿段整体剥离，再按需追加一次。

用法: python t28_finalize_summary.py [--check]
"""
import hashlib
import io
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
P = os.path.join(HERE, 't28-summary.md')
MARK = '**定稿说明（本节自身也漂移过，故不写本文件自身哈希）**'
LEGACY = re.compile(r'\n\*\*(?:最终值（本节自身也漂移一次）|定稿说明[^\n]*)\*\*.*\Z', re.S)

BLOCK = (
    '\n\n' + MARK + '：本文件在加入 §8 后还改动过两次（恢复一行被误删、写入本说明）。'
    '为避免自指悖论，**本节不收录本文件自身的哈希**——引用本文件请**现算**'
    '（本工作区源受 DLP 保护，必须用 python 以 rb 读后取 sha256；不要用 pwsh 文本工具）。\n'
    '**需要稳定锚点时请引用本批交付的“证据文件”**（自交付后未被再编辑）：\n'
    '- `t28-red-proof.json` = 5,351 B / `b97441a457119ca0ca11dca2b55a69e302c06cc6cb0b378f663bc77d4d78c529`\n'
    '- `redproof-after-fix.log` = 6,377 B / `6a17726003afaa6e6470c20e7e94ea18477e96c6590d76ad906e1970c3aae7e2`\n'
    '- `redproof-before-fix.log` = 1,317 B / `c0bfc972d34b4491…`（完整值现算）\n'
    '- `check_input_sync.py`（被审脚本）= 17,455 B / `e804c459b2d3088e72d455eb9e1b7893119cea47ad0a640735b6f5db42d784d1`\n'
    '- `gate_baseline.json`（未改）= 28 B / `021015da84e6fd4c54a595796e1bad73e18c57db94f856871d5667044302cb1d`\n'
)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def main():
    t = io.open(P, encoding='utf-8-sig').read()
    stripped = LEGACY.sub('\n', t).rstrip()          # 先剥离所有历史定稿段（幂等的关键）
    times = t.count(MARK)
    if '--check' in sys.argv:
        print('现盘 %d B / %s' % (os.path.getsize(P), sha(P)))
        print('  历史定稿段出现次数 = %d（>1 说明曾经重复追加）' % times)
        return
    io.open(P, 'w', encoding='utf-8', newline='').write(stripped + BLOCK)
    s = io.open(P, encoding='utf-8-sig').read()
    print('FINAL %d B / %s' % (os.path.getsize(P), sha(P)))
    print('  定稿段出现次数 = %d（应为 1）' % s.count(MARK))
    print('  五个稳定锚点齐备 = %s' % all(k in s for k in
          ('b97441a457119ca0', '6a17726003afaa6e', 'c0bfc972', 'e804c459b2d3088e', '021015da84e6fd4c')))


if __name__ == '__main__':
    main()
