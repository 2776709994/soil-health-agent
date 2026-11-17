$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$project = Resolve-Path (Join-Path $root "..")

if (-not $env:MINIMAX_API_KEY) {
    Write-Host '请先设置 $env:MINIMAX_API_KEY' -ForegroundColor Yellow
    exit 1
}

Set-Location $project
python -m uvicorn server.main:app --host 127.0.0.1 --port 8000
