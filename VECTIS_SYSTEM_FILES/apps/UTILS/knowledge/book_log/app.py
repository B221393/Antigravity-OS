"""
📚 Book Insight (読書記録) - 自分ステーション
Port: 8520
読書記録と知識の結晶化を行うアプリ。
"""

import streamlit as st
import json
import os
import requests
from datetime import datetime
import uuid

# Path setup
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from modules.nav import render_global_road, render_station_footer
from modules.style import apply_vectis_style, get_station_header

# Config
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
BOOKS_FILE = os.path.join(DATA_DIR, "books.json")
KCARD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../apps/job_hunting"))

# Page Config
st.set_page_config(page_title="📚 Book Insight | 自分ステーション", page_icon="📚", layout="wide")
apply_vectis_style()

# Custom Styles
st.markdown("""
<style>
    .book-card {
        background: rgba(30, 30, 35, 0.8);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 20px;
        transition: transform 0.2s;
        height: 100%;
    }
    .book-card:hover {
        transform: translateY(-5px);
        border-color: #00FFCC;
    }
    .book-status {
        font-size: 0.75rem;
        padding: 2px 8px;
        border-radius: 10px;
        margin-bottom: 8px;
        display: inline-block;
    }
    .status-reading { background: rgba(0, 255, 204, 0.2); color: #00FFCC; }
    .status-done { background: rgba(100, 100, 255, 0.2); color: #8888FF; }
    .status-wish { background: rgba(255, 165, 0, 0.2); color: #FFA500; }
    
    .insight-box {
        background: rgba(0, 0, 0, 0.3);
        border-left: 3px solid #00FFCC;
        padding: 10px;
        font-size: 0.9em;
        margin-top: 10px;
        color: #ddd;
    }
</style>
""", unsafe_allow_html=True)

# --- Logic ---

