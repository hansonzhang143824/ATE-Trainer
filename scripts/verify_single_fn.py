# -*- coding: utf-8 -*-
# verify_single_fn.py — 单函数冒烟自检（步骤 14 第一层）
# 职责: 一个测试函数生成后立即自检, 秒级、无需编译; 对应 B-001「先单函数冒烟」。
# 规则源: .claude/knowledge/standards/verification.md + rules-registry B-001 + framework.md
# 用法:
#   python verify_single_fn.py [--src <test.cpp>] [--fn <TMxxx>]
#   --src: 默认 project_config.json 的 vs_src_dir/test.cpp
#   --fn:  可选, 只检查指定函数 (默认全部)
# 判定: 任一 FAIL → exit 1; 全部通过 → exit 0
#
# 检查项 (7 项):
#   1 placeholder_residual      __X__ 残留 (batch 占位符, B-001)
#   2 semicolon_before_comment  分号在尾随注释后 (C2143 风险, B-001)
#   3 brace_balance             花括号配平 (B-001)
#   4 crlf_clean                CRLF 字节干净, 无 \r\r (DLP 字节模式, B-001)
#   5 six_step_complete         <%X%> 模板占位符残留
#   6 lifecycle_semantics       Step1~6 有序 + 每阶段有行为证据
#   7 register_unlock_order     有 I2C 写时 entertestmode 必须先执行

import json, re, os, sys

import proj_config

BATCH_PLACEHOLDER_RE = re.compile(r'__[A-Z][A-Z0-9_]*__')   # batch 占位符 __CONNECT__ 等
TPL_PLACEHOLDER_RE   = re.compile(r'<%[A-Z][A-Z0-9_]*%>')    # 模板占位符 <%RELAY_CODE%> 等
# C++ 预定义宏 (双下划线, 非占位符, 白名单避免误报)
SAFE_MACROS = {'__FILE__', '__LINE__', '__FUNCTION__', '__PRETTY_FUNCTION__'}


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


def split_functions(text):
    """按花括号提取 DUT_API TM 函数，兼容 TM000 和 TM000_NAME。"""
    header = re.compile(r'\bDUT_API\s+int\s+(TM\d+(?:_\w+)?)\s*\(')
    for match in header.finditer(text):
        brace = text.find('{', match.end())
        if brace < 0:
            yield match.group(1), text[match.start():]
            continue
        depth = 0
        end = None
        for pos in range(brace, len(text)):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    end = pos + 1
                    break
        yield match.group(1), text[match.start():end]


def _strip_comments_and_strings(text):
    """去掉注释/字符串, 供花括号配平用"""
    text = re.sub(r'//[^\n]*', '', text)                 # 行注释
    text = re.sub(r'/\*.*?\*/', '', text, flags=re.S)    # 块注释
    text = re.sub(r'"(?:\\.|[^"\\])*"', '""', text)      # 字符串字面量
    return text


def _first_match(body, patterns, start=0):
    positions = []
    for pattern in patterns:
        match = re.search(pattern, body[start:], flags=re.I | re.S)
        if match:
            positions.append(start + match.start())
    return min(positions) if positions else -1


def has_waiver(waivers, rule_id, function_name):
    for waiver in (waivers or {}).get('waivers', []):
        if waiver.get('status') != 'active' or waiver.get('rule_id') != rule_id:
            continue
        if (waiver.get('scope') or {}).get('function') == function_name:
            return True
    return False


