@echo off
setlocal EnableExtensions
chcp 65001 >nul
set "ROOT=%~dp0"
if "%ROOT:~-1%"=="\" set "ROOT=%ROOT:~0,-1%"
cd /d "%ROOT%"

set "FULL=0"
if /I "%~1"=="--full" set "FULL=1"

echo.
echo  RavenStack Intelligence - setup e dashboard Challenge 001
if "%FULL%"=="1" echo  Modo --full: pipeline, build, verify e pytest.
echo  Pasta: %ROOT%
echo.

call :need_cmd python "Python 3" https://www.python.org/downloads/
if errorlevel 1 goto :fail
call :need_cmd node "Node.js LTS" https://nodejs.org/
if errorlevel 1 goto :fail
call :need_cmd npm "npm" https://nodejs.org/
if errorlevel 1 goto :fail

echo [1/7] Dependencias Python...
python -m pip install --upgrade pip
if errorlevel 1 goto :fail
python -m pip install -r "%ROOT%\solution\requirements.txt"
if errorlevel 1 goto :fail

call :ensure_data
if errorlevel 1 goto :fail

set "DIST=%ROOT%\solution\command-center\dist\index.html"
set "BUNDLE=%ROOT%\solution\command-center\public\data\bundle.json"
if "%FULL%"=="0" if exist "%DIST%" if exist "%BUNDLE%" (
  echo [2/7] Build e bundle ja presentes - pulando pipeline e npm.
  echo        Rode start.bat --full para refazer analise, build, verify e pytest.
  goto :serve_only
)

echo [3/7] Pipeline analitico...
cd /d "%ROOT%\solution"
python run_analysis.py
if errorlevel 1 goto :fail

echo [4/7] Command Center - npm install e build...
cd /d "%ROOT%\solution\command-center"
if not exist "node_modules\" (
  call npm install
  if errorlevel 1 goto :fail
)
call npm run build
if errorlevel 1 (
  echo Build npm falhou; tentando tsc + vite local...
  if exist "node_modules\.bin\tsc.cmd" call "node_modules\.bin\tsc.cmd" -b
  if exist "node_modules\.bin\vite.cmd" call "node_modules\.bin\vite.cmd" build
)
if not exist "dist\index.html" (
  echo ERRO: dist\index.html ausente apos o build.
  goto :fail
)

echo [5/7] Verificacao CE...
cd /d "%ROOT%\solution"
python verify_submission.py
if errorlevel 1 goto :fail

echo [6/7] Testes pytest...
python -m pytest analytics/tests/ -q
if errorlevel 1 goto :fail

:serve_only
echo [7/7] Liberando porta 8765 e iniciando servidor...
call :free_port 8765

cd /d "%ROOT%\solution"
echo.
echo  === Pronto ===
echo  http://127.0.0.1:8765
echo  Feche esta janela ou Ctrl+C para parar o servidor.
echo.
python serve_dashboard.py
goto :eof

:need_cmd
where %~1 >nul 2>&1
if errorlevel 1 (
  echo ERRO: %~2 nao encontrado no PATH.
  echo Instale em: %~3
  exit /b 1
)
exit /b 0

:ensure_data
echo [2/7] Dados RavenStack CSV...
if exist "%ROOT%\data\ravenstack_accounts.csv" if exist "%ROOT%\data\ravenstack_churn_events.csv" exit /b 0

echo   CSVs nao encontrados em data\ - tentando download Kaggle...
if not exist "%ROOT%\data\" mkdir "%ROOT%\data"
python -m pip install kaggle
if errorlevel 1 goto :data_help

pushd "%ROOT%\data"
python -m kaggle datasets download -d rivalytics/saas-subscription-and-churn-analytics-dataset -p . --unzip
if errorlevel 1 (
  popd
  goto :data_help
)
popd
if not exist "%ROOT%\data\ravenstack_accounts.csv" goto :data_help
exit /b 0

:data_help
echo.
echo  Coloque os 5 CSVs em submissions\felipe\data\ manualmente:
echo    ravenstack_accounts.csv
echo    ravenstack_subscriptions.csv
echo    ravenstack_feature_usage.csv
echo    ravenstack_support_tickets.csv
echo    ravenstack_churn_events.csv
echo.
echo  Kaggle: https://www.kaggle.com/datasets/rivalytics/saas-subscription-and-churn-analytics-dataset
echo  Auth: kaggle auth login ou variavel KAGGLE_API_TOKEN
echo  Ver: data\README.md
exit /b 1

:free_port
for /f "tokens=5" %%p in ('netstat -aon ^| findstr ":%~1" ^| findstr "LISTENING"') do (
  echo   Encerrando PID %%p na porta %~1...
  taskkill /F /PID %%p >nul 2>&1
)
exit /b 0

:fail
echo.
echo  Falhou. Corrija o erro acima e rode start.bat de novo.
exit /b 1
