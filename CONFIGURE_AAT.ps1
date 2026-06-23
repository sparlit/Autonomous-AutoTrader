Write-Host '⚙️ Autonomous AutoTrader - Quick Configuration' -ForegroundColor Yellow

$configPath = 'config\main_config.json'
if (-not (Test-Path $configPath)) {
    Write-Host '[ERROR] Configuration file missing.' -ForegroundColor Red
    exit
}

$config = Get-Content $configPath | ConvertFrom-Json

Write-Host "Current Threshold: $($config.brains.consensus_threshold)"
Write-Host "Current Daily Loss: $($config.risk.daily_loss_limit_pct)%"

$newThreshold = Read-Host 'Enter new Consensus Threshold (or press Enter to keep)'
if ($newThreshold) { $config.brains.consensus_threshold = [double]$newThreshold }

$newLoss = Read-Host 'Enter new Daily Loss Limit % (or press Enter to keep)'
if ($newLoss) { $config.risk.daily_loss_limit_pct = [double]$newLoss }

$config | ConvertTo-Json -Depth 10 | Set-Content $configPath
Write-Host '[SUCCESS] Configuration updated.' -ForegroundColor Green
