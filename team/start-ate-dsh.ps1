param(
    [switch]$DumpConfig
)

$ErrorActionPreference = 'Stop'
$workspace = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
$patch = Join-Path $workspace 'team\dsh-agent-teams.patch.yml'

if (-not (Test-Path -LiteralPath $patch)) { throw "AgentTeams patch not found: $patch" }
Set-Location -LiteralPath $workspace

if ($DumpConfig) {
    & dsh --profile web --patch $patch --dump-config
    exit $LASTEXITCODE
}

& dsh --profile web --patch $patch
exit $LASTEXITCODE
