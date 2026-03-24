
import sys
import os
import traceback

sys.path.append(os.getcwd())

try:
    import gemini_client
    print("Import successful.")
    
    print("Attempting to generate content...")
    # Using a simple prompt
    response = gemini_client.generate_content("Say 'Hello' briefly.")
    print(f"Response: {response}")
    
except Exception as e:
    print("Error during execution:")
    traceback.print_exc()
