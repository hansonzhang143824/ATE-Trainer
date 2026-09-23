# dte_read_buildlog.ps1 — 读取 VS 输出窗口 Build 面板的构建日志 (只读)
$ErrorActionPreference = "Continue"
$progId = "VisualStudio.DTE.12.0"
try {
    $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
} catch { Write-Host "[ERR] 未找到 VS: $_"; exit 1 }

Write-Host "=== VS 输出窗口面板列表 ===" -ForegroundColor Cyan
try {
    $op = $dte.ToolWindows.OutputWindow
    $n = $op.OutputWindowPanes.Count
    for ($i = 0; $i -lt $n; $i++) {
        $pane = $op.OutputWindowPanes.Item($i)
        $len = $pane.TextDocument.EndPoint.AbsoluteCharOffset
        Write-Host "  [$i] $($pane.Name)  字符数=$len" -ForegroundColor Green
    }
} catch { Write-Host "[ERR] 读输出窗口失败: $_"; exit 1 }

# 尝试读取 Build 面板 (中英文名都可能)
$pane = $null
try { $pane = $op.OutputWindowPanes.Item("Build") } catch {}
if (-not $pane) { try { $pane = $op.OutputWindowPanes.Item("生成") } catch {} }
if (-not $pane -and $op.OutputWindowPanes.Count -gt 0) { $pane = $op.OutputWindowPanes.Item(0) }

if ($pane) {
    Write-Host "`n=== 读取面板: $($pane.Name) ===" -ForegroundColor Cyan
    $end = $pane.TextDocument.EndPoint
    $start = $pane.TextDocument.StartPoint.CreateEditPoint()
    $all = $start.GetText($end.AbsoluteCharOffset)
    # 只显示最后 4000 字符
    if ($all.Length -gt 4000) { $all = $all.Substring($all.Length - 4000) }
    Write-Host $all
    Write-Host "`n=== (尾部日志完) ===" -ForegroundColor Cyan
} else {
    Write-Host "[WARN] 未找到任何输出面板"
}
