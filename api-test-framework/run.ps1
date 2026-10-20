param(
    [string[]]$PytestArgs = @()
)

$ErrorActionPreference = "Stop"
if (-not $env:API_BASE_URL) {
    $env:API_BASE_URL = "http://127.0.0.1:8081"
}

Write-Host "执行接口自动化用例..." -ForegroundColor Cyan
python -m pytest $PytestArgs
$exitCode = $LASTEXITCODE

$allureHome = if ($env:ALLURE_HOME) { $env:ALLURE_HOME } else { Join-Path $env:USERPROFILE "allure-cli\allure-2.29.0" }
$allureBat = Join-Path $allureHome "bin\allure.bat"

if (Get-Command allure -ErrorAction SilentlyContinue) {
    $allureExe = (Get-Command allure).Source
} elseif (Test-Path $allureBat) {
    $allureExe = $allureBat
} else {
    $allureExe = $null
}

if ($allureExe) {
    Write-Host "生成 Allure 报告..." -ForegroundColor Cyan
    & $allureExe generate reports/allure-results -o reports/allure-report --clean
} else {
    Write-Host "未检测到 Allure 命令行，用例结果已保存在 reports/allure-results，安装 allure 后可生成 HTML 报告。" -ForegroundColor Yellow
}

exit $exitCode
