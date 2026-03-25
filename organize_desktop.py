#!/usr/bin/env python3
import os
import shutil
from pathlib import Path

# Base directory
base_dir = Path("C:/Users/Yuto/Desktop/app")
os.chdir(base_dir)

# Define categories and file patterns
categories = {
    "projects": [
        "Qumi_Core", "RUST_PROJECTS", "apps", "DYNAMIC_DESKTOP_PROJECT",
        "quake_sim", "quake_sim_3d", "agents", "personal", "system"
    ],
    "docs": [
        "README.md", "Integrated_System_Specs.md", "Integrated_Thinking_OS_Paper.md",
        "Todays_Tasks_from_Email.md", "ai_collaboration_test.md"
    ],
    "tools": [
        "bin", "python_scripts", "check_calendar.py", "check_interview_schedule.py",
        "cleanup.py", "_agent", "_config", "_launchers"
    ],
    "temp": [
        "ai_comparison_index.html", "light_scatter_ai1_haiku.html",
        "light_scatter_ai2_optimized.html", "light_scatter_ai3_raycasting.html",
        "qumi_ui_concept.html", "gmail_out.txt", "tmp_objects.txt",
        "large_tracked_files.txt"
    ],
    "archive": [
        "archives"
    ]
}

# Create directories if they don't exist
for category in categories.keys():
    Path(category).mkdir(exist_ok=True)
    print(f"✓ Created: {category}/")

# Move files
moved_count = 0
for category, items in categories.items():
    for item in items:
        item_path = Path(item)
        if item_path.exists():
            dest = Path(category) / item
            # Avoid moving if already in correct location
            if item_path.parent.name != category:
                try:
                    shutil.move(str(item_path), str(dest))
                    print(f"  → {item} → {category}/")
                    moved_count += 1
                except Exception as e:
                    print(f"  ✗ Error moving {item}: {e}")

print(f"\n✓ Moved {moved_count} items")
print("\nDesktop organization complete!")
