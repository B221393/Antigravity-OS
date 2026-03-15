import os
import sys
import pytest

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_deep_cosmos_e2e_workflow():
    """
    Scenario: User generates a cosmos from 'Time'
    Given the DeepCosmos application
    When I run the main generation process with 'Time'
    Then an HTML file 'cosmos_Time.html' should be created
    """
    # This import should fail initially (Red State)
    try:
        from main import DeepCosmosApp
    except ImportError:
        pytest.fail("DeepCosmosApp could not be imported. Implementation missing.")

    keyword = "Time_Test"
    output_file = f"cosmos_{keyword}.html"
    
    # Clean up before test
    if os.path.exists(output_file):
        os.remove(output_file)

    app = DeepCosmosApp()
    
    # Mocking or using real logic? 
    # For E2E, we prefer real logic, but without paying API costs or waiting too long.
    # However, for this initial Red test, we expect the class/method to be missing.
    app.run(keyword)
    
    # Verify
    assert os.path.exists(output_file), "Output HTML file was not created."
    assert os.path.getsize(output_file) > 100, "Output file is empty."
    
    # Cleanup
    if os.path.exists(output_file):
        os.remove(output_file)
