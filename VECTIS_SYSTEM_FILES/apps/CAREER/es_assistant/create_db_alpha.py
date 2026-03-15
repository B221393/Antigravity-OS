
import json
import csv
import os
import datetime

# Paths
BASE_DIR = r"c:\Users\Yuto\Desktop\app\EGO_SYSTEM_FILES"
CSV_PATH = os.path.join(BASE_DIR, r"apps\es_assistant\data\submission_materials\transcript_db_alpha.csv")
DB_ALPHA_PATH = os.path.join(BASE_DIR, r"apps\es_assistant\data\DB_ALPHA.json")

def create_db_alpha():
    print("🚀 Initializing DB-Alpha Creation...")
    
    if not os.path.exists(CSV_PATH):
        print(f"❌ Error: CSV not found at {CSV_PATH}")
        return

    courses = []
    try:
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                courses.append(row)
        print(f"✅ Loaded {len(courses)} courses from CSV.")
    except Exception as e:
        print(f"❌ Error reading CSV: {e}")
        return

    # Calculate Summary Stats for easy copy-paste
    total_credits = 0
    gpa_points = 0
    graded_courses = 0
    
    # Simple GPA calc assumptions (modify if specific logic needed)
    # S=4, A=3, B=2, C=1, F=0 (Example)
    grade_map = {'S': 4, 'A': 3, 'B': 2, 'C': 1, 'F': 0, '秀': 4, '優': 3, '良': 2, '可': 1, '不可': 0}

    for c in courses:
        try:
            cred = float(c.get('Credits', 0) or c.get('単位数', 0) or c.get('単位', 0))
            grade = c.get('Grade', '') or c.get('評価', '')
            total_credits += cred
            
            if grade in grade_map:
                gpa_points += grade_map[grade] * cred
                graded_courses += cred # weighted by credits
        except:
            pass
            
    gpa = 0
    if graded_courses > 0:
        gpa = gpa_points / graded_courses

    # Create DB-Alpha Structure
    db_alpha = {
        "db_name": "DB-Alpha",
        "description": "User Academic Transcript Data for Upload",
        "last_updated": datetime.datetime.now().isoformat(),
        "summary": {
            "total_credits": total_credits,
            "estimated_gpa": round(gpa, 2),
            "course_count": len(courses)
        },
        "records": courses,
        "upload_helper": {
            "notes": "Use this data to fill out 'Kenria' or other career forms.",
            "csv_source": CSV_PATH
        }
    }

    try:
        with open(DB_ALPHA_PATH, 'w', encoding='utf-8') as f:
            json.dump(db_alpha, f, indent=2, ensure_ascii=False)
            
        print(f"✅ DB-Alpha created successfully at: {DB_ALPHA_PATH}")
        print(f"   Total Credits: {total_credits}")
        print(f"   GPA (Est): {round(gpa, 2)}")
        
    except Exception as e:
        print(f"❌ Error writing DB-Alpha: {e}")

if __name__ == "__main__":
    create_db_alpha()
