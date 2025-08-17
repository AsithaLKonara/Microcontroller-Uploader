Write-Host "Testing J Tech Pixel Uploader Dependencies..." -ForegroundColor Cyan
Write-Host ""

try {
    python test_dependency_checker.py
} catch {
    Write-Host "Error running dependency checker: $_" -ForegroundColor Red
}

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Yellow
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
