$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not $Root) { $Root = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent }

$Front = Join-Path $Root "src\frontend"
$Chat = Join-Path $Root "src\monorepos\e2e-chatbot-app-next"
$Dash = Join-Path $Root "src\monorepos\aibi-dashboards-external-embedding"

foreach ($dir in @($Front, $Chat, $Dash)) {
  if (-not (Test-Path $dir)) { throw "pasta ausente: $dir" }
}

if (-not (Test-Path (Join-Path $Front "node_modules"))) {
  Push-Location $Front; npm install; Pop-Location
}
if (-not (Test-Path (Join-Path $Chat "node_modules"))) {
  Push-Location $Chat; npm install; Pop-Location
}
if (-not (Test-Path (Join-Path $Dash "frontend\node_modules"))) {
  Push-Location (Join-Path $Dash "frontend"); npm install; Pop-Location
}

try {
  python -c "import flask" | Out-Null
} catch {
  Push-Location (Join-Path $Dash "backend")
  python -m pip install -r requirements.txt
  Pop-Location
}

Write-Host "3020 institucional  http://localhost:3020/"
Write-Host "3030 chats          http://localhost:3030/  (via /sdk/chatbot)"
Write-Host "3010 paineis        http://localhost:3010/  (via /sdk/dashboards)"
Write-Host "Feche as janelas abertas para parar."

Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Dash\backend'; python app.py"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Dash\frontend'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Chat'; `$env:CHAT_APP_PORT='3031'; `$env:PORT='3030'; `$env:BACKEND_URL='http://localhost:3031'; npm run dev"
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location '$Front'; npx next dev -p 3020"
