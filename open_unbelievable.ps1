$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$Project = Join-Path $Root "projects\unbelievable"
$Backend = Join-Path $Project "backend"
$Frontend = Join-Path $Project "frontend"
$RepoZip = "https://github.com/tjrghks0823456-rgb/code/archive/refs/heads/main.zip"
$LauncherDir = Join-Path $Root ".launcher"
$UserLauncherDir = Join-Path $env:USERPROFILE ".unbelievable_launcher"
$PortableNodeVersion = "v20.11.1"
$PortableNodeName = "node-$PortableNodeVersion-win-x64"
$PortableNodeZip = "https://nodejs.org/dist/$PortableNodeVersion/$PortableNodeName.zip"

function Write-Step($message) {
    Write-Host ""
    Write-Host "==> $message" -ForegroundColor Cyan
}

function Ensure-ProjectFiles {
    $backendMain = Join-Path $Backend "app\main.py"
    $frontendPackage = Join-Path $Frontend "package.json"

    if ((Test-Path $backendMain) -and (Test-Path $frontendPackage)) {
        return
    }

    Write-Step "Local project files are missing. Downloading the latest GitHub ZIP..."
    New-Item -ItemType Directory -Force -Path $Project | Out-Null

    $tempRoot = Join-Path $env:TEMP ("unbelievable_" + [guid]::NewGuid().ToString("N"))
    $zipPath = Join-Path $tempRoot "repo.zip"
    $extractPath = Join-Path $tempRoot "extract"

    New-Item -ItemType Directory -Force -Path $tempRoot | Out-Null
    Invoke-WebRequest -Uri $RepoZip -OutFile $zipPath
    Expand-Archive -LiteralPath $zipPath -DestinationPath $extractPath -Force

    $downloadedProject = Join-Path $extractPath "code-main\projects\unbelievable"
    if (-not (Test-Path $downloadedProject)) {
        throw "Downloaded ZIP did not contain projects\unbelievable."
    }

    Copy-Item -Path (Join-Path $downloadedProject "*") -Destination $Project -Recurse -Force
    Remove-Item -LiteralPath $tempRoot -Recurse -Force

    if (-not (Test-Path $backendMain)) {
        throw "Backend main.py still not found: $backendMain"
    }
    if (-not (Test-Path $frontendPackage)) {
        throw "Frontend package.json still not found: $frontendPackage"
    }
}

function Get-PythonCommand {
    $bundledPython = Join-Path $env:USERPROFILE ".cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"
    if (Test-Path $bundledPython) {
        return $bundledPython
    }
    if (Get-Command py -ErrorAction SilentlyContinue) {
        return "py"
    }
    if (Get-Command python -ErrorAction SilentlyContinue) {
        return "python"
    }
    throw "Python was not found. Install Python or add it to PATH."
}

function Get-NodeTools {
    $systemNpm = Get-Command npm -ErrorAction SilentlyContinue
    $systemNode = Get-Command node -ErrorAction SilentlyContinue
    if ($systemNpm -and $systemNode) {
        return @{
            NodeDir = Split-Path -Parent $systemNode.Source
            Npm = $systemNpm.Source
        }
    }

    Write-Step "npm was not found. Installing portable Node.js for this project..."
    New-Item -ItemType Directory -Force -Path $UserLauncherDir | Out-Null

    $nodeRoot = Join-Path $UserLauncherDir "node"
    $nodeDir = Join-Path $nodeRoot $PortableNodeName
    $npmCmd = Join-Path $nodeDir "npm.cmd"

    if (-not (Test-Path $npmCmd)) {
        $zipPath = Join-Path $LauncherDir "$PortableNodeName.zip"
        New-Item -ItemType Directory -Force -Path $nodeRoot | Out-Null
        Invoke-WebRequest -Uri $PortableNodeZip -OutFile $zipPath
        Expand-Archive -LiteralPath $zipPath -DestinationPath $nodeRoot -Force
        Remove-Item -LiteralPath $zipPath -Force
    }

    if (-not (Test-Path $npmCmd)) {
        throw "Portable npm was not installed correctly: $npmCmd"
    }

    return @{
        NodeDir = $nodeDir
        Npm = $npmCmd
    }
}

