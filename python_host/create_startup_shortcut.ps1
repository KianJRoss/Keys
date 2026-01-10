# Create startup shortcut for Keychron Menu System

$WshShell = New-Object -ComObject WScript.Shell
$StartupFolder = "$env:APPDATA\Microsoft\Windows\Start Menu\Programs\Startup"
$ShortcutPath = Join-Path $StartupFolder "Keychron Menu.lnk"

$Shortcut = $WshShell.CreateShortcut($ShortcutPath)
$Shortcut.TargetPath = "C:\Keyboard\Keys\python_host\venv\Scripts\pythonw.exe"
$Shortcut.Arguments = "C:\Keyboard\Keys\python_host\keychron_app.py"
$Shortcut.WorkingDirectory = "C:\Keyboard\Keys\python_host"
$Shortcut.Description = "Keychron V1 Menu System"
$Shortcut.IconLocation = "C:\Windows\System32\shell32.dll,176"  # Keyboard icon
$Shortcut.Save()

Write-Host "Shortcut created successfully at: $ShortcutPath"
Write-Host "The Keychron Menu System will now start automatically on boot."
