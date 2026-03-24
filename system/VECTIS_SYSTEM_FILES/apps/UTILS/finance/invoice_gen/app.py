import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import os
# VECTIS共通スタイル
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
try:
    from modules.style import apply_vectis_style
    apply_vectis_style()
except: pass
from datetime import datetime

st.set_page_config(page_title="Invoice Gen", page_icon="🧾")
st.title("🧾 Invoice Gen [Rank 41]")

c1, c2 = st.columns(2)
client = c1.text_input("Client Name", "Client Inc.")
my_name = c2.text_input("My Name / Company", "Yuto Studio")
inv_num = c1.text_input("Invoice #", f"INV-{datetime.now().strftime('%Y%m%d')}")
reg_num = c2.text_input("Registration # (T-Num)", "T1234567890123")

items = []
if 'items' not in st.session_state: st.session_state.items = [{"desc": "Service A", "price": 10000}]

for i, item in enumerate(st.session_state.items):
    cols = st.columns([3, 1])
    item['desc'] = cols[0].text_input(f"Item {i+1}", item['desc'])
    item['price'] = cols[1].number_input(f"Price {i+1}", value=item['price'])

if st.button("Add Item"):
    st.session_state.items.append({"desc": "", "price": 0})
    st.rerun()

total = sum([x['price'] for x in st.session_state.items])
tax = total * 0.1
grand = total + tax

st.metric("Grand Total", f"¥{grand:,.0f}")

if st.button("Generate PDF"):
    fn = f"Invoice_{inv_num}.pdf"
    p = canvas.Canvas(fn, pagesize=A4)
    
    # Font attempt (Default strictly doesn't support JP, need ttf)
    # We will fallback to Helvetica and warn if JP chars used, OR try to find a system font.
    # For CI/Cloud, usually no JP font. locally we might find msgothic.ttc
    
    font_path = "C:\\Windows\\Fonts\\msmincho.ttc"
    if os.path.exists(font_path):
        try:
            pdfmetrics.registerFont(TTFont('Mincho', font_path))
            p.setFont('Mincho', 12)
        except: pass
    else:
        st.warning("JP Font not found, using default. English only recommended.")
    
    p.drawString(50, 800, f"INVOICE: {inv_num}")
    p.drawString(50, 780, f"To: {client}")
    p.drawString(300, 780, f"From: {my_name} ({reg_num})")
    
    y = 700
    p.drawString(50, y, "Description")
    p.drawString(400, y, "Price")
    y -= 20
    p.line(50, y+15, 500, y+15)
    
    for item in st.session_state.items:
        p.drawString(50, y, item['desc'])
        p.drawString(400, y, f"{item['price']:,}")
        y -= 20
        
    y -= 20
    p.line(50, y+15, 500, y+15)
    p.drawString(300, y, f"Subtotal: {total:,}")
    y -= 20
    p.drawString(300, y, f"Tax (10%): {tax:,}")
    y -= 20
    p.setFont("Helvetica-Bold", 14)
    p.drawString(300, y, f"Total: {grand:,.0f}")
    
    p.save()
    st.success(f"Generated: {fn}")
    with open(fn, "rb") as f:
        st.download_button("Download PDF", f, file_name=fn)