def check_lifecycle(name, body, errors, waivers=None):
    """用阶段标记 + 行为证据验证六阶段，避免"只有注释/占位符消失"的假 PASS。"""
    trim_execute = _first_match(body, [r'(?:\.|->)\s*execute\s*\('])
    markers = []
    for step in range(1, 7):
        match = re.search(r'\bStep\s*%d\b' % step, body, flags=re.I)
        if not match:
            # TREG execute 内部完成测量与日志，trim 函数允许无独立 Step 6。
            if not (step == 6 and trim_execute >= 0):
                errors.append('%s: 缺少 Step %d 阶段标记' % (name, step))
            markers.append(-1)
        else:
            markers.append(match.start())
    present = [pos for pos in markers if pos >= 0]
    if len(present) == 6 and present != sorted(present):
        errors.append('%s: Step 1~6 阶段顺序错误' % name)

    relay = _first_match(body, [r'\bcbite\s*\.\s*SetOn\s*\('])
    power_on = _first_match(body, [r'\.\s*Set\s*\(', r'\bpower_on\s*\('])
    register_write = _first_match(body, [r'\bI2CWrite\w*\s*\(', r'\bwrite_byte\s*\('])
    enter_test = _first_match(body, [r'\bentertestmode\s*\('])
    measure = _first_match(body, [
        r'\.\s*MeasureVI\s*\(', r'\.\s*GetMeasResult\s*\(',
        r'\bMeasureFrequency\s*\(', r'\bramp[vi]_cap[vi]\s*\(',
        r'\bmeasure_[A-Za-z0-9_]+\s*\(', r'(?:\.|->)\s*execute\s*\(',
    ])
    log_result = trim_execute if trim_execute >= 0 else _first_match(
        body, [r'(?:\.|->)\s*SetTestResult\s*\(']
    )
    power_off = _first_match(body, [
        r'\bpower_off\s*\(',
        r'\.\s*Set\s*\(\s*(?:FV|FI)\s*,\s*(?:0(?:\.0*)?|0[eE][+-]?\d+)',
        r'\.\s*Set\s*\([^;]*\bRELAY_OFF\b',
    ], start=max(measure, 0))

    evidence = (
        ('Step 1 relay', relay), ('Step 2 power-on', power_on),
        ('Step 4 measure', measure), ('Step 5 power-off', power_off),
        ('Step 6 log', log_result),
    )
    for label, position in evidence:
        if position < 0:
            errors.append('%s: %s 无行为证据' % (name, label))

    # 普通函数日志在下电后；trim 的 execute 同时承担测量/日志，之后才下电。
    ordered = ([relay, power_on, measure, power_off] if trim_execute >= 0 else
               [relay, power_on, measure, power_off, log_result])
    if all(pos >= 0 for pos in ordered) and ordered != sorted(ordered):
        errors.append('%s: relay→power→measure→power-off→log 行为顺序错误' % name)

    if register_write >= 0:
        if enter_test < 0:
            if not has_waiver(waivers, 'R034', name):
                errors.append('%s: 有寄存器写但缺少 entertestmode()' % name)
        elif enter_test > register_write:
            errors.append('%s: entertestmode() 位于首次寄存器写之后' % name)
        elif power_on >= 0 and enter_test < power_on:
            errors.append('%s: entertestmode() 位于本次上电之前' % name)


def check_func(name, body, errors, syntax_only=False, waivers=None):
    # 1. placeholder_residual: __X__ 残留
    resid = sorted({m for m in BATCH_PLACEHOLDER_RE.findall(body) if m not in SAFE_MACROS})
    if resid:
        errors.append(f'{name}: 占位符残留 {resid} (B-001, 生成未替换完)')

    # 2. semicolon_before_comment: 分号在尾随注释后 (C2143)
    for i, line in enumerate(body.split('\n'), 1):
        idx = line.find('//')
        if idx < 0:
            continue
        before, after = line[:idx], line[idx:]
        if not before.strip() or before.strip() in ('{', '}'):
            continue
        if ';' in after and ';' not in before:
            errors.append(f'{name}: 第{i}行 分号在注释之后 (C2143 风险): {line.strip()[:80]}')

    # 3. brace_balance: 花括号配平
    stripped = _strip_comments_and_strings(body)
    o, c = stripped.count('{'), stripped.count('}')
    if o != c:
        errors.append(f'{name}: 花括号不配平 ({{={o} }}={c})')

    # 5. six_step_complete: <%X%> 模板占位符残留
    tpl = sorted(set(TPL_PLACEHOLDER_RE.findall(body)))
    if tpl:
        errors.append(f'{name}: 模板占位符未替换 {tpl} (6步结构不完整)')
    if not syntax_only:
        check_lifecycle(name, body, errors, waivers=waivers)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    args = sys.argv[1:]
    cfg = proj_config.load(proj_config.config_from_argv(args))
    src = cfg['derived']['test_cpp']
    fn_filter = None
    syntax_only = '--syntax-only' in args
    waiver_path = cfg.get('intermediates', {}).get('waivers', '')
    if '--src' in args:
        i = args.index('--src')
        if i + 1 < len(args):
            src = args[i + 1]
    if '--fn' in args:
        i = args.index('--fn')
        if i + 1 < len(args):
            fn_filter = args[i + 1]
    if '--waivers' in args:
        i = args.index('--waivers')
        if i + 1 < len(args):
            waiver_path = args[i + 1]

    if not os.path.exists(src):
        print(f'*** FAIL: 源文件不存在 {src}')
        sys.exit(1)

    text = read_enc(src)
    waivers = {}
    if waiver_path and os.path.isfile(waiver_path):
        waivers = json.loads(read_enc(waiver_path))
    errors = []

    # 4. crlf_clean (文件级): 无 \r\r (DLP 应字节模式写)
    if '\r\r' in text:
        errors.append('CRLF 字节不干净 (检测到 \\r\\r, DLP 应字节模式写, 禁止文本模式)')

    checked = 0
    for name, body in split_functions(text):
        if fn_filter and name != fn_filter:
            continue
        checked += 1
        check_func(name, body, errors, syntax_only=syntax_only, waivers=waivers)

    if fn_filter and checked == 0:
        errors.append(f'未找到函数 {fn_filter}')

    print(f'[scan] {src}')
    print(f'[scan] 检查函数数: {checked}')
    print(f'[scan] FAIL={len(errors)}')

    if errors:
        print('\n*** FAIL (单函数冒烟自检) ***')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('\nSINGLE-FN SMOKE PASSED')


if __name__ == '__main__':
    main()
