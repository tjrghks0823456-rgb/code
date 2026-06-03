$ErrorActionPreference = "Stop"

function Test-PortOpen($Port) {
  $client = [System.Net.Sockets.TcpClient]::new()
  try {
    $client.Connect("127.0.0.1", $Port)
    return $true
  } catch {
    return $false
  } finally {
    $client.Dispose()
  }
}

function Wait-Port($Port, $Name) {
  for ($i = 0; $i -lt 30; $i++) {
    if (Test-PortOpen $Port) {
      Write-Host "$Name ready on port $Port" -ForegroundColor Green
      return
    }
    Start-Sleep -Seconds 1
  }
  throw "$Name did not start on port $Port."
}

$Root = Split-Path -Parent $MyInvocation.MyCommand.Path
$BackendScript = Join-Path $Root ".launcher\run_backend.ps1"
$FrontendScript = Join-Path $Root ".launcher\run_frontend.ps1"

Write-Host "Starting Unbelievable local services..." -ForegroundColor Cyan

if (-not (Test-PortOpen 8000)) {
  Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $BackendScript
  )
}

if (-not (Test-PortOpen 3000)) {
  Start-Process -WindowStyle Hidden -FilePath "powershell.exe" -ArgumentList @(
    "-NoExit",
    "-ExecutionPolicy",
    "Bypass",
    "-File",
    $FrontendScript
  )
}

Wait-Port 8000 "Backend"
Wait-Port 3000 "Frontend"

$LocalUrl = "http://127.0.0.1:3000"
$BundledCloudflared = Join-Path $Root ".launcher\cloudflared.exe"
$Cloudflared = Get-Command "cloudflared" -ErrorAction SilentlyContinue
if (-not $Cloudflared -and (Test-Path -LiteralPath $BundledCloudflared)) {
  $Cloudflared = @{ Source = $BundledCloudflared }
}

Write-Host ""
Write-Host "Local URL: $LocalUrl" -ForegroundColor Green

if (-not $Cloudflared) {
  Write-Host ""
  Write-Host "cloudflared was not found, so a public URL cannot be opened yet." -ForegroundColor Yellow
  Write-Host "Install Cloudflare Tunnel, then run this file again:" -ForegroundColor Yellow
  Write-Host "  winget install --id Cloudflare.cloudflared" -ForegroundColor White
  Write-Host ""
  Write-Host "Press Enter to close..."
  Read-Host | Out-Null
  exit 1
}

Write-Host ""
Write-Host "Opening a public tunnel. Copy the https://...trycloudflare.com URL and send it to others." -ForegroundColor Cyan
Write-Host "Keep this window open while people use the site." -ForegroundColor Yellow
Write-Host ""

& $Cloudflared.Source tunnel --url $LocalUrl
