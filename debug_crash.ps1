$pythonPath = "C:\Keyboard\Keys\python_host\venv\Scripts\python.exe"
$scriptPath = "C:\Keyboard\Keys\python_host\keychron_app_qt.py"
$logFile = "crash_log.txt"

Write-Host "Starting Keychron App..."
try {
    & $pythonPath $scriptPath 2>&1 | Tee-Object -FilePath $logFile
} catch {
    Write-Host "Error launching process: $_"
}

Write-Host "`nApplication exited. Check $logFile for details."
Write-Host "Press Enter to close this window..."
Read-Host