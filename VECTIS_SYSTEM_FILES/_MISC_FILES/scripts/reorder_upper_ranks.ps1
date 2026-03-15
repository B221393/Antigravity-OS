$upperRanks = @{
    "100_Launch_All_Systems.bat" = "01_Ultimate_Launcher.bat";
    "98_Ego_Persona.bat"         = "02_Ego_Persona.bat";
    "08_Auto_Watcher.bat"        = "03_Auto_Watcher.bat";
    "97_Data_Lake_Viewer.bat"    = "04_Data_Lake.bat";
    "87_News_Aggregator.bat"     = "05_News_Aggregator.bat";
    "92_Deep_Search.bat"         = "06_Deep_Search.bat";
    "88_Abstract_Writer.bat"     = "07_Abstract_Writer.bat";
    "78_Job_Radar.bat"           = "08_Job_Radar.bat";
    "91_Goal_OKR.bat"            = "09_Goal_OKR.bat";
    "82_Log_Scanner.bat"         = "10_Log_Scanner.bat";
    "89_Idea_Flow.bat"           = "11_Idea_Flow.bat";
    "85_System_Config.bat"       = "12_System_Config.bat"
}

$baseDir = "c:\Users\Yuto\OneDrive - Hiroshima University\app"

# 1. Demote existing 01-12 to Lower_XX
Get-ChildItem $baseDir -Filter "*.bat" | ForEach-Object {
    if ($_.Name -match "^(0[1-9]|1[0-2])_.*\.bat$") {
        # Check if this file is ALREADY one of our targets effectively (e.g. 08_Auto_Watcher is target)
        # If it IS a source for promotion, we don't demote it yet, we handle it in swap.
        # But wait, 08_Auto_Watcher IS Upper Rank 3.
        # If I rename 08 to Lower_08, I lose the source.
        
        # Strategy: Rename ALL current 01-12 to Temp_XX first.
        $newName = "Temp_" + $_.Name
        Rename-Item -Path $_.FullName -NewName $newName
    }
}

# 2. Promote Selected to Top 12
foreach ($src in $upperRanks.Keys) {
    $dest = $upperRanks[$src]
    
    # Source path might be current name OR Temp_name (if it was in 01-12 range)
    # e.g. 08_Auto_Watcher.bat became Temp_08_Auto_Watcher.bat
    
    $srcPath = Join-Path $baseDir $src
    $tempSrcPath = Join-Path $baseDir ("Temp_" + $src)
    
    if (Test-Path $tempSrcPath) {
        # It was one of the low numbers
        Rename-Item -Path $tempSrcPath -NewName $dest
        # Update Title in file
        (Get-Content (Join-Path $baseDir $dest)) -replace "title \[.*\]", "title [Upper Rank] $dest" | Set-Content (Join-Path $baseDir $dest)
    }
    elseif (Test-Path $srcPath) {
        # It was a high number
        Rename-Item -Path $srcPath -NewName $dest
        # Update Title
        (Get-Content (Join-Path $baseDir $dest)) -replace "title \[.*\]", "title [Upper Rank] $dest" | Set-Content (Join-Path $baseDir $dest)
    }
}

# 3. Rename remaining Temp_ to Lower_
Get-ChildItem $baseDir -Filter "Temp_*.bat" | ForEach-Object {
    $finalName = $_.Name -replace "Temp_", "Lower_"
    Rename-Item -Path $_.FullName -NewName $finalName
}

Write-Host "The Twelve Kizuki have been established."
