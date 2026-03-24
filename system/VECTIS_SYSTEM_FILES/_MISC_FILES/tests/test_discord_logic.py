import pytest
import os
import json
import sys
from datetime import datetime

# Path setup
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(PROJECT_ROOT)

from apps.discord_bot.logic import DiscordLogic

@pytest.fixture
def temp_diary_db(tmp_path):
    # Mocking the diary directory
    d_dir = tmp_path / "diary" / "data"
    d_dir.mkdir(parents=True)
    db_file = d_dir / "entries.json"
    db_file.write_text("[]", encoding="utf-8")
    return str(db_file)

@pytest.fixture
def temp_memo_db(tmp_path):
    # Mocking the memo json
    m_dir = tmp_path / "apps" / "job_hunting"
    m_dir.mkdir(parents=True)
    db_file = m_dir / "memo_data.json"
    init_data = {"done_list": [], "free_memo": ""}
    with open(db_file, "w", encoding="utf-8") as f:
        json.dump(init_data, f)
    return str(db_file)

def test_add_diary_via_logic(temp_diary_db):
    logic = DiscordLogic(diary_path=temp_diary_db)
    result = logic.add_diary_entry("Integration Test Content")
    
    assert "success" in result
    assert result["success"] is True
    
    # Verify file content
    with open(temp_diary_db, "r", encoding="utf-8") as f:
        entries = json.load(f)
    assert len(entries) == 1
    assert entries[0]["content"] == "Integration Test Content"
    assert entries[0]["type"] == "discord_log"

def test_add_task_via_logic(temp_memo_db):
    logic = DiscordLogic(memo_path=temp_memo_db)
    result = logic.add_task("Buy Milk")
    
    assert result["success"] is True
    
    with open(temp_memo_db, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    assert len(data["done_list"]) == 1
    assert data["done_list"][0]["item"] == "Buy Milk"
    assert data["done_list"][0]["status"] == "todo"
