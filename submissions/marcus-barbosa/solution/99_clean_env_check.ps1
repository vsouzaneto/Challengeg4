# Validação em ambiente limpo: cria um venv novo, instala só o requirements.txt, roda os testes,
# a auditoria, a exploração, o backtest e um smoke test do app (Windows PowerShell 5.1).
# Uso:  powershell -ExecutionPolicy Bypass -File 99_clean_env_check.ps1
$ErrorActionPreference = "Stop"
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $here
$venv = Join-Path $env:TEMP ("leadscorer-clean-" + (Get-Date -Format "yyyyMMdd-HHmmss"))
Write-Output "venv: $venv"
py -3.12 -m venv $venv
$py = Join-Path $venv "Scripts\python.exe"
& $py -m pip install --quiet --disable-pip-version-check -r requirements.txt
Write-Output "--- versoes"
& $py -c "import pandas, numpy, streamlit, scipy, pytest; print('pandas', pandas.__version__, '| numpy', numpy.__version__, '| streamlit', streamlit.__version__, '| scipy', scipy.__version__)"
Write-Output "--- testes"
& $py -m pytest -q tests
Write-Output "--- auditoria, exploracao, backtest"
& $py 01_audit.py | Select-Object -First 3
& $py 02_explore.py | Select-Object -Last 2
& $py 03_backtest.py | Select-Object -First 6
Write-Output "--- smoke test do app (10 s)"
$proc = Start-Process -FilePath $py -ArgumentList "-m streamlit run app.py --server.port 8599 --server.headless true --browser.gatherUsageStats false" -PassThru -WindowStyle Hidden
Start-Sleep -Seconds 10
try {
  $resp = Invoke-WebRequest -Uri "http://localhost:8599/_stcore/health" -UseBasicParsing -TimeoutSec 5
  Write-Output ("app health: " + $resp.StatusCode + " " + $resp.Content)
} finally {
  Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
}
Write-Output "ok: ambiente limpo validado em $venv"
