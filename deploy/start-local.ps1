$ErrorActionPreference = "Stop"

$project = Resolve-Path (Join-Path $PSScriptRoot "..")
$deployRoot = "D:\develop\soil-web"
$nginxHome = "D:\develop\nginx-1.28.3"
$nginx = Join-Path $nginxHome "nginx.exe"
$nginxPrefix = Join-Path $deployRoot "nginx"
$dist = Join-Path $deployRoot "dist"
$apiPort = 8000
$mcpPort = 8100
$webPort = 8080

if (-not $env:MINIMAX_API_KEY) {
    Write-Host '请先设置 $env:MINIMAX_API_KEY，再运行本脚本。' -ForegroundColor Yellow
    exit 1
}
if (-not (Test-Path $nginx)) {
    Write-Host "未找到 Nginx：$nginx" -ForegroundColor Red
    exit 1
}

function Stop-Port($port) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object {
            try { Stop-Process -Id $_.OwningProcess -Force -ErrorAction Stop } catch {}
        }
}

function Test-Port($port) {
    $client = New-Object System.Net.Sockets.TcpClient
    try {
        $iar = $client.BeginConnect("127.0.0.1", $port, $null, $null)
        if (-not $iar.AsyncWaitHandle.WaitOne(800)) { return $false }
        $client.EndConnect($iar)
        return $true
    } catch { return $false } finally { $client.Close() }
}

New-Item -ItemType Directory -Force -Path $deployRoot, $nginxPrefix, (Join-Path $nginxPrefix "conf"), (Join-Path $nginxPrefix "logs"), (Join-Path $nginxPrefix "temp") | Out-Null

# Stop previous local deployment processes on our ports
Stop-Port $apiPort
Stop-Port $mcpPort
try {
    & $nginx -p "$nginxPrefix\" -c "conf/nginx.conf" -s stop 2>$null | Out-Null
} catch {}

# Fresh static build
if (Test-Path $dist) { Remove-Item $dist -Recurse -Force }
Copy-Item (Join-Path $project "frontend\dist") $dist -Recurse -Force
Copy-Item (Join-Path $PSScriptRoot "nginx.conf") (Join-Path $nginxPrefix "conf\nginx.conf") -Force

# MCP engine
$mcp = Start-Process -FilePath "python" -ArgumentList @("-m", "engine.mcp_server") `
    -WorkingDirectory $project -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $deployRoot "mcp.out.log") `
    -RedirectStandardError (Join-Path $deployRoot "mcp.err.log")
$mcp.Id | Set-Content (Join-Path $deployRoot "mcp.pid")

# FastAPI bridge
$api = Start-Process -FilePath "python" -ArgumentList @("-m", "uvicorn", "server.main:app", "--host", "127.0.0.1", "--port", "$apiPort") `
    -WorkingDirectory $project -PassThru -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $deployRoot "api.out.log") `
    -RedirectStandardError (Join-Path $deployRoot "api.err.log")
$api.Id | Set-Content (Join-Path $deployRoot "api.pid")

# Wait for API + MCP
$ready = $false
for ($i = 0; $i -lt 40; $i++) {
    try {
        $health = Invoke-RestMethod "http://127.0.0.1:$apiPort/api/health" -TimeoutSec 2
        if ($health.ok) { $ready = $true; break }
    } catch { Start-Sleep -Milliseconds 500 }
}
if (-not $ready) {
    Write-Host "API 未启动，查看 $deployRoot\api.err.log" -ForegroundColor Red
    exit 1
}
$mcpReady = $false
for ($i = 0; $i -lt 20; $i++) {
    if (Test-Port $mcpPort) { $mcpReady = $true; break }
    Start-Sleep -Milliseconds 500
}
if (-not $mcpReady) {
    Write-Host "MCP 未监听 $mcpPort，查看 $deployRoot\mcp.err.log" -ForegroundColor Red
    exit 1
}

# Nginx
Remove-Item (Join-Path $nginxPrefix "logs\nginx.pid") -Force -ErrorAction SilentlyContinue
Start-Process -FilePath $nginx `
    -ArgumentList @("-p", "D:/develop/soil-web/nginx/", "-c", "conf/nginx.conf") `
    -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $deployRoot "nginx.out.log") `
    -RedirectStandardError (Join-Path $deployRoot "nginx.err.log") | Out-Null
Start-Sleep -Milliseconds 800
if (-not (Test-Port $webPort)) {
    Write-Host "Nginx 未监听 $webPort，查看 $nginxPrefix\logs\error.log" -ForegroundColor Red
    exit 1
}

# Firewall (needs elevation; warn if unavailable)
$isAdmin = ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
if ($isAdmin) {
    try {
        netsh advfirewall firewall delete rule name="Soil Health Agent 8080" | Out-Null
        netsh advfirewall firewall add rule name="Soil Health Agent 8080" dir=in action=allow protocol=TCP localport=$webPort profile=any | Out-Null
        Write-Host "已放行防火墙 TCP $webPort。" -ForegroundColor Green
    } catch {
        Write-Host "未能自动添加防火墙规则；如局域网访问失败，请允许 TCP $webPort。" -ForegroundColor Yellow
    }
} else {
    Write-Host "当前非管理员，跳过防火墙配置；若组员打不开页面，请用管理员 PowerShell 执行：" -ForegroundColor Yellow
    Write-Host "  netsh advfirewall firewall add rule name=`"Soil Health Agent 8080`" dir=in action=allow protocol=TCP localport=$webPort profile=any" -ForegroundColor Yellow
}

$ips = Get-NetIPAddress -AddressFamily IPv4 -ErrorAction SilentlyContinue |
    Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.254.*" -and $_.PrefixOrigin -ne "WellKnown" } |
    Select-Object -ExpandProperty IPAddress
Write-Host ""
Write-Host "部署完成。" -ForegroundColor Green
Write-Host "本机： http://127.0.0.1:$webPort/"
foreach ($ip in $ips) { Write-Host "局域网：http://$ip`:$webPort/" }
Write-Host "API：  http://127.0.0.1:$apiPort/api/health"
Write-Host "日志： $deployRoot\api.err.log / mcp.err.log / nginx\logs\error.log"
