import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Risk Register", page_icon="⚠")
st.title("⚠ Project Risk Register")

if 'risks' not in st.session_state:
    st.session_state.risks = []

with st.expander("Add New Risk"):
    r_name = st.text_input("Risk Description")
    prob = st.slider("Probability (1-5)", 1, 5, 3)
    impact = st.slider("Impact (1-5)", 1, 5, 3)
    owner = st.text_input("Owner")
    
    if st.button("Add Risk"):
        st.session_state.risks.append({
            "Risk": r_name,
            "Probability": prob,
            "Impact": impact,
            "Score": prob * impact,
            "Owner": owner
        })

if st.session_state.risks:
    df = pd.DataFrame(st.session_state.risks)
    
    st.markdown("### Risk Matrix")
    fig = px.scatter(df, x="Probability", y="Impact", size="Score", color="Score", hover_name="Risk",
                     range_x=[0, 6], range_y=[0, 6], template="plotly_dark")
    st.plotly_chart(fig)
    
    st.markdown("### List")
    st.dataframe(df.sort_values("Score", ascending=False))
