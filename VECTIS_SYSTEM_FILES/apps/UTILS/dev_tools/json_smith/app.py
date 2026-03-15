import streamlit as st
import json
import jq

st.set_page_config(page_title="JSON Smith", page_icon="🔨")
st.title("🔨 JSON Smith [Rank 30]")

st.subheader("Validator & JQ Query")

txt = st.text_area("Input JSON", height=300)

c1, c2 = st.columns(2)
query = c1.text_input("JQ Filter", ".")

if st.button("Process"):
    if txt:
        try:
            data = json.loads(txt)
            st.success("✅ Valid JSON")
            
            # JQ
            try:
                res = jq.compile(query).input(data).all()
                st.subheader("Result")
                st.json(res)
            except Exception as e:
                st.error(f"JQ Error: {e}")
                st.json(data)
                
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid: {e}")