try {
    Write-Host ""
    Write-Host "SH.SON_UNBELIEVABLE one-click launcher" -ForegroundColor White
    Write-Host "Root: $Root" -ForegroundColor DarkGray

    Ensure-ProjectFiles
    $python = Get-PythonCommand
    $nodeTools = Get-NodeTools

    New-Item -ItemType Directory -Force -Path $LauncherDir | Out-Null
    $backendScriptPath = Join-Path $LauncherDir "run_backend.ps1"
    $frontendScriptPath = Join-Path $LauncherDir "run_frontend.ps1"
    $nodeDir = $nodeTools.NodeDir
    $npm = $nodeTools.Npm

    $backendCommand = @"
`$ErrorActionPreference = "Stop"
function Test-PortOpen(`$Port) {
  `$client = [System.Net.Sockets.TcpClient]::new()
  try {
    `$client.Connect("127.0.0.1", `$Port)
    return `$true
  } catch {
    return `$false
  } finally {
    `$client.Dispose()
  }
}
`$RootPath = Resolve-Path -LiteralPath (Join-Path `$PSScriptRoot "..")
`$Root = `$RootPath.Path
`$Backend = Join-Path `$Root "projects\unbelievable\backend"
Set-Location -LiteralPath `$Backend
if (Test-PortOpen 8000) {
  Write-Host "Backend is already running on http://127.0.0.1:8000" -ForegroundColor Green
  return
}
if (-not (Test-Path "venv\Scripts\python.exe")) {
  & @'
$python
'@ -m venv venv
}
& "venv\Scripts\python.exe" -c "import fastapi, uvicorn, pydantic_settings, multipart, jinja2, httpx" 2>`$null
if (`$LASTEXITCODE -ne 0) {
  & "venv\Scripts\python.exe" -m pip install fastapi uvicorn pydantic pydantic-settings python-multipart jinja2 httpx
}
& "venv\Scripts\python.exe" -m uvicorn app.main:app --host 127.0.0.1 --port 8000
"@

    $frontendCommand = @"
`$ErrorActionPreference = "Stop"
function Test-PortOpen(`$Port) {
  `$client = [System.Net.Sockets.TcpClient]::new()
  try {
    `$client.Connect("127.0.0.1", `$Port)
    return `$true
  } catch {
    return `$false
  } finally {
    `$client.Dispose()
  }
}
`$RootPath = Resolve-Path -LiteralPath (Join-Path `$PSScriptRoot "..")
`$Root = `$RootPath.Path
`$Frontend = Join-Path `$Root "projects\unbelievable\frontend"
Set-Location -LiteralPath `$Frontend
if (Test-PortOpen 3000) {
  Write-Host "Frontend is already running on http://127.0.0.1:3000" -ForegroundColor Green
  return
}
`$env:PATH = @'
$nodeDir
'@ + ";" + `$env:PATH
if (-not (Test-Path "node_modules")) {
  & @'
$npm
'@ install
}
& (Join-Path @'
$nodeDir
'@ "node.exe") dev-server.js
"@

    Set-Content -LiteralPath $backendScriptPath -Value $backendCommand -Encoding UTF8
    Set-Content -LiteralPath $frontendScriptPath -Value $frontendCommand -Encoding UTF8

    Write-Step "Starting backend and frontend in separate windows..."
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$backendScriptPath`"" -WindowStyle Normal
    Start-Process -FilePath "powershell.exe" -ArgumentList "-NoExit", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", "`"$frontendScriptPath`"" -WindowStyle Normal

    Write-Step "Opening browser..."
    Start-Sleep -Seconds 8
    Start-Process "http://127.0.0.1:3000"

    Write-Host ""
    Write-Host "Backend:  http://127.0.0.1:8000" -ForegroundColor Green
    Write-Host "Frontend: http://127.0.0.1:3000" -ForegroundColor Green
    Write-Host ""
    Write-Host "You can close this launcher window. Keep the backend/frontend windows open while using the app."
}
catch {
    Write-Host ""
    Write-Host "[ERROR] $($_.Exception.Message)" -ForegroundColor Red
    Write-Host ""
    Write-Host "Press Enter to close..."
    Read-Host | Out-Null
    exit 1
}
