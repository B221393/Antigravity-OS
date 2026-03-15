import os
import sys
from pathlib import Path
from typing import Optional

# --- Configuration Constants ---
SKILL_NAME = "skill-creator"
DEFAULT_LOCAL_PATH = Path.home() / ".gemini" / "skills" / SKILL_NAME
DEFAULT_AG_PATH = Path.cwd() / "skills" / SKILL_NAME

# --- Templates ---

SKILL_MD_TEMPLATE = """---
name: {skill_name}
description: A meta-skill to create new Agent Skills following the Anthropic open standard.
version: 1.0.0
---

# {skill_name}

## Description
Creates a new skill directory structure optimized for Gemini CLI agents.
Enforces strict Progressive Disclosure and safety guardrails.

## Usage
Run the script to interactively generate a new skill.

```bash
python3 scripts/create.py
```

## Mandatory Guardrails
- MUST NOT overwrite existing skills without user confirmation.
- MUST insert the mandatory acknowledgement hook in the new skill.
"""

# Note: We use raw string for the inner template to avoid f-string confusion, 
# but we need to verify the content matches the intent.
CREATE_SCRIPT_TEMPLATE = """#!/usr/bin/env python3
import os
import sys
from pathlib import Path
from typing import Optional

def get_input(prompt: str, default: Optional[str] = None) -> str:
    prompt_text = f"{prompt} [{default}]: " if default else f"{prompt}: "
    res = input(prompt_text).strip()
    return res if res else (default or "")

def create_skill():
    print(f"--- Agent Skill Generator ({SKILL_NAME}) ---")
    
    # 1. Define Paths
    base_dir = Path.cwd().parent 
    skill_name = get_input("Enter new skill name (kebab-case)", "my-new-skill")
    target_dir = base_dir / skill_name
    
    # 2. Safety Check (No Overwrite)
    if target_dir.exists():
        print(f"\\n[!] Target directory already exists: {target_dir}")
        choice = get_input("Overwrite? (y/n)", "n")
        if choice.lower() != 'y':
            print("Aborted.")
            sys.exit(0)
    else:
        target_dir.mkdir(parents=True)
        
    # 3. Create Structure
    (target_dir / "references").mkdir(exist_ok=True)
    (target_dir / "scripts").mkdir(exist_ok=True)
    
    # 4. Generate SKILL.md with Mandatory Acknowledgement
    # We construct the content. Note the f-string in the generated code
    skill_md = f\"\"\"---
name: {skill_name}
description: TODO: Add description
version: 0.1.0
---

# {skill_name}

## Acknowledgement (Mandatory)
`[Skill activated: {skill_name}]`

## Description
Describe what this skill does here.

## References
See references/ for details.
\"\"\"

    with open(target_dir / "SKILL.md", "w", encoding="utf-8") as f:
        f.write(skill_md)
        
    print(f"\\n[+] Skill created successfully at: {target_dir}")
    print(f"    Check {target_dir}/SKILL.md to start editing.")

if __name__ == "__main__":
    create_skill()
"""

# --- Installer Logic ---
def determine_install_path() -> Path:
    """Interactively determine the installation path based on environment."""
    # Heuristic for AntiGravity/Cloud vs Local
    is_local = "google.colab" not in sys.modules and not os.environ.get("ANTIGRAVITY_ENV")
    
    default_path = DEFAULT_LOCAL_PATH if is_local else DEFAULT_AG_PATH
    
    print(f"--- {SKILL_NAME} Installer ---")
    print(f"Suggested install path: {default_path}")
    
    while True:
        choice = input("Accept suggested path? [Y/n/custom]: ").strip().lower()
        if choice in ('', 'y', 'yes'):
            return default_path
        elif choice in ('n', 'no'):
            print("Operation cancelled by user.")
            sys.exit(0)
        elif choice == 'custom':
            custom = input("Enter absolute path: ").strip()
            if custom:
                return Path(custom)
        else:
            # Assume user typed a path directly if not y/n/custom
            if "/" in choice or "\\" in choice:
                 return Path(choice)

def install():
    target_path = determine_install_path()
    
    # Safety: Check existence
    if target_path.exists():
        print(f"\\n[!] Warning: Path {target_path} already exists.")
        if input("Overwrite? [y/N]: ").strip().lower() != 'y':
            print("Aborted.")
            sys.exit(0)
            
    # Create Directories
    scripts_dir = target_path / "scripts"
    refs_dir = target_path / "references"
    
    try:
        scripts_dir.mkdir(parents=True, exist_ok=True)
        refs_dir.mkdir(parents=True, exist_ok=True)
        
        # Write Files
        # 1. SKILL.md
        with open(target_path / "SKILL.md", "w", encoding="utf-8") as f:
            f.write(SKILL_MD_TEMPLATE.format(skill_name=SKILL_NAME))
            
        # 2. scripts/create.py (The actual logic for the skill)
        create_script_path = scripts_dir / "create.py"
        with open(create_script_path, "w", encoding="utf-8") as f:
            f.write(CREATE_SCRIPT_TEMPLATE.replace("{SKILL_NAME}", SKILL_NAME))
            
        # Make script executable (Linux/Mac)
        if os.name == 'posix':
            create_script_path.chmod(0o755)
            
        print(f"\\n[Success] {SKILL_NAME} installed to: {target_path}")
        print(f"To use: python3 {create_script_path}")
        
    except Exception as e:
        print(f"\\n[Error] Installation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install()
