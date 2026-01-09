# PowerShell script to download MSYS2 installer
# Run this with: powershell -ExecutionPolicy Bypass -File download_msys2.ps1

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "QMK Firmware - MSYS2 Installer Download" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$msys2Url = "https://github.com/msys2/msys2-installer/releases/latest/download/msys2-x86_64-latest.exe"
$installerPath = "$PSScriptRoot\msys2-installer.exe"

Write-Host "Downloading MSYS2 installer..." -ForegroundColor Yellow
Write-Host "URL: $msys2Url" -ForegroundColor Gray
Write-Host "Saving to: $installerPath" -ForegroundColor Gray
Write-Host ""

try {
    # Download with progress
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $msys2Url -OutFile $installerPath -UseBasicParsing
    $ProgressPreference = 'Continue'

    Write-Host "✓ Download complete!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Run the installer: $installerPath" -ForegroundColor White
    Write-Host "2. Install to default location: C:\msys64" -ForegroundColor White
    Write-Host "3. After installation, run: .\setup_qmk.bat" -ForegroundColor White
    Write-Host ""

    # Ask if they want to run installer now
    $response = Read-Host "Would you like to run the installer now? (Y/N)"
    if ($response -eq 'Y' -or $response -eq 'y') {
        Write-Host "Launching installer..." -ForegroundColor Yellow
        Start-Process -FilePath $installerPath -Wait

        Write-Host ""
        Write-Host "✓ Installation complete!" -ForegroundColor Green
        Write-Host "Now run: .\setup_qmk.bat to continue" -ForegroundColor Cyan
    }

} catch {
    Write-Host "✗ Error downloading MSYS2:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Please download manually from: https://www.msys2.org/" -ForegroundColor Yellow
    exit 1
}
