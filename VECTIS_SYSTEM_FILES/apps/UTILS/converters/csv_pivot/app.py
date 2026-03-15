import streamlit as st
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
import pandas as pd

st.set_page_config(page_title="CSV Pivot", page_icon="📊")
st.title("📊 CSV Pivot & Stats [Rank 54]")

uploaded = st.file_uploader("CSV File", type=["csv"])

if uploaded:
    # Save temp
    path = "temp_pivot.csv"
    with open(path, "wb") as f: f.write(uploaded.getbuffer())
    
    df = pd.read_csv(path)
    st.dataframe(df.head())
    
    # Rust Stats
    st.subheader("⚡ Rust Core Analysis")
    cols = df.select_dtypes(include='number').columns.tolist()
    target_col = st.selectbox("Column", cols)
    
    if target_col:
        # Call vectis_core calc-stats
        ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        CORE = os.path.join(ROOT, "VECTIS_SYSTEM_FILES/apps/vectis_core/target/release/vectis_core.exe")
        
        if os.path.exists(CORE):
            cmd = [CORE, "calc-stats", "--file", path, "--column", target_col]
            try:
                res = subprocess.run(cmd, capture_output=True, text=True)
                if res.stdout.strip():
                    try:
                        stats = json.loads(res.stdout)
                        c1, c2, c3 = st.columns(3)
                        c1.metric("Sum", f"{stats['sum']:,.2f}")
                        c2.metric("Avg", f"{stats['avg']:,.2f}")
                        c3.metric("Max", f"{stats['max']:,.2f}")
                    except:
                        st.text(res.stdout)
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Rust Core not found. Using Pandas.")
            st.write(df[target_col].describe())

    st.subheader("Pivot")
    # Simple pivot UI
    idx = st.selectbox("Index", df.columns)
    val = st.selectbox("Value", cols)
    agg = st.selectbox("Func", ["sum", "mean", "count"])
    
    if st.button("Pivot Table"):
        p = pd.pivot_table(df, index=idx, values=val, aggfunc=agg)
        st.dataframe(p)
        st.bar_chart(p)
