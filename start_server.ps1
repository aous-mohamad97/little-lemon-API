# PowerShell script to start Django server
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Starting Django Development Server" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Set-Location $PSScriptRoot
& .\venv\Scripts\Activate.ps1
python manage.py runserver
