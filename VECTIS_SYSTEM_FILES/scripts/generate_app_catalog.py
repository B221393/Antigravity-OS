import os
import glob

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
# app/EGO_SYSTEM_FILES/apps
APPS_DIR = os.path.join(ROOT_DIR, "apps")
OUTPUT_FILE = os.path.join(ROOT_DIR, "EGO_FULL_APP_CATALOG.md")

def get_description(dir_path):
    # Priority: SKILL.md > README.md > app.py (docstring)
    
    # 1. SKILL.md
    skill_path = os.path.join(dir_path, "SKILL.md")
    if os.path.exists(skill_path):
        try:
            with open(skill_path, "r", encoding="utf-8") as f:
                content = f.read(1000) # Read first 1000 chars
                # Try to extract description from frontmatter or first paragraph
                lines = content.split('\n')
                desc = []
                in_frontmatter = False
                for line in lines:
                    if line.strip() == "---":
                        if in_frontmatter: in_frontmatter = False
                        else: in_frontmatter = True
                        continue
                    if in_frontmatter and line.lower().startswith("description:"):
                        return line.split(":", 1)[1].strip()
                    if not in_frontmatter and line.strip() and not line.startswith("#"):
                         desc.append(line.strip())
                         if len(desc) >= 3: break
                if desc: return " ".join(desc)
        except: pass

    # 2. README.md
    readme_path = os.path.join(dir_path, "README.md")
    if os.path.exists(readme_path):
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                desc = []
                for line in lines[:10]:
                    if line.strip() and not line.startswith("#") and not line.startswith("="):
                        desc.append(line.strip())
                if desc: return " ".join(desc)
        except: pass

    return "No description available."

def generate_catalog():
    print("Generating EGO App Catalog...")
    
    catalog = ["# 📘 EGO FULL APPLICATION CATALOG\n", 
               f"Generated: {os.path.basename(ROOT_DIR)}\n",
               "This document contains specifications for all applications within the EGO ecosystem.\n"]
    
    # Categories based on folder structure
    categories = ["AI_LAB", "MEDIA", "UTILS", "SYSTEM"]
    
    for category in categories:
        cat_path = os.path.join(APPS_DIR, category)
        if not os.path.exists(cat_path): continue
        
        catalog.append(f"\n## 📂 {category}\n")
        
        # Get subdirectories
        subdirs = [d for d in os.listdir(cat_path) if os.path.isdir(os.path.join(cat_path, d))]
        subdirs.sort()
        
        for app_name in subdirs:
            app_path = os.path.join(cat_path, app_name)
            desc = get_description(app_path)
            
            # Simple One-Liner
            catalog.append(f"### {app_name}")
            catalog.append(f"- **Path**: `apps/{category}/{app_name}`")
            catalog.append(f"- **Description**: {desc}\n")
            
            # Identify Key Files
            key_files = glob.glob(os.path.join(app_path, "*.py")) + glob.glob(os.path.join(app_path, "*.bat"))
            if key_files:
                files_str = ", ".join([os.path.basename(f) for f in key_files[:5]])
                if len(key_files) > 5: files_str += ", ..."
                catalog.append(f"- **Files**: `{files_str}`\n")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(catalog))
    
    print(f"✅ Catalog saved to: {OUTPUT_FILE}")

if __name__ == "__main__":
    generate_catalog()
