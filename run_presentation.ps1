# PowerShell script to open the presentation
Write-Host "Opening TwelveLabs Presentation..." -ForegroundColor Cyan
Start-Process "presentation.html"
Write-Host ""
Write-Host "Presentation opened in your default browser!" -ForegroundColor Green
Write-Host ""
Write-Host "Navigation:" -ForegroundColor Yellow
Write-Host "  - Use Arrow Keys (Left/Right) to navigate"
Write-Host "  - Or click Previous/Next buttons at the bottom"
Write-Host ""
Read-Host "Press Enter to exit"



