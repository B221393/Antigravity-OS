
# python_scripts/update_tasks_md.py
import os
import re

def update_schedule_in_tasks():
    # Base directory logic: this script is in python_scripts/, so go up one level to app/
    # Then access VECTIS_SYSTEM_FILES and documents/notes (which seems to be the user's structure in the prompt)
    # Wait, the user's actual structure might be different. I should use relative paths carefully.
    
    # We are at C:\Users\Yuto\Desktop\app\python_scripts
    # VECTIS is at C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES
    # Task file is at C:\Users\Yuto\.gemini\antigravity\brain\66ed5608-f571-403e-b7ab-0e03de082ae5\task.md
    # OR wherever the user keeps their main task list. The prompt mentioned "documents/notes/tasks.md" but that might be hallucinated.
    # The user accepted the AI's proposal which used that path. I should check if "documents/notes" exists.
    # If not, I'll use the artifact task.md I know about.
    pass

import os
import re

def update_schedule_in_tasks():
    # Hardcoded paths based on known structure
    # Events file from the Calendar client
    events_file = r"C:\Users\Yuto\Desktop\app\VECTIS_SYSTEM_FILES\apps\UTILS\calendar\events_output.txt"
    
    # Task file - default to the known artifact location if documents/notes/tasks.md doesn't exist
    tasks_file_artifact = r"C:\Users\Yuto\.gemini\antigravity\brain\66ed5608-f571-403e-b7ab-0e03de082ae5\task.md"
    tasks_file_manual = r"C:\Users\Yuto\Desktop\app\documents\notes\tasks.md"
    
    if os.path.exists(tasks_file_manual):
        tasks_file = tasks_file_manual
    else:
        tasks_file = tasks_file_artifact

    # 1. Read events from events_output.txt
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events_content = f.read().strip()
    except FileNotFoundError:
        print(f"Error: {events_file} not found. Run google_calendar_client.py first.")
        return

    # 2. Prepare the new schedule section content
    new_schedule_section = "## 5. スケジュール (直近の予定)\n\n"
    if "No upcoming events found" in events_content or not events_content:
        new_schedule_section += "Googleカレンダーから取得した結果、直近の予定は見つかりませんでした。\n"
    else:
        new_schedule_section += "以下はGoogleカレンダーから取得した直近の予定です。\n\n"
        # Format as a list
        event_lines = events_content.split('\n')
        formatted_events = []
        for line in event_lines:
            if line.strip():
                 # line format: "2026-02-13T15:30:00+09:00 - Summary"
                 # Let's make it prettier if possible, or just list it
                 formatted_events.append(f"*   {line}")
        new_schedule_section += '\n'.join(formatted_events)
    
    new_schedule_section += "\n"

    # 3. Read tasks.md and replace the schedule section
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_content = f.read()
    except FileNotFoundError:
        print(f"Error: {tasks_file} not found.")
        return

    # 4. Replace logic
    # We look for "## 5. スケジュール" and replace until the next "## " or EOF.
    # If the section doesn't exist, we assume it should be appended or inserted?
    # The prompt simulation assumed it existed. Let's try to find it.
    
    pattern = r"(## 5\. スケジュール \(直近の予定\))(.*?)(?=\n## |\Z)" 
    # ?= is positive lookahead. \Z is EOF.
    
    match = re.search(pattern, tasks_content, re.DOTALL)
    if match:
        updated_tasks_content = tasks_content[:match.start(2)] + "\n\n" + new_schedule_section.replace("## 5. スケジュール (直近の予定)\n\n", "") + tasks_content[match.end(2):]
    else:
        # If not found, append it
        updated_tasks_content = tasks_content + "\n\n" + new_schedule_section

    # 5. Write the updated content back to tasks.md
    try:
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(updated_tasks_content)
        print(f"Successfully updated {tasks_file} with the latest schedule.")
    except Exception as e:
        print(f"Error writing to {tasks_file}: {e}")

if __name__ == "__main__":
    update_schedule_in_tasks()
