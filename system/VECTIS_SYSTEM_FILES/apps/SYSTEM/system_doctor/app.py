import streamlit as st
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import sys
import pkg_resources

st.set_page_config(page_title="System Doctor", page_icon="👨‍⚕️", layout="wide")
st.title("👨‍⚕️ System Doctor (Health Check)")

def check_env():
    # Check .env
    env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../.env"))
    return os.path.exists(env_path)

def check_dirs():
    # Critical dirs
    roots = ["../../../AUTO_YOUTUBE", "../../../memory", "../../../logs"]
    missing = []
    for r in roots:
        path = os.path.abspath(os.path.join(os.path.dirname(__file__), r))
        if not os.path.exists(path): missing.append(r)
    return missing

# Dashboard
c1, c2, c3 = st.columns(3)
score = 100

# 1. ENV Check
c1.subheader("Configuration")
if check_env():
    c1.success("✅ .env found")
else:
    c1.error("❌ .env missing")
    score -= 30

# 2. Structure Check
c2.subheader("File Structure")
missing_dirs = check_dirs()
if not missing_dirs:
    c2.success("✅ Structure OK")
else:
    c2.error(f"❌ Missing: {missing_dirs}")
    score -= 20

# 3. Python Libs
c3.subheader("Dependencies")
installed = {pkg.key for pkg in pkg_resources.working_set}
required = {"streamlit", "pandas", "numpy", "feedparser", "google-generativeai"}
missing_libs = required - installed
if not missing_libs:
    c3.success("✅ Libraries OK")
else:
    c3.warning(f"⚠️ Missing: {missing_libs}")
    score -= 10

st.divider()
st.metric("System Health Score", f"{score}/100")

if score < 100:
    st.warning("Issues detected. Please run 'pip install -r requirements.txt' or check file paths.")
else:
    st.balloons()
    st.success("System is Healthy! VECTIS OS is ready.")
