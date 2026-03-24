import json
import subprocess
import os
import time

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'launcher_config.json')
VENV_PYTHON = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.venv', 'Scripts', 'python.exe')

def load_config():
    """Loads the launcher configuration from the JSON file."""
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: Configuration file '{CONFIG_FILE}' not found.")
        return {"apps": []}
    with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)

def launch_streamlit_app(command):
    """Launches a single Streamlit app in a new process."""
    try:
        # Streamlit commands already include 'python -m streamlit run ...'
        # We need to execute it in a new console
        subprocess.Popen(command, creationflags=subprocess.CREATE_NEW_CONSOLE, shell=True)
        print(f"  Launched: {command}")
    except Exception as e:
        print(f"  Error launching Streamlit app '{command}': {e}")

def main():
    """Launches all Streamlit applications defined in the config."""
    print("==========================================")
    print("  🚀 Launching All Streamlit Apps 🚀")
    print("==========================================")
    
    config = load_config()
    apps = config.get('apps', [])
    
    streamlit_apps_launched = 0
    
    for app in apps:
        command = app.get('command', '')
        if "streamlit run" in command:
            launch_streamlit_app(command)
            streamlit_apps_launched += 1
            time.sleep(2) # Give some time for each app to start

    if streamlit_apps_launched == 0:
        print("No Streamlit applications found in launcher_config.json.")
    else:
        print(f"\n✅ Successfully launched {streamlit_apps_launched} Streamlit apps.")
    
    print("\nPress any key to close this launcher.")
    os.system('pause >nul') # For Windows compatibility

if __name__ == "__main__":
    main()
