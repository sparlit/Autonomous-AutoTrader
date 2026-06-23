Write-Host '🚀 Firing up Autonomous AutoTrader (Phoenix Ascendant)' -ForegroundColor Green
Write-Host '-------------------------------------------------------' -ForegroundColor Green

if (-not (Test-Path 'venv')) {
    Write-Host '[ERROR] Virtual environment not found. Please run .\INSTALL_AAT.ps1 first.' -ForegroundColor Red
    exit
}

# Activate and Launch
Write-Host '[INFO] Initializing High-Concurrency Hive...' -ForegroundColor Yellow
& .\venv\Scripts\python main_engine.py
