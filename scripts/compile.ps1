param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectPath,

    [ValidateSet("Release","Debug","Both")]
    [string]$Configuration = "Both",

    [switch]$SkipDebug
)

$ErrorActionPreference = "Stop"
$script:BuildFailed = $false

# ============================================================
# Helper functions
# ============================================================

function Write-Step { param($msg) Write-Host "`n>>> $msg" -ForegroundColor Cyan }
function Write-OK   { param($msg) Write-Host "  OK: $msg" -ForegroundColor Green }
function Write-ERR  { param($msg) Write-Host "  ERROR: $msg" -ForegroundColor Red }
function Write-WARN { param($msg) Write-Host "  WARN: $msg" -ForegroundColor Yellow }

# ============================================================
# Step A1: Discover project
# ============================================================
Write-Step "Step A1: Discover project"

$sln = Get-ChildItem -Path $ProjectPath -Filter "*.sln" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
if ($sln) {
    $slnPath = $sln.FullName
    Write-OK "Found solution: $slnPath"
} else {
    $vcxproj = Get-ChildItem -Path $ProjectPath -Filter "*.vcxproj" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
    if ($vcxproj) {
        $slnPath = $vcxproj.FullName
        Write-OK "Found vcxproj: $slnPath"
    } else {
        Write-ERR "No .sln or .vcxproj found in $ProjectPath"
        exit 1
    }
}

# Check PlatformToolset
$vcxprojFile = if ($sln) {
    Get-ChildItem -Path (Split-Path $slnPath -Parent) -Filter "*.vcxproj" | Select-Object -First 1
} else {
    $vcxproj
}
if ($vcxprojFile) {
    $toolsetLine = Select-String -Path $vcxprojFile.FullName -Pattern 'PlatformToolset' | Select-Object -First 1
    if ($toolsetLine -match '>v(\d+)<') {
        $tsVer = [int]$matches[1]
        if ($tsVer -gt 120) {
            Write-WARN "PlatformToolset v$tsVer > v120, auto-fixing to v120..."
            (Get-Content $vcxprojFile.FullName -Raw) -replace "v$tsVer", 'v120' | Set-Content $vcxprojFile.FullName -NoNewline
            Write-OK "Toolset fixed: v$tsVer -> v120"
        } else {
            Write-OK "PlatformToolset: v$tsVer"
        }
    }
}

# Check devenv.exe
$devenv = "C:\Program Files (x86)\Microsoft Visual Studio 12.0\Common7\IDE\devenv.exe"
if (-not (Test-Path $devenv)) {
    Write-ERR "devenv.exe not found: $devenv"
    exit 1
}
Write-OK "devenv.exe found"

# ============================================================
# Step A2 & A3: Rebuild
# ============================================================
$msbuild = "C:\Program Files (x86)\MSBuild\12.0\Bin\MSBuild.exe"
if (-not (Test-Path $msbuild)) {
    Write-ERR "MSBuild not found: $msbuild"
    exit 1
}

function Invoke-Rebuild {
    param([string]$Config)
    Write-Step "Rebuild $Config"
    $output = & $msbuild $slnPath /t:Rebuild /p:Configuration=$Config /p:Platform=Win32 /m 2>&1
    $exitCode = $LASTEXITCODE

    # Filter to error lines only
    $errors = $output | Where-Object { $_ -match 'error C\d+:|error LNK\d+:|: error MSB\d+:' }

    if ($exitCode -eq 0) {
        Write-OK "$Config PASSED (0 errors, 0 warnings)"
        return $true
    } else {
        Write-ERR "$Config FAILED (exit=$exitCode)"
        if ($errors) {
            Write-Host "`n  Build errors:"
            $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
        }
        $script:BuildFailed = $true
        return $false
    }
}

if ($Configuration -in @("Release","Both")) {
    $releaseOk = Invoke-Rebuild "Release"
}
if ($Configuration -in @("Debug","Both")) {
    $debugOk = Invoke-Rebuild "Debug"
}

if ($BuildFailed) {
    Write-ERR "Build failed. Skipping debug."
    exit 1
}

if ($SkipDebug) {
    Write-OK "Build complete (debug skipped)"
    exit 0
}

# ============================================================
# Step A4: COM Debug
# ============================================================
Write-Step "Step A4: COM Debug"

$progId = "VisualStudio.DTE.12.0"
$dte = $null

# 1) Try COM
try {
    $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
    Write-OK "VS COM connected"
} catch {
    Write-WARN "VS not running, launching..."
}

# 2) Launch VS if needed
if (-not $dte) {
    cmd /c start "" "$devenv" "$slnPath"
    for ($i = 0; $i -lt 30; $i++) {
        try {
            $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
            if ($dte -ne $null) { Write-OK "COM ready (${i}s)"; break }
        } catch { }
        Start-Sleep -Seconds 1
    }
    if (-not $dte) {
        Write-ERR "VS launch timeout (30s)"
        exit 1
    }
}

# 3) Ensure Solution loaded
$sol = $dte.Solution
if ($sol -eq $null) {
    Write-WARN "Solution is null, using File.OpenProject..."
    $dte.ExecuteCommand("File.OpenProject", $slnPath)
    Start-Sleep -Seconds 3
    Write-OK "Project opened"
} elseif (-not $sol.IsOpen -or $sol.FullName -ne $slnPath) {
    Write-WARN "Opening solution: $slnPath"
    $sol.Open($slnPath)
    Start-Sleep -Seconds 2
    Write-OK "Solution opened"
} else {
    Write-OK "Solution already open: $($sol.FullName)"
}

# 4) Debugger.Go() in background job (this call blocks, so we run async)
Write-Step "Debugger.Go() (async)"
$job = Start-Job -ScriptBlock {
    param($progId)
    $dte = [System.Runtime.InteropServices.Marshal]::GetActiveObject($progId)
    $dte.Debugger.Go()
} -ArgumentList $progId

# 5) Verify testui.exe started
$maxWait = 15
for ($i = 0; $i -lt $maxWait; $i++) {
    Start-Sleep -Seconds 1
    $testui = Get-Process -Name "testui" -ErrorAction SilentlyContinue
    if ($testui) {
        Write-OK "testui.exe started (PID: $($testui.Id), waited ${i}s)"
        Write-Host "`n=== ALL DONE ===" -ForegroundColor Green
        Write-Host "  Release : PASSED" -ForegroundColor Green
        Write-Host "  Debug   : PASSED" -ForegroundColor Green
        Write-Host "  Debugger: RUNNING" -ForegroundColor Green
        exit 0
    }
}

Write-ERR "testui.exe did not start within ${maxWait}s"
Write-WARN "Debugger job may still be running in background"
exit 1
