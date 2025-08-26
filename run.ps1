# Fuel Tracker PowerShell Script
# Quick run order for common operations

param(
    [Parameter(Position=0)]
    [string]$Command = "help"
)

# Define all functions in script scope
function Show-Help {
    Write-Host "Fuel Tracker - Quick Run Commands" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Commands:" -ForegroundColor Yellow
    Write-Host "  setup     - Install dependencies and setup environment"
    Write-Host "  pull      - Pull data from EIA API and build panel"
    Write-Host "  backtest  - Run baseline backtest on last 60 months"
    Write-Host "  forecast  - Generate forecast using winning model"
    Write-Host "  clean     - Clean up generated files and caches"
    Write-Host "  status    - Show current status"
    Write-Host ""
    Write-Host "Quick run order:" -ForegroundColor Green
    Write-Host "  .\run.ps1 setup     # once"
    Write-Host "  .\run.ps1 pull      # data pull → panel (writes append-only parquet + lineage log)"
    Write-Host "  .\run.ps1 backtest  # baseline backtest on last 60 months (writes metrics.csv)"
    Write-Host "  .\run.ps1 forecast  # stubbed forecast (writes forecast_12m.csv)"
}

function Invoke-Setup {
    Write-Host "🔧 Setting up Fuel Tracker environment..." -ForegroundColor Blue
    pip install -r requirements.txt
    Write-Host "✅ Setup complete!" -ForegroundColor Green
}

function Invoke-Pull {
    Write-Host "📥 Pulling data from EIA API and building panel..." -ForegroundColor Blue
    python -m fueltracker.pipeline.fetch_and_build
    Write-Host "✅ Data pull complete!" -ForegroundColor Green
}

function Invoke-Backtest {
    Write-Host "🧪 Running baseline backtest on last 60 months..." -ForegroundColor Blue
    python -m fueltracker.backtest --model baseline --last-n-months 60
    Write-Host "✅ Backtest complete!" -ForegroundColor Green
}

function Invoke-Forecast {
    Write-Host "🔮 Generating forecast using winning model..." -ForegroundColor Blue
    python -m fueltracker.forecast
    Write-Host "✅ Forecast complete!" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "🧹 Cleaning up generated files and caches..." -ForegroundColor Blue
    if (Test-Path "data/cache") { Remove-Item "data/cache/*" -Recurse -Force }
    if (Test-Path "outputs") { Remove-Item "outputs/*" -Recurse -Force }
    if (Test-Path "MODEL_CARD.md") { Remove-Item "MODEL_CARD.md" -Force }
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

function Show-Status {
    Write-Host "📊 Fuel Tracker Status:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Files:" -ForegroundColor Yellow
    if (Test-Path "outputs") {
        Get-ChildItem "outputs" | ForEach-Object { Write-Host "  $($_.Name)" }
    } else {
        Write-Host "  No outputs directory"
    }
    Write-Host ""
    Write-Host "Panel info:" -ForegroundColor Yellow
    try {
        python -c "from fueltracker.io_parquet import get_panel_info; print(get_panel_info())"
    } catch {
        Write-Host "  No panel data"
    }
    Write-Host ""
    Write-Host "Metrics:" -ForegroundColor Yellow
    if (Test-Path "outputs/metrics.csv") {
        $lineCount = (Get-Content "outputs/metrics.csv" | Measure-Object -Line).Lines
        Write-Host "  $lineCount lines in metrics.csv"
    } else {
        Write-Host "  No metrics file"
    }
    Write-Host ""
    Write-Host "Forecast:" -ForegroundColor Yellow
    if (Test-Path "outputs/forecast_12m.csv") {
        $lineCount = (Get-Content "outputs/forecast_12m.csv" | Measure-Object -Line).Lines
        Write-Host "  $lineCount lines in forecast_12m.csv"
    } else {
        Write-Host "  No forecast file"
    }
}

# Main command dispatch
switch ($Command.ToLower()) {
    "help" { Show-Help }
    "setup" { Invoke-Setup }
    "pull" { Invoke-Pull }
    "backtest" { Invoke-Backtest }
    "forecast" { Invoke-Forecast }
    "clean" { Invoke-Clean }
    "status" { Show-Status }
    default {
        Write-Host "Unknown command: $Command" -ForegroundColor Red
        Write-Host "Use '.\run.ps1 help' for available commands" -ForegroundColor Yellow
        exit 1
    }
}
