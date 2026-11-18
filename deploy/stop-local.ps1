$ErrorActionPreference = "Stop"

$deployRoot = "D:\develop\soil-web"
$nginxHome = "D:\develop\nginx-1.28.3"
$nginx = Join-Path $nginxHome "nginx.exe"
$nginxPrefix = Join-Path $deployRoot "nginx"

try {
    & $nginx -p "$nginxPrefix\" -c "conf/nginx.conf" -s stop 2>$null | Out-Null
} catch {}

foreach ($name in @("api", "mcp")) {
    $pidFile = Join-Path $deployRoot "$name.pid"
    if (Test-Path $pidFile) {
        $pidValue = Get-Content $pidFile -ErrorAction SilentlyContinue
        if ($pidValue) {
            try { Stop-Process -Id ([int]$pidValue) -Force -ErrorAction Stop } catch {}
        }
        Remove-Item $pidFile -Force -ErrorAction SilentlyContinue
    }
}

Write-Host "本地部署已停止。" -ForegroundColor Green
