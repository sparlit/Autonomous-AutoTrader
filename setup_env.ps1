Write-Host '🌌 Phoenix Ascendant - Windows Setup Automation' -ForegroundColor Cyan

# 1. Check Python
if (Get-Command python -ErrorAction SilentlyContinue) {
    Write-Host '[INFO] Python found.' -ForegroundColor Green
} else {
    Write-Host '[ERROR] Python not found. Please install Python 3.11+' -ForegroundColor Red
    exit
}

# 2. Virtual Environment
if (-not (Test-Path 'venv')) {
    Write-Host '[INFO] Creating Virtual Environment...' -ForegroundColor Yellow
    python -m venv venv
}

# 3. Dependencies
Write-Host '[INFO] Installing Dependencies...' -ForegroundColor Yellow
& .\venv\Scripts\pip install -r requirements.txt
& .\venv\Scripts\pip install polars torch scikit-learn xgboost fastapi dearpygui maturin psutil fakeredis

# 4. Build Rust Kernels
if (Test-Path 'src\rust_institutional_core') {
    Write-Host '[INFO] Building Rust Institutional Core Kernel...' -ForegroundColor Yellow
    Set-Location src\rust_institutional_core
    & ..\..\venv\Scripts\maturin develop
    Set-Location ..\..
}

Write-Host '[SUCCESS] environment ready. Launch with: .\venv\Scripts\python main_engine.py' -ForegroundColor Green
