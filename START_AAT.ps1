# Phoenix Ascendant: Unified Setup, Configure and Launch Script
# Version: V3.0-AUTONOMOUS (Institutional Pro)

$ErrorActionPreference = "Stop"
Write-Host "Launching Autonomous AutoTrader: Phoenix Ascendant" -ForegroundColor Cyan

# 1. Verification
Write-Host "Verifying environment..." -ForegroundColor Yellow
if (Get-Command python -ErrorAction SilentlyContinue) {
    $pyVer = python --version
    Write-Host "[OK] Python found: $pyVer" -ForegroundColor Green
} else {
    Write-Host "[ERROR] Python not found. Please install Python 3.11+" -ForegroundColor Red
    return
}

# 2. Virtual Environment Setup
if (-not (Test-Path "venv")) {
    Write-Host "Creating Virtual Environment..." -ForegroundColor Yellow
    python -m venv venv
    Write-Host "[OK] Virtual Environment created." -ForegroundColor Green
}

# 3. Dependency Management
Write-Host "Synchronizing dependencies..." -ForegroundColor Yellow
& .\venv\Scripts\pip install -U pip 2>$null
& .\venv\Scripts\pip install -r requirements.txt
Write-Host "[OK] Dependencies synchronized." -ForegroundColor Green

# 4. Institutional Core Compilation
if (Test-Path "src\rust_institutional_core") {
    Write-Host "Building Rust Institutional Core..." -ForegroundColor Yellow
    $currentDir = Get-Location
    Set-Location src\rust_institutional_core
    try {
        & ..\..\venv\Scripts\maturin develop --release
        Write-Host "[OK] Rust institutional kernel active." -ForegroundColor Green
    } catch {
        Write-Host "[WARNING] Rust build skipped/failed. Ensure Rust/Maturin are configured." -ForegroundColor DarkYellow
    }
    Set-Location $currentDir
}

# 5. Execute System
Write-Host "Handing over to Supervisor..." -ForegroundColor Green
Write-Host "--------------------------------------------------" -ForegroundColor Gray
& .\venv\Scripts\python main_engine.py
