$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Resolve-Path (Join-Path $root "..\..")
$workspace = Join-Path $project "agent-workspace"
$dshHome = Join-Path $project "dsh-home"
$dshRoot = if ($env:DSH_RUNTIME) { $env:DSH_RUNTIME } else { "D:\develop\dsh-runtime" }
$dsh = Join-Path $dshRoot "node_modules\.bin\dsh.cmd"

if (-not $env:MINIMAX_API_KEY) {
    Write-Host "请先设置 MiniMax API Key（不要写进仓库）：" -ForegroundColor Yellow
    Write-Host '  $env:MINIMAX_API_KEY = "sk-cp-..."' -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $dsh)) {
    Write-Host "未找到 dsh：$dsh" -ForegroundColor Red
    Write-Host '请先在 dsh-runtime 目录执行：npm install @deepseek-ai/dsh@0.2.2-rc.3' -ForegroundColor Yellow
    exit 1
}

New-Item -ItemType Directory -Force -Path $dshHome | Out-Null
$env:DSH_HOME = $dshHome

Push-Location $workspace
try {
    & $dsh --profile web --patch (Join-Path $root "minimax.patch.yml") --no-open --port 3080
}
finally {
    Pop-Location
}
