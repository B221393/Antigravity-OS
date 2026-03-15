$WScriptShell = New-Object -ComObject WScript.Shell

# 1. Start Logger Shortcut
$Shortcut = $WScriptShell.CreateShortcut("$env:USERPROFILE\Desktop\Start_Seminar_Logger.lnk")
$Shortcut.TargetPath = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools\start_seminar_log.bat"
$Shortcut.WorkingDirectory = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools"
$Shortcut.IconLocation = "shell32.dll,296" # Icon: Tape/Recording
$Shortcut.Save()

# 2. Stop Logger Shortcut
$Shortcut = $WScriptShell.CreateShortcut("$env:USERPROFILE\Desktop\Stop_Seminar_Logger.lnk")
$Shortcut.TargetPath = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools\stop_seminar_log.bat"
$Shortcut.WorkingDirectory = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools"
$Shortcut.IconLocation = "shell32.dll,27" # Icon: Stop/Warning
$Shortcut.Save()

# 3. Seminar Assistant App Shortcut
$Shortcut = $WScriptShell.CreateShortcut("$env:USERPROFILE\Desktop\Seminar_Assistant.lnk")
$Shortcut.TargetPath = "pythonw.exe"
$Shortcut.Arguments = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools\seminar_assistant.py"
$Shortcut.WorkingDirectory = "c:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\AI_LAB\tools"
$Shortcut.IconLocation = "shell32.dll,22" # Icon: Magnifying Glass/Search
$Shortcut.Save()

Write-Host "Shortcuts created successfully."
