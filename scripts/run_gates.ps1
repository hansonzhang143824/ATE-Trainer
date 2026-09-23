# run_gates.ps1 — 收尾门禁一次跑完（把 12 次工具调用压成 1 次）+ 存量失败基线对照
#
# 为什么有这个脚本（2026-09-13 实测结论）：
#   每次工具调用 = **一次完整的模型往返**（模型要把整段累积上下文重新处理一遍）。
#   12 个门禁分 12 次调用 → 12 轮往返；合并成 1 次 → 省 11 轮。
#   机器时间只省 ~3.6s（可忽略），**省的是"轮数"**。
#   本脚本因此只把【新增红 / 已修复】的细节打出来 → 汇总输出很小。
#
# 用法:
#   .\run_gates.ps1                      # 跑全部门禁, 对照基线
#   .\run_gates.ps1 -Scope 1205          # 给 meta 反向覆盖门带上批次范围
#   .\run_gates.ps1 -Build               # 门禁跑完再增量编译一次（阶段1/阶段2 各用一次）
#   .\run_gates.ps1 -UpdateBaseline      # 把当前红灯登记为"已知存量"基线
#   .\run_gates.ps1 -Only awg,relay-trace
#
# 退出码: 0 = 无新增红（存量红不阻塞）; 1 = 有新增红

param(
    [string]$Scope = "",
    [switch]$Build,
    [switch]$UpdateBaseline,
    [string[]]$Only = @(),
    [string]$LogDir = "",
    [string]$Config = "Release",
    [string]$BuildPath = ""
)

$ErrorActionPreference = "Continue"
# $root = **workspace 根** (不是 scripts 目录): 下面所有路径都写成 $root + "scripts\..."。
# 用本脚本文件的真实路径上溯两级: <workspace>/scripts/run_gates.ps1 → <workspace>。
# 不用 $PSScriptRoot 直取: 本脚本可能以**副本**形式被运行/沙箱/dot-source, 那时
# $PSScriptRoot = 副本目录 → 基线/配置静默找不到 (t25 首版踩过, 已实测)。
$__self = $MyInvocation.MyCommand.Path
if (-not $__self) { $__self = $PSCommandPath }
if (-not $__self) { $__self = Join-Path $PSScriptRoot 'run_gates.ps1' }
$root = Split-Path -Parent (Split-Path -Parent $__self)
if (-not $LogDir) { $LogDir = Join-Path $env:TEMP ("dsh_gates_" + (Get-Date -Format "yyyyMMdd_HHmmss")) }
New-Item -ItemType Directory -Force -Path $LogDir | Out-Null
$baselinePath = Join-Path $root "scripts\gate_baseline.json"

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
if (-not $stdafx) { Write-Output "WARN: 读不到 project_config.json 的 inputs.relay_definitions → cbit 门将跳过" }

# ---- 门禁清单（id / 说明 / 命令）----
$gates = @(
    @{ id = 'material-audit';  desc = '材料门 规则自检';        args = @('scripts\verify_material_receipt.py', '--audit-rules') },
    @{ id = 'material';        desc = '材料门 主门';            args = @('scripts\verify_material_receipt.py') },
    @{ id = 'material-status'; desc = '材料状态索引 漂移';      args = @('scripts\gen_material_status.py', '--check') },
    @{ id = 'awg';             desc = 'AWG/Toggle 3参数 E005';  args = @('scripts\verify_awg_params.py', '--strict-params') },
    @{ id = 'meta';            desc = 'meta 全覆盖门';          args = @('scripts\check_testitems_meta.py', '--require-all') },
    @{ id = 'smoke';           desc = '单函数冒烟';             args = @('scripts\verify_single_fn.py') },
    @{ id = 'input-sync';      desc = '输入同步门';             args = @('scripts\check_input_sync.py') },
    @{ id = 'relay-trace';     desc = '继电器反向检查 E';        args = @('scripts\verify_relay_trace.py', '--meta') },
    @{ id = 'merge';           desc = '合并纪律';               args = @('scripts\verify_merge_rules.py') },
    @{ id = 'bst-sw';          desc = 'BST-SW 黄金约束';        args = @('scripts\verify_bst_sw_sequence.py') },
    @{ id = 'cbit';            desc = 'CBIT 定义校验';          args = @('scripts\gen_cbit_defines.py', '--verify') },    @{ id = 'path-def';        desc = '通路定义校验';           args = @('scripts\gen_path_defines.py', '--verify') }
)

# ---- 基线（已知存量红）----
$baseline = @{}
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
}

