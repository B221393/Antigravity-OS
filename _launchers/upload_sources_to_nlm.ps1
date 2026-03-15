# NotebookLM Source Upload Script (v2 - Command Substitution)
# This script uploads all essential project documents to the 'antigravity' notebook.

Write-Host "Starting upload to NotebookLM... (v2)"

# --- Core System & Identity Files ---
Write-Host "Uploading Core System & Identity files..."
nlm add text "antigravity" --title "EGO Specifications JP" "$(Get-Content 'VECTIS_SYSTEM_FILES/EGO_SPECIFICATIONS_JP.md' -Raw)"
nlm add text "antigravity" --title "System Specifications" "$(Get-Content 'VECTIS_SYSTEM_FILES/SYSTEM_SPEC.md' -Raw)"
nlm add text "antigravity" --title "AI Identity" "$(Get-Content 'VECTIS_SYSTEM_FILES/IDENTITY.md' -Raw)"
nlm add text "antigravity" --title "AI Soul" "$(Get-Content 'VECTIS_SYSTEM_FILES/SOUL.md' -Raw)"

# --- VECTIS System Files ---
Write-Host "Uploading VECTIS System files..."
nlm add text "antigravity" --title "System - Additional Orders" "$(Get-Content 'VECTIS_SYSTEM_FILES/ADDITIONAL_ORDERS.md' -Raw)"
nlm add text "antigravity" --title "System - Agents" "$(Get-Content 'VECTIS_SYSTEM_FILES/AGENTS.md' -Raw)"
nlm add text "antigravity" --title "System - AI Context Bridge" "$(Get-Content 'VECTIS_SYSTEM_FILES/AI_CONTEXT_BRIDGE.md' -Raw)"
nlm add text "antigravity" --title "System - Apps Catalog" "$(Get-Content 'VECTIS_SYSTEM_FILES/APPS_CATALOG.md' -Raw)"
nlm add text "antigravity" --title "System - Bootstrap" "$(Get-Content 'VECTIS_SYSTEM_FILES/BOOTSTRAP.md' -Raw)"
nlm add text "antigravity" --title "System - Directory Map" "$(Get-Content 'VECTIS_SYSTEM_FILES/DIRECTORY_MAP.md' -Raw)"
nlm add text "antigravity" --title "System - Heartbeat" "$(Get-Content 'VECTIS_SYSTEM_FILES/HEARTBEAT.md' -Raw)"
nlm add text "antigravity" --title "System - Ideas Log" "$(Get-Content 'VECTIS_SYSTEM_FILES/IDEAS_LOG.md' -Raw)"
nlm add text "antigravity" --title "System - Instruction" "$(Get-Content 'VECTIS_SYSTEM_FILES/INSTRUCTION.md' -Raw)"
nlm add text "antigravity" --title "User - Liberal Arts Nexus" "$(Get-Content 'VECTIS_SYSTEM_FILES/LIBERAL_ARTS_NEXUS.md' -Raw)"
nlm add text "antigravity" --title "System - Rule" "$(Get-Content 'VECTIS_SYSTEM_FILES/rule.md' -Raw)"
nlm add text "antigravity" --title "System - Skill" "$(Get-Content 'VECTIS_SYSTEM_FILES/SKILL.md' -Raw)"
nlm add text "antigravity" --title "System - System Status" "$(Get-Content 'VECTIS_SYSTEM_FILES/SYSTEM_STATUS.md' -Raw)"
nlm add text "antigravity" --title "System - Tools" "$(Get-Content 'VECTIS_SYSTEM_FILES/TOOLS.md' -Raw)"
nlm add text "antigravity" --title "System - User Request Log" "$(Get-Content 'VECTIS_SYSTEM_FILES/USER_REQUEST_LOG.md' -Raw)"
nlm add text "antigravity" --title "System - User" "$(Get-Content 'VECTIS_SYSTEM_FILES/USER.md' -Raw)"

# --- User Profile & Skills ---
Write-Host "Uploading User Profile & Skills files..."
nlm add text "antigravity" --title "User - Job Hunting Strategy" "$(Get-Content 'User_Profile/JOB_HUNTING_STRATEGY.md' -Raw)"
nlm add text "antigravity" --title "User - My Episodes" "$(Get-Content 'User_Profile/MY_EPISODES.md' -Raw)"
nlm add text "antigravity" --title "Skill - Debate" "$(Get-Content 'Skills/skill_debate.md' -Raw)"
nlm add text "antigravity" --title "Skill - E2E" "$(Get-Content 'Skills/skill_e2e.md' -Raw)"
nlm add text "antigravity" --title "Skill - Review" "$(Get-Content 'Skills/skill_review.md' -Raw)"
nlm add text "antigravity" --title "Skill - Writing" "$(Get-Content 'Skills/skill_writing.md' -Raw)"

Write-Host "All files have been processed. Please check your NotebookLM."
