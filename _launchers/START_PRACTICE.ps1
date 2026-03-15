$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location -Path $scriptPath

$venvPython = ".\.venv\Scripts\pythonw.exe"

if (Test-Path $venvPython) {
    Start-Process $venvPython -ArgumentList "START_PRACTICE.py" -WindowStyle Hidden
} else {
    Start-Process pythonw -ArgumentList "START_PRACTICE.py" -WindowStyle Hidden
}
