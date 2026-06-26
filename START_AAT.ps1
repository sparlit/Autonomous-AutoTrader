# Version: V3.1.4-AUTONOMOUS (Hardened RESTRUCTURE)
# 🌌 Phoenix Ascendant: Unified Setup & Launch Script

$ErrorActionPreference = "Stop"
Write-Host "🌌 Launching Autonomous AutoTrader: Phoenix Ascendant (V3.1)" -ForegroundColor Cyan

# 1. Environment Verification
Write-Host "🔍 Verifying environment..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVer = python --version
    Write-Host "[OK] Python found: $pyVer" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    return
}

# 2. Virtual Environment Lifecycle
if (-not (Test-Path "venv")) {
    Write-Host "📦 Creating Virtual Environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual Environment created." -ForegroundColor Green
}

# 3. Dependency Synchronization
Write-Host "📥 Synchronizing dependencies..." -ForegroundColor Yellow
$currentDir = Get-Location
$env:VIRTUAL_ENV = "$currentDir\venv"
& .\venv\Scripts\python.exe -m pip install -U pip 2>$null
& .\venv\Scripts\python.exe -m pip install -r requirements.txt
Write-Host "[OK] Dependencies synchronized." -ForegroundColor Green

# 4. Orchestration Handoff
Write-Host "🏁 Handing over to Phoenix Orchestrator..." -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Gray
# Use explicit absolute path to avoid module import issues
& .\venv\Scripts\python.exe main_engine.py
