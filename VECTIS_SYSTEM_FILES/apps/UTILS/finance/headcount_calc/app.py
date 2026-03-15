import streamlit as st
import pandas as pd

st.set_page_config(page_title="Headcount Calc", page_icon="👥")
st.title("👥 Headcount & Budget Planner")

# Settings
st.sidebar.header("Parameters")
months = st.sidebar.slider("Projection Months", 1, 36, 12)
social_tax = st.sidebar.number_input("Social Security Load %", 0, 50, 15)

# Roles
if 'roles' not in st.session_state:
    st.session_state.roles = [
        {"Role": "Engineer", "Count": 2, "Salary": 600000},
        {"Role": "Designer", "Count": 1, "Salary": 500000}
    ]

with st.expander("Add Role"):
    r = st.text_input("Role Name")
    c = st.number_input("Count", 1, 100, 1)
    s = st.number_input("Monthly Salary", 100000, 2000000, 500000)
    if st.button("Add"):
        st.session_state.roles.append({"Role": r, "Count": c, "Salary": s})
        st.rerun()

# Calc
total_monthly = 0
for role in st.session_state.roles:
    cost = role["Count"] * role["Salary"] * (1 + social_tax/100)
    total_monthly += cost

st.markdown(f"### Monthly Burn: **¥{total_monthly:,.0f}**")
st.markdown(f"### Annual Burn: **¥{total_monthly*12:,.0f}**")

# Chart
data = []
cum = 0
for m in range(1, months + 1):
    cum += total_monthly
    data.append({"Month": m, "Cumulative Cost": cum})

df = pd.DataFrame(data)
st.line_chart(df, x="Month", y="Cumulative Cost")

st.table(pd.DataFrame(st.session_state.roles))
