# -*- coding: utf-8 -*-
"""
gen_test_conditions.py — 生成 test_conditions.yaml（DFT 极简摘要，给人看；与 meta 互相不派生）

架构（2026-08-27 用户定稿）:
  DFT 解析 ──同步──▶ meta 文件（完整数据 + 寄存器补充 + 项目/参数类型判定，供 AI/脚本）
                 └─▶ YAML 文件（极简摘要，只给人类速览）
  两者都从 DFT 解析出来，互相不派生。

输入: 仅 dali_tm_meta.json（DFT 解析产物）。详细数据在 meta，YAML 只摘取摘要行：
  - power:  静态 vset 供电 PIN=V（保 DFT 次序；两段斜坡 pin 移入 rampv；monitor bias 由 agent 移出）
  - rampv:  两段斜坡（同 pin 首尾相等连续 vset → 升+降）pin；iset 斜坡 → rampi
  - measure:PIN (MI/MV)      （normal / trim，trim 带标注）
  - monitor:PIN (toggleI/V)  （toggle；pin/bias 语义由 agent 按黄金补，如 TM616 ATEST0→VDM）

用法: python gen_test_conditions.py [--config <json>] [--meta <meta.json>] [--out <yaml>]
"""
import json
import io
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import proj_config

# 路径一律走 project_config.json 唯一入口
# (2026-09-13 修正: 原 _BASE 指向 scripts/ 导致默认 meta/out 路径全部失效, 脚本实际跑不起来)
_CFG = proj_config.load(proj_config.config_from_argv(sys.argv))
_DEF_META = _CFG['outputs']['meta']
_DEF_OUT = _CFG['outputs'].get('test_conditions') or os.path.join(
    _CFG['project_dir'], 'meta', 'test_conditions.yaml')


def read_enc(path):
    """rb 读(DLP 白名单解密) + 编码回退解码。"""
    with open(path, 'rb') as f:
        raw = f.read()
    for enc in ('utf-8-sig', 'utf-8', 'gbk', 'latin-1'):
        try:
            return raw.decode(enc)
        except (UnicodeDecodeError, ValueError):
            continue
    return raw.decode('utf-8', errors='replace')


def _y(v):
    """YAML 标量安全化（含特殊字符才加引号）。"""
    s = str(v)
    if any(c in s for c in ':#{}[],&*!|>%@`"\'\\\n') or s != s.strip() \
            or s.lower() in ('yes', 'no', 'true', 'false', 'null', '~'):
        return json.dumps(s, ensure_ascii=False)
    return s


def _fmt_v(v):
    """电压值格式化: 3.5→'3.5', 5.0→'5'（整数去 .0）"""
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else repr(f)
    except (TypeError, ValueError):
        return str(v)


def _split_power_ramps(cmds):
    """把 hardwareInit 里的两段斜坡从静态供电拆出（保守，脚本不猜）。

    规则: 同 pin 连续 vset 且首尾值相等（如 amux 1.3→1.5→1.3）→ 斜坡段，
    相邻两两拆成升/降 pair；单调两连（3→5）可能是台阶非斜坡，留在 power 由 agent 定。
    返回 (power_lines, ramp_pairs)；ramp_pairs 每项 = [v1, v2, ...] 原值序列。
    """
    out = []
    ramps = []
    i = 0
    n = len(cmds)
    while i < n:
        c = cmds[i]
        if c.get('cmd') == 'vset':
            j = i
            while j < n and cmds[j].get('cmd') == 'vset' and cmds[j].get('pin') == c.get('pin'):
                j += 1
            run = cmds[i:j]
            if len(run) >= 3 and str(run[0].get('value')) == str(run[-1].get('value')):
                ramps.append(run)
                i = j
                continue
        out.append(c)
        i += 1
    return out, ramps


def main(argv):
    meta_path = _DEF_META
    out_path = _DEF_OUT
    for i, a in enumerate(argv):
        if a == '--meta' and i + 1 < len(argv):
            meta_path = argv[i + 1]
        if a == '--out' and i + 1 < len(argv):
            out_path = argv[i + 1]
    meta = json.loads(read_enc(meta_path))
    # 输入同步 stamp: 本 YAML 派生自哪一版 meta / DFT (供 check_input_sync.py 判 meta↔YAML 同版本)
    meta_sha = proj_config.sha256_file(meta_path) or ''
    dft_sha = (meta.get('_syncStamp') or {}).get('dftSha256') or ''

    L = []
    L.append('# test_conditions.yaml — DFT 极简摘要（给人看；与 meta 互相不派生，同为 DFT 解析产物）')
    L.append('# 摘要行: power / rampv·rampi / measure(normal·trim) / monitor(toggle)；monitor pin 语义由 agent 按黄金补')
    L.append('source: Dali_testmode.xlsx (OVERVIEW)')
    L.append('_sync:')
    L.append('  metaSha256: %s' % meta_sha)
    L.append('  dftSha256: %s' % dft_sha)
    L.append('tms:')
    for fn in meta['functions']:
        name = fn['functionName']
        ttype = fn['testType']
        power_lines, ramps = _split_power_ramps(fn.get('hardwareInit', []))
        # testType 覆盖（2026-08-27 拍板）: 两段斜坡(升+降) → toggle；meta 已在解析时确定，此处兜底
        eff_ttype = 'toggle' if (ttype == 'toggle' or ramps) else ttype
        params = fn.get('params', [])
        L.append('  %s:' % _y(name))
        # --- power: 静态 vset 供电（保 DFT 次序；两段斜坡 pin 移入 rampv；monitor bias 由 agent 移出）---
        static = [c for c in power_lines if c.get('cmd') == 'vset']
        ramp_pins = {run[0].get('pin', '').lower() for run in ramps}
        pw = ['%s=%sV' % (c.get('pin', '').upper(), _fmt_v(c.get('value', '')))
              for c in static if c.get('pin', '').lower() not in ramp_pins]
        L.append('    power: %s' % (', '.join(pw) if pw else '[]'))
        # --- rampv / rampi ---
        if ramps:
            rp = sorted({run[0].get('pin', '').upper() for run in ramps})
            L.append('    rampv: %s' % ', '.join(rp))
        iset = [c.get('pin', '').upper() for c in fn.get('hardwareInit', []) if c.get('cmd') == 'iset']
        if iset:
            L.append('    rampi: %s   # agent 补 PIN1-PIN2（ZCD 类）' % ', '.join(sorted(set(iset))))
        # --- measure / monitor ---
        if eff_ttype == 'toggle':
            ob = 'toggleI' if params and str(params[0].get('check', '')).upper() == 'MI' else 'toggleV'
            mon = params[0].get('checkPin', '') if params else ''
            L.append('    monitor: %s (%s)   # agent 补: checkPin→实际 pad/bias' % (_y(mon), ob))
        else:
            chk = ', '.join('%s (%s%s)' % (_y(p.get('checkPin', '')), _y(p.get('check', '')),
                                           ', trim' if eff_ttype == 'trim' else '')
                            for p in params) if params else '[]'
            L.append('    measure: %s' % chk)

    with io.open(out_path, 'w', encoding='utf-8', newline='') as f:
        f.write('\n'.join(L) + '\n')
    print('WROTE %s functions=%d' % (out_path, len(meta['functions'])))
    return 0


if __name__ == '__main__':
    raise SystemExit(main(sys.argv[1:]))
