$ranks = @{
    # Top 12 (Upper Ranks) - Preserved, map logic handles collision but we list them to be safe or ignore
    # Group A: Core & Knowledge
    "13"  = "Dashboard";
    "14"  = "YouTube_Web";
    "15"  = "YouTube_CLI";
    "16"  = "Wiki_Lite";
    "17"  = "Journal_Plus";
    "18"  = "Book_Keeper";
    "19"  = "Quote_Bank";
    "20"  = "Skill_Tree";
    "21"  = "Knowledge_Network";
    "22"  = "Corpus_Map";
    "23"  = "Keyword_Mixer";
    "24"  = "Random_Wiki";
    "25"  = "Book_Log";

    # Group B: Dev & System
    "26"  = "Python_Dojo";
    "27"  = "Flash_Grep";
    "28"  = "Flash_Count";
    "29"  = "Regex_Dojo";
    "30"  = "JSON_Smith";
    "31"  = "Diff_Eye";
    "32"  = "Snippet_Hub";
    "33"  = "System_Doctor";
    "34"  = "Panic_Button";
    "35"  = "Ego_Engine";
    "36"  = "Ego_Voice";
    "37"  = "Memory_Viewer";
    "38"  = "Tube_Stats";
    "39"  = "Task_Bridge";

    # Group C: Business & Finance
    "40"  = "Market_Watch";
    "41"  = "Invoice_Gen";
    "42"  = "Meeting_Cost";
    "43"  = "Decision_Matrix";
    "44"  = "Risk_Register";
    "45"  = "Pareto_Plot";
    "46"  = "Headcount_Calc";
    "47"  = "Shift_Maker";
    "48"  = "Time_Zone_Mate";
    "49"  = "Retro_Board";
    "50"  = "Password_Forge";
    "51"  = "Quick_QR";
    "52"  = "PDF_Splicer";
    "53"  = "Image_Diet";
    "54"  = "CSV_Pivot";
    "55"  = "Kanji_Num";

    # Group D: Utility & Converters
    "56"  = "Era_Gengo";
    "57"  = "Unit_Master";
    "58"  = "Base_Master";
    "59"  = "Hash_Temple";
    "60"  = "UUID_Forge";
    "61"  = "Base64_Loom";
    "62"  = "URL_Keeper";
    "63"  = "Color_Picker";
    "64"  = "Mark_Live";
    "65"  = "ASCII_Artist";
    "66"  = "Color_Alchemy";
    "67"  = "Text_Cleaner";
    "68"  = "IP_Checker";
    "69"  = "Sys_Monitor";
    "70"  = "MD_Cheat";
    "71"  = "Git_Cheat";
    "72"  = "Notepad_Lite";
    "73"  = "Todo_Mini";
    "74"  = "Expense_Log";
    "75"  = "Zen_Focus";

    # Group E: Life & Games & Others
    "76"  = "Life_RPG";
    "77"  = "Mind_Alchemy";
    "78"  = "Pomodoro_Lite";
    "79"  = "Breathe";
    "80"  = "Reaction_Test";
    "81"  = "Typing_Speed";
    "82"  = "Flashcards";
    "83"  = "Habit_Chain";
    "84"  = "Bio_Rhythm";
    "85"  = "Moon_Phase";
    "86"  = "Weather_Mock";
    "87"  = "Stopwatch";
    "88"  = "Dice_Roller";
    "89"  = "World_Capitals";
    "90"  = "FX_Soundboard";
    
    # Background / Less Accessed / Deprecated-ish
    "91"  = "MAGI_HUD";
    "92"  = "Main_HUD";
    "93"  = "Control_Center";
    "94"  = "Vectis_Hub";
    "95"  = "Emergency_Stop";
    "96"  = "ES_Assistant";
    "97"  = "Ego_Evolution";
    "98"  = "TOEIC_Mastery";
    "99"  = "TOEIC_Analytics";
    "100" = "Utility_Hub" # The gap filler generic launcher can sit at end or hide
}

$baseDir = "c:\Users\Yuto\OneDrive - Hiroshima University\app"

# 1. Normalize all filenames first to remove numbers (except top 12) to avoid conflicts
# We search for ANY bat file that contains the key name (e.g. "*Dashboard.bat")
Get-ChildItem $baseDir -Filter "*.bat" | ForEach-Object {
    if ($_.Name -match "^(0[1-9]|1[0-2])_") {
        # Skip Upper Ranks 1-12
        return
    }
    
    $cleanName = $_.Name -replace "^\d+_", "" -replace "^Lower_\d+_", "" -replace "^Temp_\d+_", "" -replace "\[\d+\]_", ""
    # Rename to temporary safe ID-less name
    $tempName = "Z_PENDING_" + $cleanName
    Rename-Item -Path $_.FullName -NewName $tempName -ErrorAction SilentlyContinue
}

# 2. Apply new ranks
foreach ($rank in $ranks.Keys) {
    # Sort keys clearly? Powershell hash table is unordered list enum.
    # We loop.
    $targetName = $ranks[$rank]
    
    # Find the pending file
    $pattern = "Z_PENDING_*$targetName.bat"
    $files = Get-ChildItem $baseDir -Filter $pattern
    
    if ($files) {
        $file = $files[0] # Take first match
        $newName = "${rank}_${targetName}.bat"
        Rename-Item -Path $file.FullName -NewName $newName
        
        # Update Title
        (Get-Content (Join-Path $baseDir $newName)) -replace "title \[.*\]", "title [$rank] $targetName" | Set-Content (Join-Path $baseDir $newName)
        Write-Host "Ranked $rank : $targetName"
    }
    else {
        Write-Warning "Could not find file for $targetName"
    }
}

# 3. Cleanup any Z_PENDING that were not matched (Generic Utility Hubs 21-39 generated earlier might be duplicates or lost)
Get-ChildItem $baseDir -Filter "Z_PENDING_*.bat" | ForEach-Object {
    Write-Host "Remaining unranked: $($_.Name)"
    # Leave them or rename to Unranked_...
}
