# dte_rebuild.ps1 — 通过 COM 触发已运行 VS IDE 的 Rebuild Solution (含诊断 + fallback)
$ErrorActionPreference = "Continue"
$progId = "VisualStudio.DTE.12.0"
$slnPath = "D:\PROJECT6-DALI\devel\source\F12011.sln"
$dllPath = "D:\PROJECT6-DALI\devel\F12011.dll"

function Write-Step { param($m) Write-Host ("`n>>> " + $m) -ForegroundColor Cyan }
function Write-OK   { param($m) Write-Host ("  OK: " + $m) -ForegroundColor Green }
function Write-WARN { param($m) Write-Host ("  WARN: " + $m) -ForegroundColor Yellow }
function Write-ERR  { param($m) Write-Host ("  ERROR: " + $m) -ForegroundColor Red }

Write-Step "Step 1: 连接运行中的 VS 实例"
try {
    $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
} catch {
    Write-ERR "未找到运行中的 VS 实例: $_"; exit 1
}
Write-OK "已连接 $($dte.Name) $($dte.Version), DTE类型=$($dte.GetType().FullName)"
try { $dte.MainWindow.Activate() } catch {}

Write-Step "Step 2: 确认解决方案"
$sol = $dte.Solution
if ($sol -and $sol.FullName -ieq $slnPath -and $sol.IsOpen) {
    Write-OK "解决方案已打开: $($sol.FullName)"
} else {
    if ($sol -and $sol.FullName) { Write-WARN "当前打开: $($sol.FullName)" }
    $sol.Open($slnPath); Start-Sleep -Seconds 3
    Write-OK "已打开: $($sol.FullName)"
}

Write-Step "Step 3: 获取 SolutionBuild (多方式尝试)"
$sb = $null
try { $sb = $dte.SolutionBuild } catch { Write-WARN "dte.SolutionBuild 异常: $_" }
if ($null -eq $sb) { try { $sb = $sol.SolutionBuild } catch { Write-WARN "sol.SolutionBuild 异常: $_" } }
if ($null -eq $sb) {
    try {
        $bf = [System.Reflection.BindingFlags]::GetProperty
        $sb = $dte.GetType().InvokeMember("SolutionBuild", $bf, $null, $dte, $null)
    } catch { Write-WARN "InvokeMember 异常: $_" }
}
Write-OK "SolutionBuild 获取: $(if ($null -eq $sb) {'失败'} else {'成功: ' + $sb.GetType().FullName})"

# 记录构建前 DLL 时间戳 (用于 fallback 轮询)
$preTime = if (Test-Path $dllPath) { (Get-Item $dllPath).LastWriteTime } else { Get-Date }

if ($null -ne $sb) {
    Write-Step "Step 4a: SolutionBuild.Clean + Build (等待完成)"
    try {
        $sb.Clean($true)
        $sb.Build($true)
        Start-Sleep -Seconds 2
        $info = $sb.LastBuildInfo
        if ($info) {
            Write-OK "构建结果 Errors=$($info.Errors) Warnings=$($info.Warnings)"
            exit 0
        }
        Write-WARN "未取到 LastBuildInfo"
    } catch {
        Write-ERR "SolutionBuild 调用失败: $_"
        Write-WARN "改用 ExecuteCommand fallback..."
    }
}

# ---- fallback: ExecuteCommand 触发 IDE 菜单 Rebuild Solution ----
Write-Step "Step 4b: fallback — ExecuteCommand(Build.RebuildSolution)"
try {
    $dte.ExecuteCommand("Build.RebuildSolution")
    Write-OK "已触发 IDE Rebuild Solution (异步), 构建过程请查看 VS 输出窗口"
} catch {
    Write-ERR "ExecuteCommand 失败: $_"; exit 1
}

Write-Step "Step 5: 轮询 F12011.dll 重建 (最长 300s)"
for ($i = 0; $i -lt 150; $i++) {
    Start-Sleep -Seconds 2
    if (Test-Path $dllPath) {
        $now = (Get-Item $dllPath).LastWriteTime
        if ($now -gt $preTime.AddSeconds(1)) {
            Write-OK "检测到 F12011.dll 已重建: $now (已等待 $($i*2)s)"
            Start-Sleep -Seconds 5
            exit 0
        }
    }
}
Write-WARN "300s 内未检测到 DLL 重建 (可能构建仍在进行或有对话框阻塞)"
exit 1
