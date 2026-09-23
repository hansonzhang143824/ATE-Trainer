# -*- coding: utf-8 -*-
"""t25 patcher — 门禁 harness/模型修复 (F1 基线读取 / F2 家族前缀碰撞)。

为什么用 python 打补丁而不是 PowerShell/edit:
  1) 源受 DLP 透明加密: 只有授权读者(python)读得到明文; pwsh 文本/哈希操作是"盲的"。
  2) 必须**逐字节**保留 BOM + LF 行尾 + 编码 (run_gates.ps1 = UTF-8 BOM + LF)。
用法: python t25_apply.py [--verify-only]
"""
import hashlib
import os
import sys

# __file__ = <workspace>/team/artifacts/<run>/gate-logs-t25/t25_apply.py  → 上溯 5 级 = <workspace>
ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..', '..'))
assert os.path.isfile(os.path.join(ROOT, 'project_config.json')), 'ROOT 解析失败: ' + ROOT


def sha(path):
    return hashlib.sha256(open(path, 'rb').read()).hexdigest()


def read_bytes(path):
    with open(path, 'rb') as f:
        return f.read()


def patch(path, pairs):
    """对 path 做逐处替换; 每处必须恰好命中 1 次, 否则报错不写。"""
    raw = read_bytes(path)
    before = hashlib.sha256(raw).hexdigest()
    bom = raw[:3] == b'\xef\xbb\xbf'
    text = raw.decode('utf-8-sig')
    new = text
    for old, rep in pairs:
        n = new.count(old)
        if n != 1:
            raise SystemExit('ERROR: %s 命中 %d 次(应 1):\n---\n%s\n---' % (path, n, old[:200]))
        new = new.replace(old, rep)
    out = new.encode('utf-8')
    if bom:
        out = b'\xef\xbb\xbf' + out
    with open(path, 'wb') as f:
        f.write(out)
    after = hashlib.sha256(out).hexdigest()
    print('PATCHED %s\n  before=%s (%d B)\n  after =%s (%d B)\n  bom=%s lf=%d crlf=%d'
          % (path, before, len(raw), after, len(out), bom, out.count(b'\n') - out.count(b'\r\n'),
             out.count(b'\r\n')))
    return before, after


# =========================== F1: 基线/配置读取 ===========================
F1_OLD_HEAD = '''$ErrorActionPreference = "Continue"
$root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
if (-not $LogDir) { $LogDir = Join-Path $env:TEMP ("dsh_gates_" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$baselinePath = Join-Path $root "scripts\\gate_baseline.json"

# gen_cbit_defines.py --verify 需要一个「对拍目标 StdAfx.h」参数。
# 2026-09-13 踩坑: 裸写 --verify 会 argparse 报错 exit=2（不是校验失败，是用法错）；
# nuvolta-codegen.md Step5 里也漏写了这个参数。
$stdafx = $null
try {
    $cfg = Get-Content (Join-Path $root 'project_config.json') -Raw -Encoding UTF8 | ConvertFrom-Json
    $stdafx = $cfg.inputs.relay_definitions
    $schMap = $cfg.intermediates.sch_connect_map
    if (-not $BuildPath) { $BuildPath = $cfg.inputs.vs_src_dir }
} catch { }
if (-not $stdafx) { Write-Output "WARN: 读不到 project_config.json 的 inputs.relay_definitions → cbit 门将跳过" }'''

F1_NEW_HEAD = '''$ErrorActionPreference = "Continue"
# $PSScriptRoot 比 $MyInvocation.MyCommand.Path 可靠: 后者在被 dot-source/嵌套调用时
# 可能指向调用者。$PSScriptRoot 恒为本脚本所在目录 (即 <workspace>/scripts)。
$root = $PSScriptRoot
if (-not $root) { $root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }
if (-not $LogDir) { $LogDir = Join-Path $env:TEMP ("dsh_gates_" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$baselinePath = Join-Path $root "scripts\\gate_baseline.json"

# ---- 读 JSON 一律经「授权读者」(python) —— t25 修复 F1 ----
# 为什么 (2026-09-16 实测): 本工作区受 DLP 透明加密, pwsh 是**盲的**:
#   `Get-Content -Raw -Encoding UTF8` 拿到的是 TSZ 密文容器 (头 `%TSD-Header-###%`),
#   例: scripts/gate_baseline.json = 密文 8192 B vs python 明文 28 B
#       project_config.json       = pwsh 读到的首字符为 'T' (密文) vs python 明文 JSON
#   ⇒ `ConvertFrom-Json` 抛错 ⇒ `$baseline` 为空 ⇒ **所有红灯被误判 NEW-RED**
#     (cbit 实为 KNOWN-RED), 且 `$stdafx` 为空 ⇒ **cbit 门被静默跳过(从未执行)**。
#   ⇒ 改为 python 以 rb 读原文(经 DLP 白名单解密) → json.dumps(ascii) → ConvertFrom-Json。
#   本修复**只改读取方式**: 基线内容与判据一字未动 (gate_baseline.json 哈希前后不变)。
function Read-JsonViaPython {
    param([Parameter(Mandatory = $true)][string]$Path)
    $pyCode = 'import json,sys;sys.stdout.reconfigure(encoding="utf-8");print(json.dumps(json.load(open(sys.argv[1],encoding="utf-8-sig")),ensure_ascii=True,separators=(",",":")))'
    $raw = $null
    try { $raw = & python -c $pyCode $Path 2>$null } catch { return $null }
    if (-not $raw -or $LASTEXITCODE -ne 0) { return $null }
    return (($raw | Out-String).Trim() | ConvertFrom-Json)
}

# gen_cbit_defines.py --verify 需要一个「对拍目标 StdAfx.h」参数。
# 2026-09-13 踩坑: 裸写 --verify 会 argparse 报错 exit=2（不是校验失败, 是用法错）；
# nuvolta-codegen.md Step5 里也漏写了这个参数。
$stdafx = $null
try {
    $cfg = Read-JsonViaPython (Join-Path $root 'project_config.json')
    $stdafx = $cfg.inputs.relay_definitions
    $schMap = $cfg.intermediates.sch_connect_map
    if (-not $BuildPath) { $BuildPath = $cfg.inputs.vs_src_dir }
} catch { }
if (-not $stdafx) { Write-Output "WARN: 读不到 project_config.json 的 inputs.relay_definitions → cbit 门将跳过" }'''

