$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Resolve-Path (Join-Path $root "..\..")
$workspace = Join-Path $project "agent-workspace"
$dshHome = Join-Path $project "dsh-home"
$dshRoot = if ($env:DSH_RUNTIME) { $env:DSH_RUNTIME } else { "D:\develop\dsh-runtime" }
$dsh = Join-Path $dshRoot "node_modules\.bin\dsh.cmd"

if (-not $env:MINIMAX_API_KEY) {
    Write-Host '请先设置 $env:MINIMAX_API_KEY' -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $dsh)) {
    Write-Host "未找到 dsh：$dsh" -ForegroundColor Red
    exit 1
}

New-Item -ItemType Directory -Force -Path $dshHome | Out-Null
$env:DSH_HOME = $dshHome

$prompt = if ($args.Count -gt 0) { $args -join " " } else {
    "请读取 data/case.md 和 .agents/skills/soil-health/SKILL.md，诊断 5 个地块，给出分地块主要限制和 3 条路线比较。ESP/SAR/CEC 缺失时必须说明钠化不可判定。不要给精确石膏用量。"
}

Push-Location $workspace
try {
    & $dsh --profile headless --patch (Join-Path $root "minimax.patch.yml") $prompt
}
finally {
    Pop-Location
}
