
import streamlit as st

def apply_vectis_style():
    """
    自分ステーション統一デザインシステム v3.0 (Space Edition)
    Theme: "Orbit Control"
    Concept: 宇宙から地球を見下ろすような広大な視点と、佐久間宣行氏のHPのような
             「プロデューサー的」で「ボールド」なタイポグラフィ、そして洗練されたグラスモーフィズム。
    """
    st.markdown("""
        <!-- Import Fonts -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;700;900&family=Oswald:wght@500;700&family=Share+Tech+Mono&display=swap" rel="stylesheet">
        
        <style>
        /* ============================================
           VECTIS OS - GLOBAL THEME v3.0
           ============================================ */
        
        :root {
            /* Palette: Deep Space & Starlight */
            --glass-bg: rgba(16, 20, 28, 0.65);
            --glass-border: rgba(255, 255, 255, 0.15);
            --glass-highlight: rgba(255, 255, 255, 0.05);
            
            --accent-primary: #FFFFFF; /* Pure White like stars */
            --accent-secondary: #00E5FF; /* Cyan */
            --accent-alert: #FF3366; /* Magenta-Red */
            
            --text-main: #FFFFFF;
            --text-sub: #A0AEC0;
            
            --font-display: 'Oswald', sans-serif;
            --font-body: 'Noto Sans JP', sans-serif;
            --font-mono: 'Share Tech Mono', monospace;
        }

        /* Background Image: Earth from Space (High Res) */
        .stApp {
            background-image: url("https://images.unsplash.com/photo-1451187580459-43490279c0fa?q=80&w=2672&auto=format&fit=crop");
            background-size: cover;
            background-position: center center;
            background-attachment: fixed;
            background-repeat: no-repeat;
        }
        
        /* Darken overlay to ensure text readability */
        .stApp::before {
            content: "";
            position: fixed;
            top: 0; 
            left: 0;
            width: 100%; 
            height: 100%;
            background: rgba(5, 8, 16, 0.6); /* Deep blue-black tint */
            z-index: 0;
            pointer-events: none;
        }

        /* Content Wrapper */
        .main > .block-container {
            position: relative;
            z-index: 1;
            padding-top: 2rem;
            max-width: 1200px;
        }

        /* ============================================
           Typography
           ============================================ */
        h1, h2, h3 {
            font-family: var(--font-display) !important;
            letter-spacing: 0.05em !important;
            text-transform: uppercase;
            color: var(--text-main) !important;
            text-shadow: 0 4px 12px rgba(0,0,0,0.5);
        }

        h1 {
            font-size: 3.5rem !important;
            font-weight: 700 !important;
            border-bottom: none !important;
            margin-bottom: 0.5rem !important;
        }
        
        h2 {
            font-size: 1.8rem !important;
            border-left: 6px solid var(--accent-secondary);
            padding-left: 16px;
            margin-top: 2rem !important;
            background: linear-gradient(90deg, rgba(0, 229, 255, 0.1) 0%, transparent 100%);
        }

        p, li, span, div {
            font-family: var(--font-body);
            color: var(--text-main);
        }

        /* ============================================
           Sidebar
           ============================================ */
        [data-testid="stSidebar"] {
            background: rgba(8, 12, 18, 0.85) !important;
            backdrop-filter: blur(20px);
            border-right: 1px solid rgba(255,255,255,0.08);
        }
        
        [data-testid="stSidebar"] .stMarkdown h1,
        [data-testid="stSidebar"] .stMarkdown h2,
        [data-testid="stSidebar"] .stMarkdown h3 {
             font-family: var(--font-display) !important;
        }

        /* ============================================
           Cards / Containers (Glassmorphism)
           ============================================ */
        .station-card {
            background: var(--glass-bg);
            border: 1px solid var(--glass-border);
            border-radius: 4px; /* Sharper corners for a "Tech" feel */
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(12px);
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            position: relative;
            overflow: hidden;
        }
        
        /* Hover Effect for Cards */
        .station-card:hover {
            transform: translateY(-4px);
            border-color: var(--accent-secondary);
            box-shadow: 0 12px 48px rgba(0, 229, 255, 0.2);
            background: rgba(20, 30, 45, 0.85);
        }
        
        /* Subtle "scan" line on hover */
        .station-card::after {
            content: "";
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transform: skewX(-20deg);
            transition: 0.5s;
        }
        .station-card:hover::after {
            left: 150%;
            transition: 0.5s;
        }

        /* Badges */
        .station-badge {
            display: inline-block;
            font-family: var(--font-mono);
            font-size: 0.65rem;
            font-weight: 700;
            color: var(--accent-secondary);
            border: 1px solid var(--accent-secondary);
            padding: 2px 8px;
            text-transform: uppercase;
            letter-spacing: 1px;
            background: rgba(0, 229, 255, 0.1);
        }
        
        .station-badge-blue {
            /* Default cyan style */
        }

        /* ============================================
           Buttons
           ============================================ */
        .stButton > button {
            border-radius: 2px;
            border: 1px solid var(--text-main);
            background: transparent;
            color: var(--text-main);
            font-family: var(--font-display);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            padding: 0.6rem 1.2rem;
            transition: all 0.2s;
        }

        .stButton > button:hover {
            background: var(--text-main);
            color: #000; /* Invert */
            box-shadow: 0 0 15px rgba(255,255,255,0.5);
            border-color: var(--text-main);
        }

        /* Primary Button */
        .stButton > button[kind="primary"] {
            background: var(--accent-secondary);
            border-color: var(--accent-secondary);
            color: #000;
        }
        
        .stButton > button[kind="primary"]:hover {
            background: #fff;
            border-color: #fff;
            box-shadow: 0 0 20px var(--accent-secondary);
        }

        /* ============================================
           Tabs
           ============================================ */
        .stTabs [data-baseweb="tab-list"] {
            gap: 2rem;
            border-bottom: 1px solid rgba(255,255,255,0.2);
            padding-bottom: 5px;
        }
        
        .stTabs [data-baseweb="tab"] {
            background: transparent;
            border: none;
            color: var(--text-sub);
            font-family: var(--font-display);
            font-size: 1.1rem;
            padding: 0 10px 10px 10px;
        }
        
        .stTabs [aria-selected="true"] {
             color: var(--accent-secondary) !important;
             border-bottom: 2px solid var(--accent-secondary);
             text-shadow: 0 0 10px var(--accent-secondary);
        }

        /* ============================================
           Status Online Indicator
           ============================================ */
        .status-online {
            font-family: var(--font-mono);
            color: var(--accent-secondary);
            display: flex;
            align-items: center;
            gap: 6px;
        }
        .status-online::before {
            content: "";
            display: inline-block;
            width: 8px; height: 8px;
            background-color: var(--accent-secondary);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--accent-secondary);
        }

        /* ============================================
           Metrics & Charts
           ============================================ */
        [data-testid="stMetric"] {
            background: rgba(0,0,0,0.4);
            backdrop-filter: blur(5px);
            padding: 15px;
            border-left: 2px solid var(--accent-secondary);
        }
        [data-testid="stMetricValue"] {
            font-family: var(--font-mono);
            color: var(--text-main) !important;
        }
        
        /* Scrollbar */
        ::-webkit-scrollbar {
            width: 8px;
            background: #000;
        }
        ::-webkit-scrollbar-thumb {
            background: #333;
            border-radius: 4px;
        }
        ::-webkit-scrollbar-thumb:hover {
            background: var(--accent-secondary);
        }

        </style>
    """, unsafe_allow_html=True)


def get_station_header(title: str, subtitle: str = "", channel_id: str = ""):
    """Unified Header for Space Theme"""
    return f"""
    <div style="margin-bottom: 40px; border-bottom: 1px solid rgba(255,255,255,0.2); padding-bottom: 20px;">
        <div style="display: flex; justify-content: space-between; align-items: flex-end;">
            <div>
                <div class="status-online" style="margin-bottom: 8px;">{channel_id} /// SIGNAL_LOCKED</div>
                <h1 style="margin: 0; line-height: 1;">{title}</h1>
            </div>
            <div style="text-align: right; font-family: 'Share Tech Mono'; color: rgba(255,255,255,0.6);">
                VECTIS OS<br>v3.0.1
            </div>
        </div>
        <p style="margin-top: 10px; font-size: 1.1rem; color: #ccc; max-width: 600px;">{subtitle}</p>
    </div>
    """
