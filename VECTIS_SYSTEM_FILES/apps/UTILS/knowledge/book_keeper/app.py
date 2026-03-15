import streamlit as st
import pandas as pd
import json
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
import requests

st.set_page_config(page_title="Book Keeper", page_icon="📚")
st.title("📚 Book Keeper [Rank 18]")

DB_FILE = "books.json"

if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w") as f: json.dump([], f)

with open(DB_FILE, "r") as f: books = json.load(f)

# ISBN Search Integration
isbn = st.text_input("ISBN Search (OpenBD)", placeholder="9784...")
if st.button("Fetch Info") and isbn:
    try:
        url = f"https://api.openbd.jp/v1/get?isbn={isbn}"
        res = requests.get(url).json()
        if res and res[0]:
            info = res[0]['summary']
            st.session_state['new_title'] = info.get('title', '')
            st.session_state['new_author'] = info.get('author', '')
            st.success("Found!")
        else:
            st.error("Not found.")
    except Exception as e:
        st.error(f"Error: {e}")

with st.expander("Add New Book", expanded=True):
    title = st.text_input("Title", value=st.session_state.get('new_title', ''))
    author = st.text_input("Author", value=st.session_state.get('new_author', ''))
    status = st.selectbox("Status", ["To Read", "Reading", "Finished"])
    rating = st.slider("Rating", 1, 5, 3)
    
    if st.button("Add Book"):
        books.append({
            "Title": title, "Author": author, "Status": status, "Rating": rating
        })
        with open(DB_FILE, "w") as f: json.dump(books, f)
        st.success("Added!")

# List
if books:
    df = pd.DataFrame(books)
    st.table(df)
