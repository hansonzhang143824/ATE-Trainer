# dte_buildcheck.ps1 — 综合验证 VS 构建状态 (不吞异常)
$ErrorActionPreference = "Continue"
$progId = "VisualStudio.DTE.12.0"

Write-Host "=== A) F12011.dll 当前状态 ===" -ForegroundColor Cyan
$dll = Get-Item "D:\PROJECT6-DALI\devel\F12011.dll" -ErrorAction SilentlyContinue
if ($dll) { Write-Host ("  " + $dll.LastWriteTime + "  " + $dll.Length + " bytes") }
else { Write-Host "  [缺失] F12011.dll" }

Write-Host "`n=== B) 所有 devenv 进程 ===" -ForegroundColor Cyan
Get-Process devenv -ErrorAction SilentlyContinue | ForEach-Object {
    Write-Host ("  PID=" + $_.Id + "  Started=" + $_.StartTime + "  Mem=" + [int]($_.WorkingSet64/1MB) + "MB")
}

Write-Host "`n=== C) 输出窗口面板 (完整错误) ===" -ForegroundColor Cyan
try {
    $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
    Write-Host ("  已连接 " + $dte.Name + " " + $dte.Version)
    $op = $dte.ToolWindows.OutputWindow
    Write-Host ("  OutputWindow 对象类型: " + $op.GetType().FullName)
    $n = $op.OutputWindowPanes.Count
    Write-Host ("  面板数量: " + $n)
    for ($i = 0; $i -lt $n; $i++) {
        try {
            $pane = $op.OutputWindowPanes.Item($i)
            Write-Host ("    [$i] " + $pane.Name)
        } catch { Write-Host ("    [$i] 读取失败: " + $_.Exception.Message) }
    }
    # 尝试直接激活输出窗口
    try { $op.Activate(); Write-Host "  [OK] 已激活输出窗口" } catch { Write-Host "  [WARN] Activate失败: $($_.Exception.Message)" }
} catch {
    Write-Host ("  [ERR] " + $_.Exception.Message)
}

Write-Host "`n=== D) 最近构建相关文件 ===" -ForegroundColor Cyan
Get-ChildItem "D:\PROJECT6-DALI\devel\source\Release" -Filter "*.obj" -ErrorAction SilentlyContinue |
    Sort-Object LastWriteTime -Descending | Select-Object -First 3 |
    ForEach-Object { Write-Host ("  " + $_.LastWriteTime + "  " + $_.Name) }