# ---- 逐个跑 ----
$results = @()
foreach ($g in $gates) {
    if ($Only.Count -gt 0 -and ($Only -notcontains $g.id)) { continue }
    $a = @($g.args)
    if ($g.id -eq 'meta' -and $Scope) { $a += @('--require-scope', $Scope) }
    if ($g.id -eq 'cbit') {
        if (-not $stdafx) { continue }
        $a += @($stdafx)
        if ($schMap) { $a += @('--map', $schMap) }   # --map 也需要参数; 不给会降级为纯名字规则(V6 WARN)
    }

    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    $out = & python @a 2>&1
    $code = $LASTEXITCODE
    $sw.Stop()

    $log = Join-Path $LogDir ($g.id + '.log')
    ($out | Out-String) | Set-Content -Path $log -Encoding UTF8
    $errLines = @($out | Where-Object { "$_" -match '^\s*[-*]\s+\S' } | Select-Object -First 6)

    $known = $baseline.ContainsKey($g.id)
    $status = if ($code -eq 0) { if ($known) { 'FIXED' } else { 'GREEN' } }
              elseif ($known) { 'KNOWN-RED' } else { 'NEW-RED' }

    $results += [pscustomobject]@{
        id = $g.id; desc = $g.desc; exit = $code; status = $status
        sec = [math]::Round($sw.Elapsed.TotalSeconds, 2); log = $log; errLines = $errLines
    }
}

# ---- 汇总（只打新增红 / 已修复 的细节）----
Write-Output "================ run_gates 汇总 ================"
Write-Output ("  {0,-16} {1,-24} {2,-10} {3,-5} {4}" -f 'id', '门禁', '状态', 'exit', '秒')
$results | ForEach-Object {
    Write-Output ("  {0,-16} {1,-24} {2,-10} {3,-5} {4:N2}" -f $_.id, $_.desc, $_.status, $_.exit, $_.sec)
}

$buildFail = $false
$newRed = @($results | Where-Object { $_.status -eq 'NEW-RED' })
$fixed  = @($results | Where-Object { $_.status -eq 'FIXED' })
$known  = @($results | Where-Object { $_.status -eq 'KNOWN-RED' })

if ($newRed.Count -gt 0) {
    Write-Output "*** 新增红 $($newRed.Count) 个（阻塞）***"
    foreach ($r in $newRed) {
        Write-Output ("  [$($r.id)] $($r.desc)  exit=$($r.exit)")
        $r.errLines | ForEach-Object { Write-Output ("      " + ("$_").Trim()) }
        Write-Output ("      日志: $($r.log)")
    }
}
if ($fixed.Count -gt 0) { Write-Output "已修复（基线可清理）: $($fixed.id -join ', ')" }
if ($known.Count -gt 0) { Write-Output "存量红（已知, 不阻塞）: $(($known | ForEach-Object { $_.id }) -join ', ')" }
if ($newRed.Count -eq 0) { Write-Output "结论: 无新增红 —— 收尾通过（存量红 $($known.Count) 个）" }

# ---- 编译（可选）----
if ($Build) {
    if (-not $BuildPath) {
        Write-Output "ERROR: 未配置编译目录（project_config.json inputs.vs_src_dir 或 -BuildPath）"
        exit 1
    }
    Write-Output "---------------- 增量编译（$Config）----------------"
    Write-Output "  编译目录: $BuildPath"
    $blog = Join-Path $LogDir 'build.log'
    $b = & (Join-Path $root 'scripts\fast_rebuild.ps1') $BuildPath -Config $Config -Incremental -LogFile $blog 2>&1
    $bcode = $LASTEXITCODE
    $bstat = if ($bcode -eq 0) { 'PASSED' } else { 'FAILED' }
    Write-Output ("  编译($Config): $bstat (exit=$bcode)")
    Write-Output ("  编译器日志: $blog")
    if ($bcode -ne 0) { $buildFail = $true }
}

# ---- 基线写入 ----
if ($UpdateBaseline) {
    $obj = @{}
    foreach ($r in $results) { if ($r.exit -ne 0) { $obj[$r.id] = $true } }
    ($obj | ConvertTo-Json -Depth 3) | Set-Content -Path $baselinePath -Encoding UTF8
    Write-Output "已更新基线 → $baselinePath（登记存量红 $(@($obj.Keys).Count) 个: $(@($obj.Keys) -join ', ')）"
}

Write-Output "日志目录: $LogDir"
if ($newRed.Count -gt 0 -or $buildFail) { exit 1 } else { exit 0 }
