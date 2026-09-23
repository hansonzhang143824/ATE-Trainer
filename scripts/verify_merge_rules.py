# -*- coding: utf-8 -*-
# 合并纪律检查 — 核对 merge_log.md 与 merge_rules.md 的一致性
# 规则源: .claude/knowledge/standards/merge_rules.md (M001/M002/M003/M004)
# 用法: python verify_merge_rules.py [--strict]
#   --strict: merge_log.md 缺失时也报 M002 (默认缺失 = 无合并, PASS)

import io, re, os, sys

import proj_config

_CFG = proj_config.load(proj_config.config_from_argv(sys.argv))
PROJ = _CFG['_root']                                     # workspace 根 (跨项目知识)
RULES = os.path.join(PROJ, 'knowledge', 'standards', 'merge_rules.md')
LOG   = os.path.join(PROJ, 'merge_log.md')
AI    = os.path.join(_CFG['project_dir'], 'AI.cpp')      # 已废弃, 待随 AI.cpp 清理


def read_enc(path):
    """DLP 透明加密回退: utf-8-sig→utf-8→gbk→latin-1"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def strip_fenced(text):
    """剔除 ``` 代码围栏块 (格式示例不参与解析)"""
    out, in_fence = [], False
    for line in text.splitlines():
        if line.strip().startswith('```'):
            in_fence = not in_fence
            continue
        if not in_fence:
            out.append(line)
    return '\n'.join(out)


def parse_active_rules(text):
    """解析 merge_rules.md 表格, 返回 {rule_id: {'action':..., 'from_tm':set, 'status':...}}
    只认 状态=✅ 生效中 的 MR-0xx 行。格式: | MR-0xx | ... | ✅ 生效中 | 日期 |"""
    rules = {}
    for line in strip_fenced(text).splitlines():
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip().replace('**', '') for c in line.strip().strip('|').split('|')]
        if len(cells) < 4 or not re.fullmatch(r'MR-\d+', cells[0]):
            continue
        rid = cells[0]
        # 找状态列: 任一 cell 含 ✅/⛔
        status = None
        for c in cells[1:]:
            if '生效中' in c:
                status = 'active'
                break
            if '停用' in c:
                status = 'inactive'
                break
        rules[rid] = {'status': status, 'cells': cells}
    return rules


def parse_log_merges(text):
    """解析 merge_log.md 表格行: | 规则ID | 合并进 | 被合并 | 理由 | ... """
    rows = []
    for line in strip_fenced(text).splitlines():
        if not line.strip().startswith('|'):
            continue
        cells = [c.strip() for c in line.strip().strip('|').split('|')]
        if len(cells) < 3 or not re.fullmatch(r'MR-\d+', cells[0]):
            continue
        rows.append(cells)
    return rows


def parse_ai_functions(text):
    """AI.cpp 现有 DUT_API 函数 TM 号集合"""
    return set(int(m) for m in re.findall(r'DUT_API int TM(\d+)_\w+\(', text))


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    strict = '--strict' in sys.argv
    errors, warns = [], []

    rules_txt = read_enc(RULES)
    active = parse_active_rules(rules_txt)
    print(f'[rules] merge_rules.md 生效规则: {sorted(active.keys()) if active else "无"}')

    # 零合并判定: 只有 MR-000 且 active
    zero_merge = ('MR-000' in active and active['MR-000']['status'] == 'active'
                  and len(active) == 1)

    if not os.path.exists(LOG):
        if strict:
            errors.append('M002: merge_log.md 缺失')
        else:
            print('[log] merge_log.md 不存在 → 视为无合并, PASS (可用 --strict 强制要求文件存在)')
    else:
        log_txt = read_enc(LOG)
        rows = parse_log_merges(log_txt)
        if not rows:
            print('[log] merge_log.md 存在但无合并行, PASS')
        else:
            print(f'[log] merge_log.md 合并行: {len(rows)}')
            if zero_merge:
                for r in rows:
                    errors.append(f'M001: 零合并铁律生效中(MR-000), 但存在合并行 {r[0]}→{r[1]} (被合并 {r[2]})')
            else:
                ai_tms = parse_ai_functions(read_enc(AI)) if os.path.exists(AI) else set()
                for r in rows:
                    rid, into, merged = r[0], r[1], r[2]
                    # M003: 规则引用错误
                    if rid not in active or active[rid]['status'] != 'active':
                        errors.append(f'M003: 规则 {rid} 不存在或未生效 (行: {line_of(rows, r)})')
                    # 自合并
                    if into == merged:
                        errors.append(f'M003: 自合并 {rid}: 合并进==被合并 ({into})')
                    # M004: 被合并 TM 仍存在独立函数
                    for tm in re.findall(r'TM(\d+)', merged):
                        n = int(tm)
                        if n in ai_tms:
                            warns.append(f'M004: 被合并 TM{n} 在 AI.cpp 仍存在独立函数 (规则 {rid})')

    print()
    if warns:
        print('WARNINGS:')
        for w in warns:
            print('  -', w)
    if errors:
        print('*** FAIL ***')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('MERGE DISCIPLINE PASSED')


def line_of(rows, target):
    return rows.index(target) + 1


if __name__ == '__main__':
    main()
