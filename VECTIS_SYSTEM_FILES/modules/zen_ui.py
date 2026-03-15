import streamlit as st
import datetime

def apply_zen_style():
    """
    Applies VECTIS Zen Design System to Streamlit Apps.
    Dynamic switching based on time (Day/Night).
    """
    
    # Time Logic (Server Time)
    now = datetime.datetime.now()
    hour = now.hour
    is_focus_mode = (hour >= 20 or hour < 6)
    
    # Theme Variables
    if is_focus_mode:
        # Focus Mode (Night)
        bg_color = "#000000"
        card_bg = "#121212"
        text_color = "#e5e5e7"
        text_sub = "#86868b"
        accent = "#ffffff"
    else:
        # Admin Mode (Day)
        bg_color = "#f5f5f7"
        card_bg = "#ffffff"
        text_color = "#1d1d1f"
        text_sub = "#86868b"
        accent = "#0066cc"

    # CSS Injection
    css = f"""
    <style>
        /* Global Reset for Streamlit */
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
            font-family: 'Inter', sans-serif;
        }}
        
        /* Headers */
        h1, h2, h3 {{
            color: {text_color} !important;
            font-family: 'Inter', sans-serif !important;
            font-weight: 600 !important;
        }}
        
        h1 {{ letter-spacing: -0.5px; }}
        
        /* Buttons (Vectis Style) */
        .stButton button {{
            background-color: transparent !important;
            border: 1px solid {text_sub} !important;
            color: {text_color} !important;
            border-radius: 20px !important;
            padding: 8px 24px !important;
            transition: all 0.3s ease !important;
        }}
        
        .stButton button:hover {{
            background-color: {text_color} !important;
            color: {bg_color} !important;
            border-color: {text_color} !important;
        }}
        
        /* DataFrame / Tables */
        .stDataFrame {{
            border: 1px solid {text_sub} !important;
            border-radius: 12px !important;
            overflow: hidden !important;
        }}
        
        /* Hide Streamlit Decorations */
        #MainMenu {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        header {{visibility: hidden;}}
        
        /* Custom Cards (You can use st.markdown('<div class="zen-card">...</div>') */
        .zen-card {{
            background-color: {card_bg};
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            margin-bottom: 20px;
        }}
        
        /* Success/Info Alerts */
        .stAlert {{
            background-color: {card_bg} !important;
            color: {text_color} !important;
            border: 1px solid {text_sub} !important;
        }}
        
    </style>
    """
    
    st.markdown(css, unsafe_allow_html=True)
    
    # Sidebar Info
    with st.sidebar:
        st.markdown(f"""
        <div style='text-align:center; padding: 20px 0;'>
            <h3 style='color:{text_sub}; font-size:14px; text-transform:uppercase;'>VECTIS Mode</h3>
            <h1 style='color:{accent}; font-size:24px;'>{'FOCUS' if is_focus_mode else 'ADMIN'}</h1>
        </div>
        """, unsafe_allow_html=True)

