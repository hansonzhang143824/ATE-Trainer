# -*- coding: utf-8 -*-
# AWG/Toggle 参数检查 — Toggle/AWG 两段式 ramp 必须 3 参数 <基名>_Rise/_Fall/_Hys
# 规则源: .claude/agents/check-agent.md E005 / H010
# 命名: 参数 = DFT 参数基名 + _Rise/_Fall/_Hys 后缀 (如 VBAT_UV_Rise), 禁止泛称 Param_ 前缀, 禁止单参数
# 用法:
#   python verify_awg_params.py [--src <test.cpp>] [--strict-params]
#   --src: 默认 project_config.json 的 vs_src_dir/test.cpp
#   --strict-params: 额外检查 rampv_capv 参数值 (step=200, interval=20, trig=1.65/2.5)
# 判定: 任一 FAIL → exit 1; 只有 WARN → exit 0 (打印 WARNINGS)

import io, re, os, sys

import proj_config

# 允许的 trig_level (nQON/DTEST0 数字检测 1.65V; 其他 Toggle 可能 2.5V)
ALLOW_TRIG = (1.65, 2.5)


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


# ramp 调用判定: 必须「函数名 + (」才算调用 (裸字符串会把注释里的提及也算进来)
RAMP_CALL_RE = re.compile(r'\b(?:rampv_capv|rampi_capv)\s*\(')


def _blank_noncode(s):
    """把注释与字符串字面量替换成等长空格 (保留偏移量), 供花括号配平用。

    test.cpp 实测注释/字符串里含 217 对花括号, 直接数花括号会被干扰。
    """
    out = list(s)
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c == '/' and i + 1 < n and s[i + 1] == '/':
            j = s.find('\n', i)
            j = n if j < 0 else j
            for k in range(i, j):
                out[k] = ' '
            i = j
        elif c == '/' and i + 1 < n and s[i + 1] == '*':
            j = s.find('*/', i + 2)
            j = n if j < 0 else j + 2
            for k in range(i, j):
                out[k] = ' '
            i = j
        elif c == '"' or c == "'":
            q = c
            j = i + 1
            while j < n:
                if s[j] == '\\':
                    j += 2
                    continue
                if s[j] == q:
                    j += 1
                    break
                j += 1
            for k in range(i, j):
                out[k] = ' '
            i = j
        else:
            i += 1
    return ''.join(out)


