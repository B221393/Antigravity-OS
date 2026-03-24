import streamlit as st
import glob
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import subprocess
import json
import psutil

st.set_page_config(page_title="VECTIS ULTIMATE", page_icon="💠", layout="wide")
st.title("💠 VECTIS ULTIMATE LAUNCHER [01]")

# Root Config
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
USAGE_FILE = os.path.join(ROOT_DIR, "VECTIS_SYSTEM_FILES/usage_stats.json")

# Load Usage
usage_stats = {}
if os.path.exists(USAGE_FILE):
    with open(USAGE_FILE, "r") as f: usage_stats = json.load(f)

# Helper: Check if running
def is_running(script_name):
    # Heuristic check for python script in cmdline
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['cmdline'] and script_name in " ".join(proc.info['cmdline']):
                return True
        except: pass
    return False

# Grouping Logic (based on filename convention or manual map)
# We will use "Twelve Kizuki" as Top, others by range
files = sorted(glob.glob(os.path.join(ROOT_DIR, "*.bat")))

groups = {
    "Upper Ranks (01-12)": [],
    "Knowledge (13-25)": [],
    "System (26-39)": [],
    "Business (40-55)": [],
    "Utility (56-75)": [],
    "Other (76-100)": []
}

for f in files:
    name = os.path.basename(f)
    try:
        num = int(name.split("_")[0])
        if 1 <= num <= 12: groups["Upper Ranks (01-12)"].append(f)
        elif 13 <= num <= 25: groups["Knowledge (13-25)"].append(f)
        elif 26 <= num <= 39: groups["System (26-39)"].append(f)
        elif 40 <= num <= 55: groups["Business (40-55)"].append(f)
        elif 56 <= num <= 75: groups["Utility (56-75)"].append(f)
        else: groups["Other (76-100)"].append(f)
    except:
        groups["Other (76-100)"].append(f)

# --- UI ---
tabs = st.tabs(list(groups.keys()))

for idx, (grp_name, grp_files) in enumerate(groups.items()):
    with tabs[idx]:
        cols = st.columns(4)
        for i, bat in enumerate(grp_files):
            name = os.path.basename(bat).replace(".bat", "")
            
            # Status Check (Simple python script check)
            # Infer python script name from Bat name? Hard without parsing bat.
            # Just show a generic launcher button.
            
            with cols[i % 4]:
                st.markdown(f"#### {name}")
                # Usage
                # Try match
                u_count = 0
                for k,v in usage_stats.items():
                    if k in name: u_count = v
                
                st.caption(f"Used: {u_count} times")
                
                if st.button(f"🚀 Launch", key=f"L_{name}"):
                    try:
                        subprocess.Popen(f'start "" "{bat}"', shell=True, cwd=ROOT_DIR)
                        st.toast(f"Launching {name}...")
                    except Exception as e:
                        st.error(str(e))
                
                st.divider()
