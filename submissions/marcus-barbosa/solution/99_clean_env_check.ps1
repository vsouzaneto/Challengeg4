# Validação em ambiente limpo: cria um venv novo, instala só o requirements.txt, roda os testes,
# a auditoria, a exploração, o backtest e um smoke test do app (Windows PowerShell 5.1).
# Qualquer passo com exit code diferente de zero aborta. O log vai para ../docs/clean_env_check.log.
# Uso:  powershell -ExecutionPolicy Bypass -File 99_clean_env_check.ps1
$ErrorActionPreference = "Stop"
$env:PYTHONUTF8 = "1"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$log = Join-Path (Split-Path -Parent $here) "docs\clean_env_check.log"
Start-Transcript -Path $log -Force | Out-Null
function Run($label, $exe, $argv) {
  # ($args é variável automática do PowerShell; por isso o parâmetro se chama $argv)
  Write-Output "--- $label"
  & $exe @argv
  if ($LASTEXITCODE -ne 0) { Stop-Transcript | Out-Null; throw "falhou: $label (exit $LASTEXITCODE)" }
}
$venv = Join-Path $env:TEMP ("leadscorer-clean-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
Write-Output "venv: $venv | $(Get-Date -Format 'yyyy-MM-dd HH:mm')"
py -3.12 -m venv $venv
$py = Join-Path $venv "Scripts\python.exe"
Run "instalacao" $py @("-m", "pip", "install", "--quiet", "--disable-pip-version-check", "-r", "requirements.txt")
Run "versoes" $py @("-c", "import pandas, numpy, streamlit, scipy, pytest; print('pandas', pandas.__version__, '| numpy', numpy.__version__, '| streamlit', streamlit.__version__, '| scipy', scipy.__version__)")
Run "testes" $py @("-m", "pytest", "-q", "tests")
Run "auditoria" $py @("01_audit.py")
Run "exploracao" $py @("02_explore.py")
Run "backtest" $py @("03_backtest.py")
Write-Output "--- smoke test do app (12 s)"
$proc = Start-Process -FilePath $py -ArgumentList "-m streamlit run app.py --server.port 8599 --server.headless true --browser.gatherUsageStats false" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 12
try {
  $resp = Invoke-WebRequest -Uri "http://localhost:8599/_stcore/health" -UseBasicParsing -TimeoutSec 5
  if ($resp.StatusCode -ne 200) { throw "app health $($resp.StatusCode)" }
  Write-Output ("app health: " + $resp.StatusCode + " " + $resp.Content)
} finally {
  Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
Write-Output "ok: ambiente limpo validado em $venv"
Stop-Transcript | Out-Null
