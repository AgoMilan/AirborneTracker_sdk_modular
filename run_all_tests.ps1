# ================================================================
# Script: run_all_tests.ps1
# Purpose: Runs all pytest tests in the AirborneTracker project
# ================================================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "     Running AirborneTracker SDK tests" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# 1. Activate virtual environment (if available)
$venvPath = ".\venv\Scripts\Activate.ps1"
if (Test-Path $venvPath) {
    Write-Host "Activating virtual environment..." -ForegroundColor Yellow
    & $venvPath
} else {
    Write-Host "Virtual environment not found. Using system Python." -ForegroundColor DarkYellow
}

# 2. Verify pytest is available
if (-not (Get-Command pytest -ErrorAction SilentlyContinue)) {
    Write-Host "Pytest not installed. Installing..." -ForegroundColor Red
    pip install pytest -q
}

# 3. Run all tests
Write-Host ""
Write-Host "Running all tests from 'tests/'..." -ForegroundColor Yellow
Write-Host ""

$logFile = "test_results.log"
pytest -v tests | Tee-Object -FilePath $logFile

# 4. Evaluate result
if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "All tests passed successfully!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "Some tests failed. Check test_results.log for details." -ForegroundColor Red
}

Write-Host ""
Write-Host "Log saved to: $logFile" -ForegroundColor DarkCyan
Write-Host "============================================" -ForegroundColor Cyan
