import os
import shutil
import json

# Define the root of the apps directory
APPS_ROOT = os.path.dirname(os.path.abspath(__file__))
# Define the target genre folders
GENRES = {
    "AI_LAB": [
        "ai_evolution", "ai_lab", "anime-physics-scaler", "auto_researcher", "chat_analyzer", 
        "deep_search", "diff_eye", "digital-twin", "driving_3d", "driving_lab", "ego_*", 
        "es_assistant", "face_recognizer", "knowledge_*", "memory_*", "mind_alchemy", 
        "personal_intelligence", "racing_game", "shogi_dojo", "text_router", "vectis_*", 
        "voice_input", "voice_output", "vision_action", "antigravity", "universe_*"
    ],
    "MEDIA": [
        "ascii_artist", "bookshelf", "color_*", "fx_soundboard", "image_diet", "mark_live", 
        "news_aggregator", "obsidian_vault", "pdf_splicer", "stream", "tube_stats", 
        "youtube_*", "video_*", "music_*"
    ],
    "SYSTEM": [
        "app_launcher", "base_master", "config", "corpus_map", "dashboard", "desktop_hud", 
        "error_reporter", "help", "history", "jarvis_hud", "log_scanner", "logs", "modules", 
        "process_killer", "system_*", "task_bridge", "ultimate_launcher", "usage_stats.json", 
        "user_request_log", "vectis_core"
    ],
    "UTILS": [
        "base64_loom", "book_keeper", "book_log", "calendar", "converter", "creator", 
        "csv_pivot", "data_lake", "decision_matrix", "factor_lab", "fill_21_39", 
        "flash_count", "flash_grep", "goal_okr", "hash_temple", "headcount_calc", 
        "horse_forecast", "idea_flow", "invoice_gen", "job_*", "journal_plus", "json_smith", 
        "kanji_num", "keyword_mixer", "life_rpg", "link", "mandala_chart", "market_watch", 
        "meeting_cost", "mobile", "onishi", "panic_button", "pareto_plot", "password_forge", 
        "phoneapply", "python_dojo", "quick_qr", "quote_bank", "random_wiki", "regex_dojo", 
        "retro_board", "risk_register", "rust_matcher", "schedule_*", "scheduler", "scout", 
        "shift_maker", "skill_tree", "snippet_hub", "spi_trainer", "stats", "time_zone_mate", 
        "todo", "toeic_*", "trivia", "unit_master", "url_keeper", "uuid_forge", 
        "wiki_lite", "world_capitals", "x_trends", "zen_focus", "diary"
    ]
}

def organize_apps():
    print("Starting EGO App Organization...")
    
    # 1. Create Genre Folders if they don't exist
    for genre in GENRES.keys():
        genre_path = os.path.join(APPS_ROOT, genre)
        if not os.path.exists(genre_path):
            os.makedirs(genre_path)
            print(f"Created genre folder: {genre}")

    # 2. Scan and Move
    items = os.listdir(APPS_ROOT)
    
    for item in items:
        item_path = os.path.join(APPS_ROOT, item)
        
        # Skip the genre folders themselves and this script
        if item in GENRES.keys() or item == os.path.basename(__file__):
            continue
            
        # Determine destination
        destination_genre = None
        
        # Check explicit mapping & wildcards
        for genre, patterns in GENRES.items():
            if item in patterns:
                destination_genre = genre
                break
            # Wildcard check (e.g., job_*)
            for p in patterns:
                if p.endswith("*") and item.startswith(p[:-1]):
                    destination_genre = genre
                    break
            if destination_genre: break
            
        # Default Fallback (if not found in list, put in UTILS or ask user? Putting in UTILS for now as safe bucket)
        if not destination_genre:
            # Simple heuristic: if likely system file, SYSTEM
            if item.startswith(".") or item.startswith("_"):
                destination_genre = "SYSTEM"
            else:
                destination_genre = "UTILS"
        
        # Move
        dest_path = os.path.join(APPS_ROOT, destination_genre, item)
        
        try:
            # Handle collision (if folder exists in dest, merge or skip?)
            if os.path.exists(dest_path):
                print(f"Skipping {item} -> {destination_genre} (Already exists)")
            else:
                shutil.move(item_path, dest_path)
                print(f"Moved {item} -> {destination_genre}")
        except Exception as e:
            print(f"Error moving {item}: {e}")

    print("Organization Complete.")

if __name__ == "__main__":
    organize_apps()
