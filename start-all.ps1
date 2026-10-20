# 一键启动：MySQL(3307) + 电商订单服务(8081) + 数字内容管理系统(8082)
# 可选环境变量：MYSQL_HOME、MYSQL_INI、DB_PORT、DB_ROOT_USER
$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $MyInvocation.MyCommand.Path

$mysqlBase = if ($env:MYSQL_HOME) { $env:MYSQL_HOME } else { "C:\Program Files\MySQL\MySQL Server 8.0" }
$mysqlIni = if ($env:MYSQL_INI) { $env:MYSQL_INI } else { Join-Path $env:USERPROFILE "mysql-portable\my.ini" }
$mysqlPort = if ($env:DB_PORT) { [int]$env:DB_PORT } else { 3307 }

function Test-Port([int]$port) {
    return [bool](Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue)
}

if (-not (Test-Port $mysqlPort)) {
    if (-not (Test-Path $mysqlIni)) {
        throw "未找到 MySQL 配置 $mysqlIni。请先启动 MySQL，或设置环境变量 MYSQL_INI 指向 my.ini。"
    }
    Write-Host "启动 MySQL ($mysqlPort)..." -ForegroundColor Cyan
    Start-Process -FilePath (Join-Path $mysqlBase "bin\mysqld.exe") `
        -ArgumentList "--defaults-file=$mysqlIni" -WindowStyle Hidden
    for ($i = 0; $i -lt 40 -and -not (Test-Port $mysqlPort); $i++) {
        Start-Sleep -Milliseconds 500
    }
}
if (-not (Test-Port $mysqlPort)) {
    $errLog = Join-Path (Split-Path -Parent $mysqlIni) "mysqld.err"
    throw "MySQL 启动失败，请查看 $errLog"
}
Write-Host "MySQL 已就绪 (127.0.0.1:$mysqlPort)" -ForegroundColor Green

if (-not (Test-Port 8081)) {
    Write-Host "启动电商订单服务 (8081)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "Set-Location '$root\ecommerce-order-service'; python -m uvicorn app.main:app --host 127.0.0.1 --port 8081"
}

$jar = "$root\digital-content-system\target\digital-content-system-1.0.0.jar"
if (-not (Test-Port 8082)) {
    if (-not (Test-Path $jar)) {
        throw "未找到可执行 Jar，请先在 digital-content-system 目录执行：mvn -DskipTests package"
    }
    Write-Host "启动数字内容管理系统 (8082)..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", `
        "Set-Location '$root\digital-content-system'; java -jar target\digital-content-system-1.0.0.jar"
}

Start-Sleep -Seconds 6
Write-Host ""
Write-Host "电商订单服务接口文档: http://127.0.0.1:8081/docs" -ForegroundColor Green
Write-Host "数字内容系统健康检查: http://127.0.0.1:8082/api/health" -ForegroundColor Green
Write-Host "测试框架: cd api-test-framework; python -m pytest" -ForegroundColor Yellow
