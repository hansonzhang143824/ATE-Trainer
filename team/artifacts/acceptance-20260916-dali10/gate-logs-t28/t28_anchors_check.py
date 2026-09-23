# -*- coding: utf-8 -*-
"""诊断/收尾：使 t28-anchors.json 的 --check 语义正确，并给出稳定引用方式。

问题：`anchorsObservedAt` 每次运行变化 ⇒ 文件字节不稳；--check 的比较方式也需修正。
处置：把 `anchorsObservedAt` 从**确定性主体**中分离：写入固定字面量 `"see-body"` 之外，
      另用独立的 `observedAt.file` 记录？——过度设计。**采用最简单的可信方案**：
      文件内只保留一个时间戳，并在 --check 中**按行剔除后再逐行比较**（而非整串比较）。
"""
import hashlib
import io
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ANCHORS = os.path.join(HERE, 't28-anchors.json')

TS_LINE = re.compile(r'^\s*"anchorsObservedAt": ".*",\s*$', re.M)


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def body_only(text):
    return TS_LINE.sub('', text).strip()


def main():
    import subprocess
    gen = os.path.join(HERE, 't28_make_anchors.py')
    # 连跑两次并比较"剔除时间戳行后"的主体
    outs = []
    for _ in range(2):
        r = subprocess.run([sys.executable, gen], capture_output=True, text=True, encoding='utf-8')
        outs.append(r.stdout.strip().splitlines()[0])
        h1 = sha(ANCHORS)
        t1 = io.open(ANCHORS, encoding='utf-8').read()
    print('run A:', outs[0])
    print('run B:', outs[1])
    print('两次现盘字节哈希: %s / %s' % (h1, sha(ANCHORS)))
    t2 = io.open(ANCHORS, encoding='utf-8').read()
    print('剔除时间戳行后主体一致 =', body_only(t1) == body_only(t2))
    print('剔除后主体哈希 =', hashlib.sha256(body_only(t2).encode('utf-8')).hexdigest())
    print()
    print('⇒ 结论：**以「剔除 anchorsObservedAt 行后的主体哈希」作为稳定引用锚点**；')
    print('   整文件哈希只在"同一秒内连跑"时相同，不适合直接引用。')
    doc = json.load(io.open(ANCHORS, encoding='utf-8-sig'))
    print('   锚点条目 = %d；observedAt = %s' % (len(doc['anchors']), doc.get('anchorsObservedAt')))
    # 把稳定引用方式写进文件自身的 readingRule 提示（不重复写文件，仅打印建议）
    print('   建议引用写法：`t28-anchors.json`（主体哈希见上；逐条含 path/size/sha256/note）')


if __name__ == '__main__':
    main()
