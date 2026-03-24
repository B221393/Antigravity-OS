
import sys
import os
import json
import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

# Add root directory to sys.path to import mobile_bridge
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from mobile_bridge import app, LOG_FILE

client = TestClient(app)

# Mock Data
MOCK_GEMINI_RESPONSE = "This is a mock response from Gemini."

@pytest.fixture
def mock_agent():
    with patch("modules.researcher.ResearchAgent") as MockAgent:
        instance = MockAgent.return_value
        instance._call_llm.return_value = MOCK_GEMINI_RESPONSE
        yield instance

@pytest.fixture
def clean_log_file():
    # Setup: Encure log file is safe or use a temp file
    # For this test, we will patch the LOG_FILE constant or just mock open
    pass 

def test_read_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "VECTIS MOBILE" in response.text

def test_chat_endpoint_success(mock_agent):
    # Mocking os.getenv to ensure API keys appear present
    with patch("os.getenv", return_value="fake_key"):
        # We also need to mock the file writing to avoid messing up real logs
        with patch("builtins.open", new_callable=MagicMock) as mock_open:
            # Mock json load/dump
             with patch("json.load", return_value=[]):
                with patch("json.dump") as mock_dump:
                    response = client.post("/chat", data={"message": "Hello AI"})
                    
                    assert response.status_code == 200
                    json_resp = response.json()
                    assert json_resp["status"] == "success"
                    assert json_resp["reply"] == MOCK_GEMINI_RESPONSE
                    
                    # Verify Log Writing
                    mock_dump.assert_called()

def test_chat_endpoint_missing_params():
    response = client.post("/chat", data={}) # No message
    assert response.status_code == 422 # Validation Error

def test_command_endpoint():
    with patch("builtins.open", new_callable=MagicMock):
        with patch("json.dump") as mock_dump:
            response = client.post("/command", data={"command": "test_cmd"})
            assert response.status_code == 200
            assert response.json()["queued"] == "test_cmd"
