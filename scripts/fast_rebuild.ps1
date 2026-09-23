# fast_rebuild.ps1 — 按工程路径快速构建 (命令行 MSBuild, 替代慢的 IDE Rebuild)
#
# 用法:
#   .\fast_rebuild.ps1 D:\PROJECT6-DALI\devel\source            # 目录/找到 sln
#   .\fast_rebuild.ps1 D:\PROJECT6-DALI\devel\source\F12011.sln # 指定 sln
#   .\fast_rebuild.ps1 D:\PROJECT6-DALI\devel\source -Config Release -Platform Win32
#   .\fast_rebuild.ps1 <路径> -Incremental    # 增量 Build (只重编改动, 最快)
#   .\fast_rebuild.ps1 <路径> -Config Both    # Release+Debug 都编
#
param(
    [Parameter(Mandatory=$true, Position=0, HelpMessage="工程路径: sln/vcxproj 文件或所在目录")]
    [string]$Path,

    [ValidateSet("Release","Debug","Both")]
    [string]$Config = "Release",

    [ValidateSet("Win32","x64","Any CPU")]
    [string]$Platform = "Win32",

    [switch]$Incremental,   # 用 Build(增量) 而非 Rebuild
    [switch]$Quiet,         # 精简输出
    [string]$LogFile = ""  # 可审计的纯文本构建日志（含 MSBuild 原始输出）
)

$ErrorActionPreference = "Stop"
$sw = [System.Diagnostics.Stopwatch]::StartNew()

if ($LogFile) {
    $logParent = Split-Path -Parent $LogFile
    if ($logParent) { New-Item -ItemType Directory -Force -Path $logParent | Out-Null }
    Set-Content -LiteralPath $LogFile -Value "fast_rebuild started=$(Get-Date -Format o) path=$Path config=$Config platform=$Platform incremental=$Incremental" -Encoding UTF8
}

function Add-BuildLog { param($m) if ($LogFile) { Add-Content -LiteralPath $LogFile -Value $m -Encoding UTF8 } }

function Write-Step { param($m) Add-BuildLog (">>> " + $m); if (-not $Quiet) { Write-Host ("`n>>> " + $m) -ForegroundColor Cyan } }
function Write-OK   { param($m) Add-BuildLog ("OK: " + $m); if (-not $Quiet) { Write-Host ("  OK: " + $m) -ForegroundColor Green } }
function Write-WARN { param($m) Add-BuildLog ("WARN: " + $m); Write-Host ("  WARN: " + $m) -ForegroundColor Yellow }
function Write-ERR  { param($m) Add-BuildLog ("ERROR: " + $m); Write-Host ("  ERROR: " + $m) -ForegroundColor Red }

# ---- 0. 前置: 保存 VS 打开的已修改文档 (等价 VS IDE 编译前自动保存) ----
# 用户期望: 点击 VS Rebuild 会自动保存带 * 的文件, 命令行构建也应先保存,
# 否则命令行 MSBuild 只能编译磁盘旧版, DLL 不含 VS 里未保存的修改。
# 实现: COM (DTE) 连接运行中的 VS 实例 → File.SaveAll; 无 VS 运行则跳过。
function Save-VSDocuments {
    foreach ($v in @('12.0','14.0','15.0','16.0','17.0')) {
        try {
            $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject("VisualStudio.DTE.$v")
            $dte.ExecuteCommand("File.SaveAll") | Out-Null
            Write-OK "VS$v (DTE) 已保存所有打开的文档"
            return $true
        } catch {
            # 该版本未注册或 VS 未运行, 试下一版本
        }
    }
    Write-WARN "未连接运行中的 VS, 跳过自动保存 (若 VS 有未保存修改请先 Ctrl+S)"
    return $false
}

Write-Step "Step 0: 编译前保存 VS 文档"
Save-VSDocuments | Out-Null

