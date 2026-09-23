# -*- coding: utf-8 -*-
"""t25 patcher 2 — 修正 F1 的 $root 解析 (第一版误用 $PSScriptRoot)。

第一版把 `$root = $PSScriptRoot` 写成了"脚本所在目录 = <ws>\scripts", 但原脚本约定
`$root` = **workspace 根** (再由 $root + "scripts\..." 拼路径)。若脚本以副本形式运行
(诊断/沙箱/被 dot-source), $PSScriptRoot 变成副本目录 → 基线/配置全找不到 → 基线静默为空。
修法: 以**本脚本文件真实路径**上溯两级 (原语义), $PSScriptRoot 只作为 $MyInvocation 为空时的兜底。
"""
import hashlib
import io
import os

WS = 'D:/Newtest/DSH/ATE-Coding-Plat'
P = os.path.join(WS, 'scripts', 'run_gates.ps1')

OLD = '''# $PSScriptRoot 比 $MyInvocation.MyCommand.Path 可靠: 后者在被 dot-source/嵌套调用时
# 可能指向调用者。$PSScriptRoot 恒为本脚本所在目录 (即 <workspace>/scripts)。
$root = $PSScriptRoot
if (-not $root) { $root = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path) }'''

NEW = '''# $root = **workspace 根** (不是 scripts 目录): 下面所有路径都写成 $root + "scripts\\..."。
# 用本脚本文件的真实路径上溯两级: <workspace>/scripts/run_gates.ps1 → <workspace>。
# 不用 $PSScriptRoot 直取: 本脚本可能以**副本**形式被运行/沙箱/dot-source, 那时
# $PSScriptRoot = 副本目录 → 基线/配置静默找不到 (t25 首版踩过, 已实测)。
$__self = $MyInvocation.MyCommand.Path
if (-not $__self) { $__self = $PSCommandPath }
if (-not $__self) { $__self = Join-Path $PSScriptRoot 'run_gates.ps1' }
$root = Split-Path -Parent (Split-Path -Parent $__self)'''

raw = open(P, 'rb').read()
bom = raw[:3] == b'\xef\xbb\xbf'
t = raw.decode('utf-8-sig')
assert t.count(OLD) == 1, t.count(OLD)
out = t.replace(OLD, NEW).encode('utf-8')
if bom:
    out = b'\xef\xbb\xbf' + out
open(P, 'wb').write(out)
print('PATCHED %s\n  before=%s (%d B)\n  after =%s (%d B)\n  bom=%s'
      % (P, hashlib.sha256(raw).hexdigest(), len(raw), hashlib.sha256(out).hexdigest(), len(out), bom))
