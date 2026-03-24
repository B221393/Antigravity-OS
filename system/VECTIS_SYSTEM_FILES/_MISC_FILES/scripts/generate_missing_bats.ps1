$baseDir = "c:\Users\Yuto\OneDrive - Hiroshima University\app"
$targetScript = "apps\fill_21_39\app.py"

for ($i=21; $i -le 39; $i++) {
    $filename = "$baseDir\$i`_Utility_Hub.bat"
    $content = @"
@echo off
title [$i] Utility Hub
cd /d "%~dp0VECTIS_SYSTEM_FILES"
call .venv\Scripts\activate.bat
python -m streamlit run $targetScript -- $i
pause
"@
    Set-Content -Path $filename -Value $content
    Write-Host "Created $filename"
}
