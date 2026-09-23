# dsh-plugin-restart.ps1 - the ONLY sanctioned way to restart dsh web after plugin changes.
#
# WHY (2026-09-13/14 real incident): a plugin patch row wrote `name: ./lib/responsiveness.js`.
# dsh's loader anchors relative specifiers at the PROFILE directory (cordis.yml is rewritten every
# boot as the anchor), so it looked for profiles/web/lib/... -> ERR_MODULE_NOT_FOUND ->
# "plugin tree failed to load" -> the WHOLE web profile would not boot and the user's GUI died
# until it was repaired by hand. `dsh --profile web --dump-config` never caught it because it only
# COMPOSES config and never imports modules.
#
# Therefore: never stop the server before the gates pass. A gate that always runs:
#   gate A: resolve EVERY plugin patch mount row from the profile base (plugin-patch-gate.mjs)
#   gate B: the plugin's own test suite (if <PluginDir>\test\all.test.mjs exists)
#   gate C: `dsh --profile <Profile> --dump-config` composes without error
# Then, after boot: scan the startup log for the known load-error signatures.
#
# ASCII-only on purpose: a BOM-less .ps1 is decoded as GBK by powershell.exe.
# NOTE: param() MUST be the first statement (only comments may precede it). Putting it after an
# assignment silently drops the switches - that mistake caused an unintended full restart once.
param(
    [string]$Profile = 'web',
    [int]$Port = 3080,
    [string]$PluginDir = '',
    [string]$InstallPluginDir = '',
    [switch]$GatesOnly,
    [int]$WaitSeconds = 40
)

$ErrorActionPreference = 'Continue'

