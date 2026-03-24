import pytest
from unittest.mock import MagicMock
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from explorer import KnowledgeExplorer

def test_expand_knowledge_structure():
    """
    Scenario: Explorer returns a list of related terms with correct structure.
    """
    # Mocking the API response to avoid actual calls
    mock_response = """
    [
        {"term": "Special Relativity", "field": "Physics", "importance": 10},
        {"term": "Bergson", "field": "Philosophy", "importance": 8}
    ]
    """
    
    explorer = KnowledgeExplorer()
    # Mock internal _call_llm method if exists, or just the parsing logic
    explorer._call_llm = MagicMock(return_value=mock_response)
    
    results = explorer.expand("Time")
    
    assert isinstance(results, list)
    assert len(results) == 2
    assert results[0]['term'] == "Special Relativity"
    assert results[0]['field'] == "Physics"