# ---- 1. 解析工程文件 (目录 → sln; sln/vcxproj → 直接) ----
Write-Step "Step 1: 解析工程路径"
$sln = $null; $vcx = $null
if (Test-Path $Path -PathType Container) {
    $sln = Get-ChildItem -Path $Path -Filter "*.sln" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if (-not $sln) { $vcx = Get-ChildItem -Path $Path -Filter "*.vcxproj" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1 }
} elseif ($Path -like "*.sln") {
    $sln = Get-Item $Path
} elseif ($Path -like "*.vcxproj") {
    $vcx = Get-Item $Path
} else {
    Write-ERR "无法识别的路径: $Path (需目录或 .sln/.vcxproj)"; exit 1
}
if ($sln) {
    Write-OK "解决方案: $($sln.FullName)"
    if (-not $vcx) { $vcx = Get-ChildItem (Split-Path $sln.FullName -Parent) -Filter "*.vcxproj" -ErrorAction SilentlyContinue | Select-Object -First 1 }
    $buildFile = $sln
} else {
    Write-OK "项目文件: $($vcx.FullName)"
    $buildFile = $vcx
}

# ---- 2. MSBuild v120 ----
$msbuild = "C:\Program Files (x86)\MSBuild\12.0\Bin\MSBuild.exe"
if (-not (Test-Path $msbuild)) {
    Write-ERR "MSBuild v120 不存在: $msbuild"; exit 1
}
Write-OK "MSBuild: $msbuild"

# ---- 3. toolset 检查 (v143→v120, 本机无 v143 编译器) ----
if ($vcx) {
    $toolsetLine = Select-String -Path $vcx.FullName -Pattern 'PlatformToolset' | Select-Object -First 1
    if ($toolsetLine -match '>v(\d+)<') {
        $ts = [int]$matches[1]
        if ($ts -gt 120) {
            Write-WARN "PlatformToolset v$ts > v120, auto-fix 为 v120 (本机无 v143 编译器)"
            (Get-Content $vcx.FullName -Raw) -replace "v$ts", 'v120' | Set-Content $vcx.FullName -NoNewline
            Write-OK "已修复: v$ts -> v120"
        } else {
            Write-OK "PlatformToolset: v$ts"
        }
    }
}

# ---- 4. 构建 ----
$target = if ($Incremental) { "Build" } else { "Rebuild" }
$configs = if ($Config -eq "Both") { @("Release", "Debug") } else { @($Config) }
$fail = $false

foreach ($cfg in $configs) {
    Write-Step "构建 [$cfg]  target=$target  platform=$Platform"
    $out = & $msbuild $buildFile.FullName "/t:$target" "/p:Configuration=$cfg" "/p:Platform=$Platform" /m /v:minimal /nologo 2>&1
    $code = $LASTEXITCODE
    if ($LogFile) { $out | ForEach-Object { Add-BuildLog ("$_") } }
    $errs = @($out | Where-Object { $_ -match 'error C\d+:|error LNK\d+:|: error MSB\d+:' })
    $warns = @($out | Where-Object { $_ -match 'warning C\d+:|warning LNK\d+:' })

    if ($code -eq 0) {
        Write-OK "$cfg PASSED (0 errors, $($warns.Count) warnings)"
    } else {
        Write-ERR "$cfg FAILED (exit=$code, errors=$($errs.Count))"
        $errs | Select-Object -First 20 | ForEach-Object { Write-Host ("  " + $_) -ForegroundColor Red }
        $fail = $true
    }
}

$sw.Stop()
$elapsed = [math]::Round($sw.Elapsed.TotalSeconds, 1)
if ($fail) {
    Write-ERR "构建失败, 总耗时 ${elapsed}s"; exit 1
} else {
    Add-BuildLog "completed=pass elapsedSeconds=$elapsed"
    Write-Host "`n=== 全部完成, 总耗时 ${elapsed}s ===" -ForegroundColor Green
    exit 0
}