def split_functions(text):
    """切分函数块 —— 取到「本函数体结束」(花括号配平) 为止。

    2026-09-13 修两处切块缺陷:
      ① 原实现用 re.split('吃到下一个 DUT_API 之前'), 会把**下一个函数的头注释**
         吞进本函数的块。test.cpp 98/99 个函数都带前置注释块 → 99/99 块都有此泄漏
         (实测最大 1552 字节)。泄漏进来的注释一旦含门禁关键词就把无关函数误判:
         TM425_VREF_1P2V_BUF 实为 Trim 测试, 因下一条测试(TM607-609)的批注释里
         写了 `rampi_capv` 而被误报「缺 Rise/Fall/Hys」。
      ② 原正则只认 TM\\d+_\\w+, Trim_ 命名 (Trim_IZTC_RES 等 3 个) 不切块, 会被
         并进上一个 TM 块。此处与 verify_relay_trace.fn_blocks 对齐, 两者都认。
    """
    fn_re = re.compile(r'DUT_API int ((?:TM\d+_\w+|Trim_\w+))\s*\(')
    masked = _blank_noncode(text)
    for m in fn_re.finditer(text):
        brace = masked.find('{', m.end())
        if brace < 0:
            continue
        depth, i, n = 0, brace, len(masked)
        while i < n:
            c = masked[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        yield m.group(1), text[m.start():i + 1]


def check_strict_params(name, body, warns):
    """(可选) rampv_capv 参数值标准检查 —— 与参数个数规则无关, 独立执行。"""
    for m in re.finditer(
            r'rampv_capv\s*\([^;]*?,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*([\d.]+)\s*,\s*(TRIG_\w+)\s*\)',
            body):
        samples, interval, trig, mode = m.group(1), m.group(2), m.group(3), m.group(4)
        problems = []
        if float(samples) != 200:
            problems.append(f'samples={samples}≠200')
        if float(interval) != 20:
            problems.append(f'interval={interval}≠20')
        if float(trig) not in ALLOW_TRIG:
            problems.append(f'trig={trig}∉{ALLOW_TRIG}')
        if problems:
            warns.append(f'{name}: rampv_capv 参数偏离标准 ({", ".join(problems)}, 确认是否有意为之)')


def check_func(name, body, errors, warns, strict_params):
    """对单个函数做 E005 检查; 仅含 ramp **调用**的函数参与。

    段数判定 (R-AWG, toggle-awg-rules.md): 3 参数规则只适用「两段式 ramp (升+降)」。
    ramp 调用数 <2 = 单向单段 = 单阈值设计 (ZCD / OCP / 负向限流), 不存在「释放阈值」
    → Hys = Rise − Fall 无意义 → 不要求 Rise/Fall/Hys。
    (2026-09-13 修: 原来一律套用 3 参数规则, 把 TM607/608/609/640 的单阈值设计误报成缺参数)

    支持多组三件套: 每个 <基名>_Rise/_Fall/_Hys 组独立校验 (如 BST1_UV_* + BST2_UV_* 两组)。
    """
    ramp_calls = RAMP_CALL_RE.findall(body)
    if not ramp_calls:
        return

    if strict_params:
        check_strict_params(name, body, warns)

    # 单向单段 ramp → 单阈值设计, 3 参数规则不适用 (段数从 ramp 曲线推导)
    if len(ramp_calls) < 2:
        return

    # 1. AFX 参数定义 (CParam *Name = StsGetParam(funcindex, "Name"))
    params = re.findall(
        r'CParam\s*\*\s*(\w+)\s*=\s*StsGetParam\s*\(\s*funcindex\s*,\s*"(\w+)"\s*\)\s*;', body)
    names = [s for _, s in params]

    # 2. 必须有 _Rise / _Fall / _Hys 三参数 (至少一组)
    rise = [n for n in names if n.endswith('_Rise')]
    fall = [n for n in names if n.endswith('_Fall')]
    hys  = [n for n in names if n.endswith('_Hys')]
    if not (rise and fall and hys):
        errors.append(
            f'{name}: 缺 _Rise/_Fall/_Hys 三参数 (E005) — 应为 <DFT参数基名>_Rise/_Fall/_Hys, 如 VBAT_UV_Rise')
        return  # 基名未定, 后续检查无法继续

    # 3. 按基名分组: 每个基名必须 Rise/Fall/Hys 三件套齐全 (支持多组, 如 BST1_UV + BST2_UV)
    bases = {n[:-5] for n in rise} | {n[:-5] for n in fall} | {n[:-4] for n in hys}
    for base in sorted(bases):
        missing = [suf for suf in ('Rise', 'Fall', 'Hys') if f'{base}_{suf}' not in names]
        if missing:
            errors.append(
                f'{name}: 参数组 {base} 缺 {"_".join(missing)} 后缀参数 (E005) — 每组须 Rise/Fall/Hys 齐全')
    # 一致性: 所有 _Rise 都应有对应基名 (防 BST1_UV_Rise 与 BST2_UV_Rise 混搭错组)
    for n in rise + fall + hys:
        if n[:-5] not in bases and n[:-4] not in bases:
            errors.append(f'{name}: 参数 {n} 找不到完整三件套基名 (E005)')

    # 4. 禁止泛称 Param_ 前缀 (Param 是占位泛称, 必须用 DFT 参数基名)
    for n in rise + fall + hys:
        if n.startswith('Param_'):
            errors.append(f'{name}: 参数 {n} 用泛称 Param_ 前缀 — 必须用 DFT 参数基名 (如 VBAT_UV_Rise) (E005)')

    # 5. 单参数 (Toggle 只定义 1 个 CParam 且不含后缀 → 漏 3 参数)
    if len(params) == 1 and not (rise or fall or hys):
        errors.append(f'{name}: 只定义单参数 {names[0]}, Toggle 两段式必须 3 参数 (E005)')

    # 6. 必须有 hys 计算 (函数级: 任何含 hys 的变量被赋值 即为有 Hys=Rise−Fall 计算,
    #    兼容裸 hys[site]= 与分组命名 bst1_hys[site]= / bst2_hys[site]=)
    if not re.search(r'\b\w*hys\w*\s*\[?[^;]*?=', body):
        errors.append(f'{name}: 缺 hys 计算 (Hys = Rise − Fall) (E005)')

    # 7. LogData 必须每组 3 个分别 SetTestResult
    for base in sorted(bases):
        for suf in ('Rise', 'Fall', 'Hys'):
            if f'{base}_{suf}->SetTestResult' not in body:
                errors.append(f'{name}: LogData 缺 {base}_{suf}->SetTestResult (E005)')

    # (参数值标准检查已上移为 check_strict_params —— 单段 ramp 函数同样要查)


def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    except AttributeError:
        pass
    args = sys.argv[1:]
    cfg = proj_config.load(proj_config.config_from_argv(args))
    strict_params = '--strict-params' in args
    src = cfg['derived']['test_cpp']
    if '--src' in args:
        i = args.index('--src')
        if i + 1 < len(args) and not str(args[i + 1]).startswith('--'):
            src = args[i + 1]

    if not os.path.exists(src):
        print(f'*** FAIL: 源文件不存在 {src}')
        sys.exit(1)

    text = read_enc(src)
    errors, warns = [], []
    awg_count = 0
    single_ramp = 0
    for name, body in split_functions(text):
        n_calls = len(RAMP_CALL_RE.findall(body))
        if n_calls:
            awg_count += 1
            if n_calls < 2:
                single_ramp += 1
        check_func(name, body, errors, warns, strict_params)

    print(f'[scan] {src}')
    print(f'[scan] AWG 函数 (含 ramp 调用): {awg_count} '
          f'(两段式 {awg_count - single_ramp} / 单段单阈值 {single_ramp} — 后者不适用 3 参数规则)')
    print(f'[scan] FAIL={len(errors)} WARN={len(warns)}')

    if warns:
        print('\nWARNINGS:')
        for w in warns:
            print('  -', w)
    if errors:
        print('\n*** FAIL (E005 AWG/Toggle 参数) ***')
        for e in errors:
            print('  -', e)
        sys.exit(1)
    print('\nAWG PARAMS PASSED')


if __name__ == '__main__':
    main()
