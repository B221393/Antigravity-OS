import streamlit as st
import pandas as pd

st.set_page_config(page_title="Decision Matrix", page_icon="⚖️")
st.title("⚖️ Weighted Decision Matrix")

# 1. Setup Criteria
st.sidebar.header("1. Criteria & Weights")
criteria_text = st.sidebar.text_area("Criteria (one per line)", "Cost\nEase of Use\nFeatures\nReliability")
weights_text = st.sidebar.text_area("Weights (0-10, one per line)", "8\n6\n9\n10")

crits = [c.strip() for c in criteria_text.split('\n') if c.strip()]
weights = []
for w in weights_text.split('\n'):
    if w.strip().isdigit(): weights.append(int(w))
    else: weights.append(1)

# Pad weights if mismatch
while len(weights) < len(crits): weights.append(1)

# 2. Setup Options
st.sidebar.header("2. Options")
options_text = st.sidebar.text_area("Options (one per line)", "Vendor A\nVendor B\nIn-house Dev")
options = [o.strip() for o in options_text.split('\n') if o.strip()]

# 3. Scoring
st.header("Scoring Options")

# Data structure: scores[option][criterion]
if 'scores' not in st.session_state: st.session_state.scores = {}

# Initialize
for opt in options:
    if opt not in st.session_state.scores: st.session_state.scores[opt] = {}

cols = st.columns(len(options))
for i, opt in enumerate(options):
    with cols[i]:
        st.subheader(opt)
        for j, crit in enumerate(crits):
            val = st.number_input(f"{crit} (1-10)", 1, 10, 5, key=f"{opt}_{crit}")
            st.session_state.scores[opt][crit] = val

# 4. Result
st.divider()
st.header("🏆 Result")

results = []
for opt in options:
    total = 0
    breakdown = []
    for i, crit in enumerate(crits):
        score = st.session_state.scores[opt].get(crit, 5)
        w = weights[i]
        weighted_score = score * w
        total += weighted_score
        breakdown.append(weighted_score)
    results.append({"Option": opt, "Score": total})

df = pd.DataFrame(results).sort_values("Score", ascending=False)
st.dataframe(df)

best = df.iloc[0]
st.success(f"Recommended Option: **{best['Option']}** (Score: {best['Score']})")