$home_      = $env:USERPROFILE
$bin        = Join-Path $home_ 'AppData\Roaming\npm\node_modules\@deepseek-ai\dsh\lib\bin.js'
$rulesDir   = Join-Path $home_ '.dsh\rules'
$gateScript = Join-Path $rulesDir 'plugin-patch-gate.mjs'
$profileDir = Join-Path $home_ ('.dsh\profiles\' + $Profile)
$stamp      = Get-Date -Format 'yyyyMMdd-HHmmss'
$outDir     = Join-Path $env:TEMP ('dsh-plugin-restart-' + $stamp)
New-Item -ItemType Directory -Force -Path $outDir | Out-Null
$status = Join-Path $outDir 'status.txt'
$result = Join-Path $outDir 'verify.txt'
$log    = Join-Path $outDir 'server.log'
$errlog = Join-Path $outDir 'server.err'

function Write-Status($m) {
    "[$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')] $m" | Out-File $status -Append -Encoding utf8
    Write-Host $m
}
function Test-Port([int]$port) {
    try {
        $c = New-Object Net.Sockets.TcpClient
        $a = $c.ConnectAsync('127.0.0.1', $port)
        $ok = $a.Wait(1500) -and $c.Connected
        $c.Close()
        return $ok
    } catch { return $false }
}
function Get-DshWebPids {
    @(Get-CimInstance Win32_Process -Filter "Name='node.exe'" -ErrorAction SilentlyContinue |
        Where-Object {
            $_.CommandLine -and
            $_.CommandLine -match 'deepseek-ai[\\/]dsh[\\/]lib[\\/]bin\.js' -and
            $_.CommandLine -match ('\b' + $Profile + '\b')
        } | Select-Object -ExpandProperty ProcessId)
}
function Abort-Gate($which, $output) {
    Write-Status ("$which FAILED -> the server was NOT stopped")
    ($which + ' FAILED. Server NOT stopped.') | Out-File $result -Encoding utf8
    ($output -split "`n" | Select-Object -Last 40) | Out-File $result -Append -Encoding utf8
    Write-Status ("details: " + $result)
    exit 2
}

$installPackageName = ''
$installRequested = $InstallPluginDir -ne ''
if ($installRequested) {
    if (-not (Test-Path -LiteralPath $InstallPluginDir -PathType Container)) {
        Abort-Gate 'install source validation' ("directory not found: " + $InstallPluginDir)
    }
    $installManifestPath = Join-Path $InstallPluginDir 'package.json'
    try {
        $installManifest = Get-Content -LiteralPath $installManifestPath -Raw | ConvertFrom-Json
        $installPackageName = [string]$installManifest.name
    } catch {
        Abort-Gate 'install source validation' ("invalid package.json: " + $_.Exception.Message)
    }
    if ($installPackageName -eq '' -or $null -eq $installManifest.dsh.bundle.patch) {
        Abort-Gate 'install source validation' 'package must declare name and dsh.bundle.patch'
    }
    if ($PluginDir -eq '') {
        $PluginDir = $InstallPluginDir
    } elseif ((Resolve-Path -LiteralPath $PluginDir).Path -ne (Resolve-Path -LiteralPath $InstallPluginDir).Path) {
        Abort-Gate 'install source validation' '-PluginDir and -InstallPluginDir must identify the same package'
    }
    try {
        # The profile package.json can be TSZ/DLP protected. PowerShell Get-Content
        # sees the encrypted container, while DSH's own plugin command has the
        # approved plaintext view and returns a stable JSON dependency inventory.
        $listOutput = (& node $bin plugin --profile $Profile list --depth 0 --json 2>&1) -join "`n"
        $listCode = $LASTEXITCODE
        if ($listCode -ne 0) {
            throw ("dsh plugin list failed with exit " + $listCode + ": " + $listOutput)
        }
        $profileInventory = @($listOutput | ConvertFrom-Json)[0]
        if ($null -ne $profileInventory.dependencies.PSObject.Properties[$installPackageName]) {
            Abort-Gate 'install source validation' ("package is already installed: " + $installPackageName)
        }
    } catch {
        if ($_.Exception.Message -like 'package is already installed:*') { throw }
        Abort-Gate 'install source validation' ("cannot inspect profile plugin inventory: " + $_.Exception.Message)
    }
}

Write-Status ("profile=" + $Profile + " port=" + $Port + " pluginDir=" + $PluginDir + " installPluginDir=" + $InstallPluginDir + " gatesOnly=" + [bool]$GatesOnly)

# ---------- gate A: patch mount rows must resolve from the profile base ----------
if (-not (Test-Path $gateScript)) {
    Abort-Gate 'gate A (patch gate script missing)' $gateScript
}
$gateA = (& node $gateScript $profileDir 2>&1) -join "`n"
$gateACode = $LASTEXITCODE
$gateA | Out-File (Join-Path $outDir 'gateA-patch-rows.txt') -Encoding utf8
Write-Status "gate A exit=$gateACode"
if ($gateACode -ne 0) { Abort-Gate 'gate A (patch mount rows)' $gateA }

# ---------- gate B: the plugin's own test suite ----------
if ($PluginDir -ne '') {
    $testEntry = Join-Path $PluginDir 'test\all.test.mjs'
    if (Test-Path $testEntry) {
        Push-Location $PluginDir
        $gateB = (& node 'test/all.test.mjs' 2>&1) -join "`n"
        $gateBCode = $LASTEXITCODE
        Pop-Location
        $gateB | Out-File (Join-Path $outDir 'gateB-plugin-tests.txt') -Encoding utf8
        Write-Status "gate B exit=$gateBCode"
        if ($gateBCode -ne 0) { Abort-Gate 'gate B (plugin tests)' $gateB }
    } else {
        Write-Status 'gate B skipped (no test/all.test.mjs in PluginDir)'
    }
} else {
    Write-Status 'gate B skipped (no -PluginDir given)'
}

# ---------- gate C: config composition ----------
$gateC = (& node $bin --profile $Profile --dump-config 2>&1) -join "`n"
$gateCCode = $LASTEXITCODE
Write-Status "gate C exit=$gateCCode"
if ($gateCCode -ne 0) { Abort-Gate 'gate C (dump-config)' $gateC }

if ($GatesOnly) {
    Write-Status 'gates-only run: all gates passed, server untouched'
    ('GATES ONLY OK. Server untouched. Artifacts: ' + $outDir) | Out-File $result -Encoding utf8
    exit 0
}

# ---------- the wait exists so the message that launched this script is delivered ----------
if ($WaitSeconds -gt 0) {
    Write-Status ("waiting " + $WaitSeconds + "s so the previous message can be delivered")
    Start-Sleep -Seconds $WaitSeconds
}

$old = @(Get-DshWebPids)
Write-Status ("old pids: " + ($old -join ','))
$installAttempted = $false
$installSucceeded = $false
$operationFailed = $false
if ($installRequested) {
    Copy-Item -LiteralPath (Join-Path $profileDir 'package.json') -Destination (Join-Path $outDir 'profile-package.before.json') -Force
    foreach ($metadataName in @('pnpm-lock.yaml', 'pnpm-workspace.yaml')) {
        $metadataPath = Join-Path $profileDir $metadataName
        if (Test-Path -LiteralPath $metadataPath) {
            Copy-Item -LiteralPath $metadataPath -Destination (Join-Path $outDir ($metadataName + '.before')) -Force
        }
    }
    Write-Status ("first-install rollback metadata saved for " + $installPackageName)
}
try {
    foreach ($t in $old) {
        $out = (& taskkill.exe /F /PID $t 2>&1) -join ' '
        Write-Status ("taskkill $t -> " + $out)
    }
    foreach ($i in 1..30) { if ((Get-DshWebPids).Count -eq 0) { break }; Start-Sleep -Seconds 1 }
    $remainingPids = @(Get-DshWebPids)
    $portFreed = -not (Test-Port $Port)
    Write-Status ("port " + $Port + " freed: " + $portFreed)
    if ($installRequested -and ($remainingPids.Count -gt 0 -or -not $portFreed)) {
        throw 'first install refused because the old server did not stop cleanly'
    }
    if ($installRequested) {
        $installAttempted = $true
        $addOutput = (& node $bin plugin --profile $Profile add ("link:" + $InstallPluginDir) 2>&1) -join "`n"
        $addCode = $LASTEXITCODE
        $addOutput | Out-File (Join-Path $outDir 'install.txt') -Encoding utf8
        Write-Status ("first install exit=" + $addCode + " package=" + $installPackageName)
        if ($addCode -ne 0) { throw ("plugin install failed with exit " + $addCode) }

        $postA = (& node $gateScript $profileDir 2>&1) -join "`n"
        $postACode = $LASTEXITCODE
        $postA | Out-File (Join-Path $outDir 'gateA-post-install.txt') -Encoding utf8
        Write-Status ("post-install gate A exit=" + $postACode)
        if ($postACode -ne 0) { throw 'post-install gate A failed' }

        $postC = (& node $bin --profile $Profile --dump-config 2>&1) -join "`n"
        $postCCode = $LASTEXITCODE
        $postC | Out-File (Join-Path $outDir 'gateC-post-install.txt') -Encoding utf8
        Write-Status ("post-install gate C exit=" + $postCCode)
        if ($postCCode -ne 0) { throw 'post-install gate C failed' }
        $installSucceeded = $true
    }
} catch {
    $operationFailed = $true
    Write-Status ("ERROR during stop: " + $_.Exception.Message)
    if ($installRequested -and $installAttempted -and -not $installSucceeded) {
        $removeOutput = (& node $bin plugin --profile $Profile remove $installPackageName 2>&1) -join "`n"
        $removeCode = $LASTEXITCODE
        $removeOutput | Out-File (Join-Path $outDir 'rollback-remove.txt') -Encoding utf8
        Write-Status ("first-install rollback remove exit=" + $removeCode)
        $rollbackA = (& node $gateScript $profileDir 2>&1) -join "`n"
        $rollbackACode = $LASTEXITCODE
        Write-Status ("rollback gate A exit=" + $rollbackACode)
        if ($removeCode -ne 0 -or $rollbackACode -ne 0) {
            Write-Status 'ROLLBACK WARNING: profile metadata may require manual recovery from the saved before files'
        }
    }
} finally {
    Remove-Item $log, $errlog -ErrorAction SilentlyContinue
    Start-Process node -ArgumentList "`"$bin`"", 'web', '--no-open' `
        -RedirectStandardOutput $log -RedirectStandardError $errlog -WindowStyle Hidden
    Write-Status 'server start attempted (finally)'
}

$up = $false
foreach ($i in 1..45) {
    Start-Sleep -Seconds 2
    $now = @(Get-DshWebPids)
    $new = @($now | Where-Object { $old -notcontains $_ })
    if ($new.Count -gt 0 -and (Test-Port $Port)) { $up = $true; break }
}
Write-Status ("boot up: " + $up)
Start-Sleep -Seconds 6

$lines = @()
if ($up) { $lines += ('port ' + $Port + ' up') } else { $lines += ('BOOT FAILED on port ' + $Port) }

# ---------- post-check: the known load-error signatures ----------
$loadError = @(Select-String -Path $log, $errlog -Pattern 'plugin tree failed to load|ERR_MODULE_NOT_FOUND|ERR_PACKAGE_PATH_NOT_EXPORTED|input hint must not be empty' -ErrorAction SilentlyContinue)
if ($loadError.Count -gt 0) {
    $lines += 'PLUGIN LOAD ERROR DETECTED:'
    foreach ($e in $loadError) { $lines += ('  ' + $e.Line.Trim()) }
} else {
    $lines += 'plugin load: no known load-error signature in the startup log'
}

try {
    $home1 = Invoke-WebRequest -Uri ("http://127.0.0.1:$Port/") -UseBasicParsing -TimeoutSec 20
    $lines += ('GET / -> ' + $home1.StatusCode)
} catch {
    $lines += ('VERIFY ERROR: ' + $_.Exception.Message)
}

$lines | Out-File $result -Encoding utf8
Write-Status ('verify written -> ' + $result)
Write-Status ('artifacts dir: ' + $outDir)
if ($operationFailed -or -not $up -or $loadError.Count -gt 0) { exit 1 }
exit 0
