# -*- coding: utf-8 -*-
"""落实 schematic-expert ② 的建议：**门禁运行前，把该次运行的输入复制为字节快照**，

# ==== TOOL_RATIONALE_V1：本工具的价值说明 ====
# 1) **归属从"自述"升级为"字节可证"**：把该次门禁运行的输入（契约 / 候选 payload / 基线）
#    复制成字节快照并与门禁日志同放 ⇒ 将来若被质疑"那次到底读的是哪一版"，有字节可证；
#    对应 `build-report.contract.gateExpectationSet.residualCaveat` 里那句
#    "不能声称已用字节证明读的是 rev 32" —— 本工具把它变成"**下一次运行可字节证明**"。
# 2) **双哈希（`sha256` + `sha256_lf_normalized`）—— 关掉我们踩过的真坑**
#    （schematic-expert 指出，我方采纳并记此价值说明）：
#    我们查 `t28-anchors.json` 漂移时，一度靠 `11,609 + 245 = 11,854` 才发现
#    "size 差来自 CRLF vs LF" ⇒ **size 与普通 sha 都会把"行尾变化"误报成"内容变化"**。
#    同时记 **原始 sha + LF 归一化 sha** ⇒ 后来者可区分
#    **"内容变了"** 与 **"只是行尾变了"** ⇒ **快照对照不再被编辑器行尾设置污染**。
# 3) **不改任何脚本、不改门禁、不动基线**（纯 copy）⇒ 与 Captain "不改门禁脚本"的裁定相容。
# ==========================================================================

使"那次到底读的是哪一版"从**日志自述**变为**字节可证明**（纪律 #3 应用的"每次运行输入"）。

设计：
  · 目标目录 `backups/<task>-<timestamp>-gateinputs/`；
  · 复制：被读的 `setup-contract.json`、候选 payload、（若存在）`scripts/gate_baseline.json`；
  · 同时写 `manifest.json`：每项的 全路径/size/sha256/sha256_lf_normalized/at + 运行说明；
  · **不触碰任何脚本、不改门禁、不动基线**（纯 copy）。
用法：`python t54_snapshot_gate_inputs.py <task-tag> [--dry-run]`
"""
import datetime
import hashlib
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = os.path.abspath(os.path.join(HERE, '..'))
WS = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))


def sha(p):
    b = open(p, 'rb').read()
    return {'size': len(b),
            'sha256': hashlib.sha256(b).hexdigest(),
            'sha256_lf_normalized': hashlib.sha256(b.replace(b'\r\n', b'\n')).hexdigest()}


def main():
    task = sys.argv[1] if len(sys.argv) > 1 else 't54'
    dry = '--dry-run' in sys.argv
    ts = datetime.datetime.now().astimezone().strftime('%Y%m%d-%H%M%S')
    out = os.path.join(RUN, 'backups', '%s-%s-gateinputs' % (task, ts))

    items = [
        ('setup-contract.json', os.path.join(RUN, 'setup-contract.json'),
         '门禁读取的契约（rev-32 归属问题的关键输入）'),
        ('implementation-payload-TM600-TM601.cpp',
         os.path.join(RUN, 'implementation-payload-TM600-TM601.cpp'), '候选交付件'),
        ('gate_baseline.json', os.path.join(WS, 'scripts', 'gate_baseline.json'),
         '门禁基线（应始终为 28 B / cbit 豁免）'),
    ]
    man = {'task': task, 'at': datetime.datetime.now().astimezone().isoformat(timespec='seconds'),
           'purpose': ('把该次门禁运行的**输入**固化为字节快照 ⇒ 归属从"日志自述"升级为"字节可证"；'
                       '不改任何脚本、不改门禁、不动基线。'),
           'outDir': out, 'dryRun': dry, 'items': {}}
    for name, src, why in items:
        if not os.path.isfile(src):
            man['items'][name] = {'source': src, 'status': 'MISSING'}
            continue
        st = sha(src)
        man['items'][name] = {'source': src, 'why': why, 'status': 'ok', **st}
        if not dry:
            os.makedirs(out, exist_ok=True)
            shutil.copy2(src, os.path.join(out, name))
    if not dry:
        os.makedirs(out, exist_ok=True)
        io.open(os.path.join(out, 'manifest.json'), 'w', encoding='utf-8').write(
            json.dumps(man, ensure_ascii=False, indent=2))
    print('%s %s' % ('DRY-RUN:' if dry else 'SNAPSHOT:', out))
    for k, v in man['items'].items():
        print('  %-42s %-8s %s' % (k, v.get('status'), v.get('sha256', '')[:24]))
    return 0


if __name__ == '__main__':
    sys.exit(main())
