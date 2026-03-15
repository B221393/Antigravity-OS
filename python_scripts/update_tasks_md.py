# python_scripts/update_tasks_md.py
import os
import re

def update_schedule_in_tasks():
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    events_file = os.path.join(base_dir, 'VECTIS_SYSTEM_FILES', 'apps', 'UTILS', 'calendar', 'events_output.txt')
    tasks_file = os.path.join(base_dir, 'documents', 'notes', 'tasks.md')

    # 1. Read events from events_output.txt
    try:
        with open(events_file, 'r', encoding='utf-8') as f:
            events_content = f.read().strip()
    except FileNotFoundError:
        print(f"Error: {events_file} not found.")
        return

    # 2. Prepare the new schedule section content
    new_schedule_section = "## 5. スケジュール (直近の予定)

"
    if "No upcoming events found" in events_content:
        new_schedule_section += "Googleカレンダーから取得した結果、直近の予定は見つかりませんでした。
"
    else:
        new_schedule_section += "以下はGoogleカレンダーから取得した直近の予定です。

"
        # Format as a list
        event_lines = events_content.split('
')
        formatted_events = [f"*   {line.replace(' - ', ': 予定内容 - ')}" for line in event_lines if line.strip()]
        new_schedule_section += '
'.join(formatted_events)

    # 3. Read tasks.md and replace the schedule section
    try:
        with open(tasks_file, 'r', encoding='utf-8') as f:
            tasks_content = f.read()
    except FileNotFoundError:
        print(f"Error: {tasks_file} not found.")
        return

    # Use regex to find and replace the schedule section
    # This will replace everything from "## 5. スケジュール (直近の予定)" to the end of the file
    updated_tasks_content = re.sub(
        r"(?s)(## 5\. スケジュール \(直近の予定\)).*",
        new_schedule_section,
        tasks_content,
        count=1
    )

    # 4. Write the updated content back to tasks.md
    try:
        with open(tasks_file, 'w', encoding='utf-8') as f:
            f.write(updated_tasks_content)
        print(f"Successfully updated {tasks_file} with the latest schedule.")
    except Exception as e:
        print(f"Error writing to {tasks_file}: {e}")

if __name__ == "__main__":
    update_schedule_in_tasks()
