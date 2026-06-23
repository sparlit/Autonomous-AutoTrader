Write-Host '🌌 Autonomous AutoTrader - Institutional Installation' -ForegroundColor Cyan
Write-Host '--------------------------------------------------' -ForegroundColor Cyan

# 1. System Verification
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host '[ERROR] Python 3.11+ is required but not found.' -ForegroundColor Red
    exit
}

# 2. Virtual Environment Setup
if (-not (Test-Path 'venv')) {
    Write-Host '[INFO] Initializing Virtual Environment...' -ForegroundColor Yellow
    python -m venv venv
}

# 3. Dependency Installation
Write-Host '[INFO] Installing Python Dependencies...' -ForegroundColor Yellow
& .\venv\Scripts\pip install -r requirements.txt
& .\venv\Scripts\pip install polars torch scikit-learn xgboost fastapi dearpygui maturin psutil fakeredis

# 4. High-Performance Kernel Compilation
if (Test-Path 'src\rust_core') {
    Write-Host '[INFO] Compiling Rust Core Kernel...' -ForegroundColor Yellow
    Set-Location src\rust_core
    & ..\..\venv\Scripts\maturin develop
    Set-Location ..\..
}

# 5. MQL5 Deployment Instructions
Write-Host '--------------------------------------------------' -ForegroundColor Cyan
Write-Host '[SUCCESS] System environment prepared.' -ForegroundColor Green
Write-Host '[ACTION] Please copy src\mql5\Experts to your MT5 Data Folder.' -ForegroundColor White
Write-Host '[ACTION] Please copy src\mql5\Include to your MT5 Data Folder.' -ForegroundColor White
Write-Host 'Launch the app with: .\LAUNCH_AAT.ps1' -ForegroundColor Cyan
