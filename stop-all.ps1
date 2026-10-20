# 停止两个业务服务与 MySQL
# 可选环境变量：MYSQL_HOME、DB_PORT、DB_ROOT_USER、DB_ROOT_PASSWORD
$ErrorActionPreference = "SilentlyContinue"
$mysqlBase = if ($env:MYSQL_HOME) { $env:MYSQL_HOME } else { "C:\Program Files\MySQL\MySQL Server 8.0" }
$mysqlPort = if ($env:DB_PORT) { [int]$env:DB_PORT } else { 3307 }
$mysqlUser = if ($env:DB_ROOT_USER) { $env:DB_ROOT_USER } else { "root" }

foreach ($port in 8081, 8082) {
    Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue |
        ForEach-Object { Stop-Process -Id $_.OwningProcess -Force }
    Write-Host "已停止端口 $port 上的进程"
}

$mysqlArgs = @("--no-defaults", "--host=127.0.0.1", "--port=$mysqlPort", "--user=$mysqlUser")
if ($env:DB_ROOT_PASSWORD) {
    $mysqlArgs += "--password=$env:DB_ROOT_PASSWORD"
}
& (Join-Path $mysqlBase "bin\mysqladmin.exe") @mysqlArgs shutdown
Write-Host "已停止 MySQL ($mysqlPort)"