def load_books():
    if os.path.exists(BOOKS_FILE):
        try:
            with open(BOOKS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except: pass
    return []

def save_books(books):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

def search_books(query):
    """Google Books API search"""
    url = f"https://www.googleapis.com/books/v1/volumes?q={query}&maxResults=5"
    try:
        res = requests.get(url)
        data = res.json()
        books = []
        if "items" in data:
            for item in data["items"]:
                vol = item.get("volumeInfo", {})
                folder_thumb = vol.get("imageLinks", {}).get("thumbnail", "")
                books.append({
                    "title": vol.get("title", "No Title"),
                    "authors": ", ".join(vol.get("authors", [])),
                    "thumbnail": folder_thumb,
                    "published": vol.get("publishedDate", "")
                })
        return books
    except:
        return []

def export_to_kcard(book):
    """読書データをKnowledge Cardとして保存"""
    card_id = str(uuid.uuid4())[:8]
    filename = f"Book_{book['title'][:10]}_{card_id}.kcard"
    # Remove invalid chars
    filename = "".join([c for c in filename if c.isalnum() or c in (' ', '_', '-', '.')])
    
    content = f"""
    【書籍名】{book['title']}
    【著者】{book['authors']}
    
    【学び・インサイト】
    {book.get('insight', 'No insight recorded.')}
    
    【アクションプラン】
    {book.get('action', '')}
    """
    
    data = {
        "id": card_id,
        "title": f"📚 {book['title']}",
        "genre": "Book Learning",
        "content": content,
        "source": "Book Insight App",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    path = os.path.join(KCARD_DIR, filename)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return True

# --- UI ---

# Sidebar
with st.sidebar:
    render_global_road()
    st.markdown("---")
    
    st.subheader("📖 本の追加")
    search_q = st.text_input("タイトル検索", placeholder="例: 思考の整理学")
    
    if search_q:
        results = search_books(search_q)
        if not results:
            st.caption("見つかりませんでした")
        else:
            for b in results:
                c1, c2 = st.columns([1, 3])
                with c1:
                    if b['thumbnail']: st.image(b['thumbnail'], width=50)
                with c2:
                    st.write(f"**{b['title']}**")
                    st.caption(b['authors'])
                    if st.button("追加", key=f"add_{b['title']}"):
                        books = load_books()
                        new_book = {
                            "id": str(uuid.uuid4()),
                            "title": b['title'],
                            "authors": b['authors'],
                            "thumbnail": b['thumbnail'],
                            "status": "📚 積読 (To Read)",
                            "insight": "",
                            "action": "",
                            "added_at": datetime.now().strftime("%Y-%m-%d")
                        }
                        books.append(new_book)
                        save_books(books)
                        st.success("追加しました")
                        st.rerun()

# Main Header
st.markdown(get_station_header(
    title="📚 Book Insight",
    subtitle="読書を知識に変え、行動に変える",
    channel_id="KNOW.03"
), unsafe_allow_html=True)

books = load_books()

# Filters
filter_status = st.radio("", ["All", "📖 読書中", "✅ 読了", "📚 積読"], horizontal=True)

if not books:
    st.info("👈 サイドバーから本を検索して追加してください。")
else:
    # Filter logic
    filtered_books = books
    if filter_status == "📖 読書中":
        filtered_books = [b for b in books if "読書中" in b['status']]
    elif filter_status == "✅ 読了":
        filtered_books = [b for b in books if "読了" in b['status']]
    elif filter_status == "📚 積読":
        filtered_books = [b for b in books if "積読" in b['status']]
        
    # Grid display
    cols = st.columns(3)
    for i, book in enumerate(filtered_books):
        with cols[i % 3]:
            # Card Container
            with st.container():
                st.markdown(f"""
                <div class="book-card">
                    <div style="display:flex; gap:12px;">
                        <img src="{book['thumbnail']}" style="width:60px; height:90px; object-fit:cover; border-radius:4px;">
                        <div>
                            <div class="book-status status-{'done' if '読了' in book['status'] else 'reading' if '読書中' in book['status'] else 'wish'}">
                                {book['status'].split(' ')[0]}
                            </div>
                            <div style="font-weight:bold; font-size:1em; line-height:1.2;">{book['title']}</div>
                            <div style="font-size:0.8em; color:#aaa; margin-top:4px;">{book['authors']}</div>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Interactive Edit Area
                current_insight = book.get("insight", "")
                
                if "読了" in book['status']:
                    st.markdown(f'<div class="insight-box">{current_insight[:100]}...</div>', unsafe_allow_html=True)
                
                with st.expander("📝 編集 & 学び", expanded=False):
                    new_status = st.selectbox("状態", ["📚 積読 (To Read)", "📖 読書中 (Reading)", "✅ 読了 (Done)"], 
                                            key=f"st_{book['id']}", 
                                            index=["📚", "📖", "✅"].index(book['status'][0]) if book['status'][0] in ["📚", "📖", "✅"] else 0)
                    
                    insight = st.text_area("💡 学び・気づき", value=current_insight, key=f"in_{book['id']}", height=150)
                    action = st.text_input("🚀 明日からどうする？", value=book.get("action",""), key=f"ac_{book['id']}")
                    
                    c_save, c_kcard, c_del = st.columns([1, 1, 1])
                    
                    with c_save:
                        if st.button("保存", key=f"sv_{book['id']}", use_container_width=True):
                            for b in books:
                                if b['id'] == book['id']:
                                    b['status'] = new_status
                                    b['insight'] = insight
                                    b['action'] = action
                            save_books(books)
                            st.rerun()
                    
                    with c_kcard:
                        if st.button("💎 知識化", key=f"kc_{book['id']}", help="Knowledge Cardとして書き出し", use_container_width=True):
                            if export_to_kcard(book):
                                st.toast("Knowledge Cardを作成しました！")
                    
                    with c_del:
                        if st.button("削除", key=f"rm_{book['id']}", use_container_width=True):
                            books = [b for b in books if b['id'] != book['id']]
                            save_books(books)
                            st.rerun()
                
                st.markdown("</div>", unsafe_allow_html=True)

render_station_footer()