F1_OLD_BASE = '''$baseline = @{}
if (Test-Path $baselinePath) {
    try {
        $b = Get-Content $baselinePath -Raw -Encoding UTF8 | ConvertFrom-Json
        $b.PSObject.Properties | ForEach-Object { $baseline[$_.Name] = $_.Value }
    } catch { }
}'''

F1_NEW_BASE = '''$baseline = @{}
if (Test-Path $baselinePath) {
    try {
        $b = Read-JsonViaPython $baselinePath
        if ($b) { $b.PSObject.Properties | ForEach-Object { $baseline[$_.Name] = $_.Value } }
    } catch { }
}
if ($baseline.Count -eq 0 -and (Test-Path $baselinePath)) {
    Write-Output "WARN: 基线 $baselinePath 解析为空 → 存量红无法区分 (按全 NEW-RED 处理)"
} else {
    Write-Output ("基线(存量红) 已加载: {0}" -f (($baseline.Keys | Sort-Object) -join ', '))
}'''

# =========================== F2: 家族前缀碰撞 ===========================
F2_OLD = '''def fam_intersect(pins, fam):
    """pins 与 Cap 家族 fam (VCC/VBAT/VAC/VBUS) 的按 PIN 成员匹配"""
    return {p for p in pins if p == fam or p.startswith(fam) or fam.startswith(p)}'''

F2_NEW = '''def fam_intersect(pins, fam):
    """pins 与 Cap 家族 fam (VCC/VBAT/VAC/VBUS/SW...) 的按 PIN 成员匹配。

    t25 修复 F2 (前缀碰撞): 原实现 `p.startswith(fam) or fam.startswith(p)` 是**纯字符串前缀**,
    把不同轨折成同一家族:
      'SW1_BST1'.startswith('SW')   → 供电轨 'SW' 误命中 SW1_BST1/SW2_BST2 的 Cap
                                      (K45_Cap_SW1_BST1 / K44_Cap_SW2_BST2, 见 cap_pin())
      fam == 'VBUS' 与 'VBUS_F' 之类子串同理。
    判据: SCH-Connect-Map.txt:177 `CH0 High -> SW1 ... K46` / :183 `SW2 ... K46,K49` 与
          :174 `CH0 Low -> SW ... K60,K61` 是**不同节点**, 供电 SW 不得对 SW1/SW2 提出 Cap 要求。
    修法: 家族相等, 或**token 边界**相同 (下划线/连字符/空白/串尾) —— 即 'BST_SW' 仍命中家族
          'SW'(尾界), 'SW1_BST1' 不再命中 'SW'(下一字符是数字)。
    注意: 本函数用于 powered/mi/ramp/testpad 四个集合 (L318/L321/L325) 与降级分支; 判据仅"是否
          同一 token", 不改变任何集合的内容或规则强度。
    """
    if not fam:
        return set()
    hit = set()
    for p in pins:
        if p == fam:
            hit.add(p)
            continue
        # fam 作为 p 的 token 前缀: 其后必须是非字母数字的家族边界
        if p.startswith(fam):
            nxt = p[len(fam):len(fam) + 1]
            if nxt and not (nxt.isalnum()):
                hit.add(p)
                continue
        # p 作为 fam 的 token 前缀: fam 中 p 之后必须是非字母数字的家族边界
        if fam.startswith(p):
            nxt = fam[len(p):len(p) + 1]
            if nxt and not (nxt.isalnum()):
                hit.add(p)
    return hit'''

PATCHES = [
    (os.path.join(ROOT, 'scripts', 'run_gates.ps1'), [('F1_HEAD', (F1_OLD_HEAD, F1_NEW_HEAD)),
                                                      ('F1_BASE', (F1_OLD_BASE, F1_NEW_BASE))]),
    (os.path.join(ROOT, 'scripts', 'verify_relay_trace.py'), [('F2', (F2_OLD, F2_NEW))]),
]


def main():
    verify_only = '--verify-only' in sys.argv
    for path, pairs in PATCHES:
        if verify_only:
            text = read_bytes(path).decode('utf-8-sig')
            for label, (old, _rep) in pairs:
                print('%s %s: 命中 %d 次' % (path, label, text.count(old)))
            continue
        patch(path, [(o, r) for _lbl, (o, r) in pairs])
    print('DONE')


if __name__ == '__main__':
    main()
