# run.ps1  (simple, robust CLI-style)
param(
  [Parameter(Position=0)]
  [ValidateSet('help','pull','backtest','forecast','all','status')]
  [string]$cmd = 'help'
)

$ErrorActionPreference = 'Stop'

function Show-Help {
  Write-Host @"
Fuel Tracker run.ps1

Usage:
  .\run.ps1 help        # show commands
  .\run.ps1 pull        # fetch data & build panel
  .\run.ps1 backtest    # run baseline backtest
  .\run.ps1 forecast    # write 12m forecast
  .\run.ps1 all         # pull → backtest → forecast
  .\run.ps1 status      # quick status of outputs
"@
}

function Status {
  Write-Host "==> Outputs status"
  if (Test-Path outputs\panel_monthly.parquet) { Write-Host "panel_monthly.parquet : OK" } else { Write-Host "panel_monthly.parquet : MISSING" }
  if (Test-Path outputs\metrics.csv)          { Write-Host "metrics.csv            : OK" } else { Write-Host "metrics.csv            : MISSING" }
  if (Test-Path outputs\forecast_12m.csv)     { Write-Host "forecast_12m.csv       : OK" } else { Write-Host "forecast_12m.csv       : MISSING" }
}

switch ($cmd) {
  'help'     { Show-Help }
  'pull'     { python -m fueltracker.pipeline.fetch_and_build }
  'backtest' { python -m fueltracker.run_backtest --model baseline }
  'forecast' { python -m fueltracker.forecast }
  'all'      {
      python -m fueltracker.pipeline.fetch_and_build
      python -m fueltracker.run_backtest --model baseline
      python -m fueltracker.forecast
  }
  'status'   { Status }
  default    { Show-Help }
}
