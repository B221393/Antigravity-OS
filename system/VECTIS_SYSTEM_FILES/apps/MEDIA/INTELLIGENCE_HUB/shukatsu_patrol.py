"""
EGO 就活インテリジェンスパトロール
====================================
出版社・メディア業界を中心に、27卒（2027年卒業）向けの就活情報を自動収集

対象:
- 出版社ES/インターン情報
- メディア業界ニュース
- 就活一般トレンド
- 企業分析情報
"""

import os
import sys
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
import json
import time
import random
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
import re
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# Setup Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Load .env from root
load_dotenv(os.path.join(BASE_DIR, "../../..", ".env"))
DATA_DIR = os.path.join(BASE_DIR, "data")
SHUKATSU_DIR = os.path.join(DATA_DIR, "shukatsu")
os.makedirs(SHUKATSU_DIR, exist_ok=True)

# Add modules path
sys.path.insert(0, os.path.abspath(os.path.join(BASE_DIR, "../../..")))

# Import LLM - 統合クライアント（Gemini → Groq → Ollama）
try:
    from modules.unified_llm_client import ask_llm, get_available_providers
    providers = get_available_providers()
    if providers:
        llm = "unified"
        print(f"[LLM] Available: {', '.join(providers)}")
    else:
        llm = None
        print("[WARN] No LLM providers available. Will save raw data only.")
except Exception as e:
    llm = None
    print(f"[WARN] LLM not available ({e}). Will save raw data only.")

# Import Researcher for Deep Dives
try:
    from modules.researcher import Researcher
    deep_researcher = Researcher()
except:
    deep_researcher = None

# Import Visual Cortex (OCR Service)
try:
    sys.path.append(os.path.join(BASE_DIR, "../../AI_LAB/vision_cortex"))
    from ocr_service import image_to_markdown
except Exception as e:
    print(f"[WARN] Visual Cortex not linked: {e}")
    def image_to_markdown(path): return ""

# ===== 就活特化ソース =====
SHUKATSU_SOURCES = {
    # === 就活一般 ===
    "1": ("就活ニュース (Google)", "https://news.google.com/rss/search?q=%E5%B0%B1%E6%B4%BB+2027&hl=ja&gl=JP&ceid=JP:ja"),
    "2": ("ES締切 (Google)", "https://news.google.com/rss/search?q=ES%E7%B7%A0%E5%88%87+27%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),
    "3": ("インターン (Google)", "https://news.google.com/rss/search?q=%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%B3+2027&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === Deep Dive & Targeted Analysis (Deep Search) ===
    # User Request: 深く、広範囲に、KDDIなど
    "50": ("KDDI 採用 Deep Dive", "https://news.google.com/rss/search?q=KDDI+%E6%8E%A1%E7%94%A8+%E6%88%A6%E7%95%A5+%E6%96%B0%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),
    "51": ("KDDI 事業戦略", "https://news.google.com/rss/search?q=KDDI+%E4%BA%8B%E6%A5%AD%E6%88%A6%E7%95%A5+%E4%B8%AD%E6%9C%9F%E7%B5%8C%E5%96%B6%E8%A8%88%E7%94%BB&hl=ja&gl=JP&ceid=JP:ja"),
    "52": ("通信業界 トレンド", "https://news.google.com/rss/search?q=%E9%80%9A%E4%BF%A1%E6%A5%AD%E7%95%8C+%E3%83%88%E3%83%AC%E3%83%B3%E3%83%89+2026+2027&hl=ja&gl=JP&ceid=JP:ja"),
    "53": ("トヨタ自動車 戦略", "https://news.google.com/rss/search?q=%E3%83%88%E3%83%A8%E3%82%BF%E8%87%AA%E5%8B%95%E8%BB%8A+%E6%8E%A1%E7%94%A8+%E6%88%A6%E7%95%A5&hl=ja&gl=JP&ceid=JP:ja"),
    "54": ("ソニーグループ 戦略", "https://news.google.com/rss/search?q=%E3%82%BD%E3%83%8B%E3%83%BC+%E6%8E%A1%E7%94%A8+%E6%96%B0%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),
    "55": ("キーエンス", "https://news.google.com/rss/search?q=%E3%82%AD%E3%83%BC%E3%82%A8%E3%83%B3%E3%82%B9+%E6%8E%A1%E7%94%A8+%E6%BF%80%E5%8A%A1&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 教養・リベラルアーツ (Liberal Arts) ===
    # User Request: 普通に教養についても
    "60": ("リベラルアーツ トレンド", "https://news.google.com/rss/search?q=%E3%83%AA%E3%83%99%E3%83%A9%E3%83%AB%E3%82%A2%E3%83%BC%E3%83%84+%E3%83%88%E3%83%AC%E3%83%B3%E3%83%89+%E6%95%99%E9%A4%8A&hl=ja&gl=JP&ceid=JP:ja"),
    "61": ("科学技術 社会論", "https://news.google.com/rss/search?q=%E7%A7%91%E5%AD%A6%E6%8A%80%E8%A1%93+%E7%A4%BE%E4%BC%9A+%E8%AB%96%E7%82%B9&hl=ja&gl=JP&ceid=JP:ja"),
    "62": ("現代思想 入門", "https://news.google.com/rss/search?q=%E7%8F%BE%E4%BB%A3%E6%80%9D%E6%83%B3+%E5%85%A5%E9%96%80+%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9&hl=ja&gl=JP&ceid=JP:ja"),
    "63": ("歴史的背景 ニュース", "https://news.google.com/rss/search?q=%E6%AD%B4%E5%8F%B2%E7%9A%84%E8%83%8C%E6%99%AF+%E3%83%8B%E3%83%A5%E3%83%BC%E3%82%B9+%E8%A7%A3%E8%AA%AC&hl=ja&gl=JP&ceid=JP:ja"),

    "10": ("広告業界", "https://news.google.com/rss/search?q=%E5%BA%83%E5%91%8A%E6%A5%AD%E7%95%8C+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "11": ("電通", "https://news.google.com/rss/search?q=%E9%9B%BB%E9%80%9A+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "12": ("博報堂", "https://news.google.com/rss/search?q=%E5%8D%9A%E5%A0%B1%E5%A0%82+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 外資系 ===
    "13": ("P&G 採用", "https://news.google.com/rss/search?q=P%26G+%E6%8E%A1%E7%94%A8+%E6%97%A5%E6%9C%AC&hl=ja&gl=JP&ceid=JP:ja"),
    "14": ("外資メーカー", "https://news.google.com/rss/search?q=%E5%A4%96%E8%B3%87%E3%83%A1%E3%83%BC%E3%82%AB%E3%83%BC+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "15": ("外資就活", "https://news.google.com/rss/search?q=%E5%A4%96%E8%B3%87%E5%B0%B1%E6%B4%BB&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 兵庫県・関西企業 ===
    "16": ("神戸・兵庫 採用総合", "https://news.google.com/rss/search?q=%E7%A5%9E%E6%88%B8+%E4%BC%81%E6%A5%AD+%E6%8E%A1%E7%94%A8+%E6%96%B0%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),
    "17": ("兵庫県庁 採用", "https://news.google.com/rss/search?q=%E5%85%B5%E5%BA%AB%E7%9C%8C%E5%BA%81+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "18": ("川崎重工 採用", "https://news.google.com/rss/search?q=%E5%B7%9D%E5%B4%8E%E9%87%8D%E5%B7%A5+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "19": ("神戸製鋼 採用", "https://news.google.com/rss/search?q=%E7%A5%9E%E6%88%B8%E8%A3%BD%E9%8B%BC+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "28": ("アシックス 採用", "https://news.google.com/rss/search?q=ASICS+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "29": ("シスメックス 採用", "https://news.google.com/rss/search?q=%E3%82%B7%E3%82%B9%E3%83%A1%E3%83%83%E3%82%AF%E3%82%B9+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "30": ("TOA 採用", "https://news.google.com/rss/search?q=TOA+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "31": ("UCC上島珈琲 採用", "https://news.google.com/rss/search?q=UCC%E4%B8%8A%E5%B3%B6%E7%8F%88%E7%90%B2+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "32": ("ワールド 採用", "https://news.google.com/rss/search?q=%E6%A0%AA%E5%BC%8F%E4%BC%9A%E7%A4%BE%E3%83%AF%E3%83%BC%E3%83%AB%E3%83%89+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "33": ("フェリシモ 採用", "https://news.google.com/rss/search?q=%E3%83%95%E3%82%A7%E3%83%AA%E3%82%B7%E3%83%A2+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "34": ("神戸物産 採用", "https://news.google.com/rss/search?q=%E7%A5%9E%E6%88%B8%E7%89%A9%E7%94%A3+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "35": ("TOYO TIRE 採用", "https://news.google.com/rss/search?q=TOYO+TIRE+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "36": ("ノーリツ 採用", "https://news.google.com/rss/search?q=%E3%83%8E%E3%83%BC%E3%83%AA%E3%83%84+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 就活メディア (Fixed to Google News for stability) ===
    "20": ("ONE CAREER関連", "https://news.google.com/rss/search?q=ONE+CAREER+%E5%B0%B1%E6%B4%BB&hl=ja&gl=JP&ceid=JP:ja"),
    "21": ("東洋経済 (企業)", "https://news.google.com/rss/search?q=%E6%9D%B1%E6%B4%8B%E7%B5%8C%E6%B8%88+%E4%BC%81%E6%A5%AD+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "22": ("ダイヤモンド", "https://news.google.com/rss/search?q=%E3%83%80%E3%82%A4%E3%83%A4%E3%83%A2%E3%83%B3%E3%83%89%E3%82%AA%E3%83%B3%E3%83%A9%E3%82%A4%E3%83%B3+%E3%82%AD%E3%83%A3%E3%83%AA%E3%82%A2&hl=ja&gl=JP&ceid=JP:ja"),
    
    "23": ("国家公務員 総合職", "https://news.google.com/rss/search?q=%E5%9B%BD%E5%AE%B6%E5%85%AC%E5%8B%99%E5%93%A1+%E7%B7%8F%E5%90%88%E8%81%B7&hl=ja&gl=JP&ceid=JP:ja"),
    "24": ("官報訪問", "https://news.google.com/rss/search?q=%E5%AE%98%E5%BA%9C%E8%AE%AA%E5%95%8F+2027&hl=ja&gl=JP&ceid=JP:ja"),
    "25": ("外務省 採用", "https://news.google.com/rss/search?q=%E5%A4%96%E5%8B%99%E7%9C%81+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "26": ("経産省 採用", "https://news.google.com/rss/search?q=%E7%B5%8C%E6%B8%88%E7%94%A3%E6%A5%AD%E7%9C%81+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "27": ("財務省 採用", "https://news.google.com/rss/search?q=%E8%B2%A1%E5%8B%99%E7%9C%81+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),

    # === インフラ・エネルギー ===
    "40": ("JERA", "https://news.google.com/rss/search?q=JERA+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "41": ("東京ガス", "https://news.google.com/rss/search?q=%E6%9D%B1%E4%BA%AC%E3%82%AC%E3%82%B9+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "42": ("関西電力", "https://news.google.com/rss/search?q=%E9%96%A2%E8%A5%BF%E9%9B%BB%E5%8A%9B+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),

    # === 公務員（技術職・理系） ===
    "110": ("公務員 技術職 機械", "https://news.google.com/rss/search?q=%E5%85%AC%E5%8B%99%E5%93%A1+%E6%8A%80%E8%A1%93%E8%81%B7+%E6%A9%9F%E6%A2%B0+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    "111": ("国家公務員 技術区分", "https://news.google.com/rss/search?q=%E5%9B%BD%E5%AE%B6%E5%85%AC%E5%8B%99%E5%93%A1+%E6%95%99%E9%A4%8A%E5%8C%BA%E5%88%86+%E6%8A%80%E8%A1%93&hl=ja&gl=JP&ceid=JP:ja"),
    "112": ("地方上級 技術職 過去問", "https://news.google.com/rss/search?q=%E5%9C%B0%E6%96%B9%E4%B8%8A%E7%B4%9A+%E6%8A%80%E8%A1%93%E8%81%B7+%E8%A9%A6%E9%A8%93%E6%97%A5%E7%A8%8B+2026&hl=ja&gl=JP&ceid=JP:ja"),
    "113": ("神戸市 技術職 採用", "https://news.google.com/rss/search?q=%E7%A5%9E%E6%88%B8%E5%B8%82+%E6%8E%A1%E7%94%A8+%E6%8A%80%E8%A1%93%E8%81%B7+%E5%A4%A7%E5%8D%92&hl=ja&gl=JP&ceid=JP:ja"),

    # === KDDI Service Ecosystem (Deep Dive) ===
    "200": ("KDDI DX Service", "https://news.google.com/rss/search?q=KDDI+DX+%E3%82%B5%E3%83%BC%E3%83%93%E3%82%B9+%E4%BA%8B%E4%BE%8B&hl=ja&gl=JP&ceid=JP:ja"),
    "201": ("au Financial Ecosystem", "https://news.google.com/rss/search?q=au%E3%82%B8%E3%83%96%E3%83%B3%E9%8A%80%E8%A1%8C+%E9%87%91%E8%9E%8D+%E6%88%A6%E7%95%A5&hl=ja&gl=JP&ceid=JP:ja"),
    "202": ("KDDI Smart Drone", "https://news.google.com/rss/search?q=KDDI+%E3%82%B9%E3%83%9E%E3%83%BC%E3%83%88%E3%83%89%E3%83%AD%E3%83%BC%E3%83%B3+%E4%BA%8B%E6%A5%AD&hl=ja&gl=JP&ceid=JP:ja"),
    "203": ("KDDI IoT Projects", "https://news.google.com/rss/search?q=KDDI+IoT+%E5%B0%8E%E5%85%A5%E4%BA%8B%E4%BE%8B+%E3%82%BD%E3%83%AA%E3%83%A5%E3%83%BC%E3%82%B7%E3%83%A7%E3%83%B3&hl=ja&gl=JP&ceid=JP:ja"),
    "204": ("KDDI Agile Development", "https://news.google.com/rss/search?q=KDDI+%E3%82%A2%E3%82%B8%E3%83%A3%E3%82%A4%E3%83%AB%E9%96%8B%E7%99%BA+%E3%82%BB%E3%83%B3%E3%82%BF%E3%83%BC&hl=ja&gl=JP&ceid=JP:ja"),
    "205": ("Starlink Japan Business", "https://news.google.com/rss/search?q=Starlink+KDDI+%E6%B3%95%E4%BA%BA+%E5%B0%8E%E5%85%A5&hl=ja&gl=JP&ceid=JP:ja"),
    "206": ("Lawson KDDI Strategy", "https://news.google.com/rss/search?q=%E3%83%AD%E3%83%BC%E3%82%BD%E3%83%B3+KDDI+%E3%83%87%E3%82%B8%E3%82%BF%E3%83%AB%E6%88%A6%E7%95%A5&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === Failure Analysis & Deep Tech (The "More" Request) ===
    "300": ("KDDI 面接 落ちた 理由", "https://news.google.com/rss/search?q=KDDI+%E9%9D%A2%E6%8E%A5+%E8%90%BD%E3%81%A1%E3%81%9F+%E7%90%86%E7%94%B1+%E4%BD%93%E9%A8%93%E8%AB%87&hl=ja&gl=JP&ceid=JP:ja"),
    "301": ("エンジニア ES 通過しない 特徴", "https://news.google.com/rss/search?q=%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2+ES+%E9%80%9A%E9%81%8E%E3%81%97%E3%81%AA%E3%81%84+%E7%89%B9%E5%BE%B4&hl=ja&gl=JP&ceid=JP:ja"),
    "302": ("KDDI 技術面接 質問", "https://news.google.com/rss/search?q=KDDI+%E6%8A%80%E8%A1%93%E9%9D%A2%E6%8E%A5+%E8%B3%AA%E5%95%8F%E5%86%85%E5%AE%B9+%E5%9B%B0%E9%9B%A3&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 新規追加: 戦略ソース (Fixed broken feeds) ===
    "70": ("PR TIMES (就活/インターン)", "https://news.google.com/rss/search?q=site:prtimes.jp+(%E5%B0%B1%E6%B4%BB+OR+%E3%82%A4%E3%83%B3%E3%82%BF%E3%83%BC%E3%83%B3)&hl=ja&gl=JP&ceid=JP:ja"),
    "71": ("PR TIMES (AI/DX)", "https://news.google.com/rss/search?q=site:prtimes.jp+(AI+OR+DX)&hl=ja&gl=JP&ceid=JP:ja"),
    "72": ("ITmedia ニュース", "https://news.google.com/rss/search?q=site:itmedia.co.jp&hl=ja&gl=JP&ceid=JP:ja"),
    "73": ("TechCrunch JP (Archive)", "https://news.google.com/rss/search?q=TechCrunch+Japan&hl=ja&gl=JP&ceid=JP:ja"),
    "74": ("Nikkei ビジネス", "https://news.google.com/rss/search?q=%E6%97%A5%E7%B5%8C%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9+%E6%88%A6%E7%95%A5&hl=ja&gl=JP&ceid=JP:ja"),
    "75": ("ロイター 企業ニュース", "https://news.google.com/rss/search?q=Reuters+%E4%BC%81%E6%A5%AD+%E6%8E%A1%E7%94%A8&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 教養・リベラルアーツ (Deep Knowledge) ===
    "80": ("現代思想 (Google)", "https://news.google.com/rss/search?q=%E7%8F%BE%E4%BB%A3%E6%80%9D%E6%83%B3+%E5%93%B2%E5%AD%A6&hl=ja&gl=JP&ceid=JP:ja"),
    "81": ("科学史・技術史", "https://news.google.com/rss/search?q=%E7%A7%91%E5%AD%A6%E5%8F%B2+%E6%8A%80%E8%A1%93%E5%8F%B2&hl=ja&gl=JP&ceid=JP:ja"),
    "82": ("WIRED JP (Ideas)", "https://news.google.com/rss/search?q=site:wired.jp&hl=ja&gl=JP&ceid=JP:ja"),
    "83": ("National Geographic JP", "https://news.google.com/rss/search?q=site:natgeo.nikkeibp.co.jp&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === ES・スキル・選考対策 (Career Tactics) ===
    "90": ("ES 書き方 (Google)", "https://news.google.com/rss/search?q=ES+%E6%9B%B8%E3%81%8D%E6%96%B9+%E9%80%9A%E9%81%8E%E7%8E%87+%E3%82%B3%E3%83%84&hl=ja&gl=JP&ceid=JP:ja"),
    "91": ("面接対策 トレンド", "https://news.google.com/rss/search?q=%E5%B0%B1%E6%B4%BB+%E9%9D%A2%E6%8E%A5+%E5%AF%BE%E7%AD%96+%E9%80%86%E8%B3%AA%E5%95%8F&hl=ja&gl=JP&ceid=JP:ja"),
    "92": ("Webテスト 攻略", "https://news.google.com/rss/search?q=SPI+Web%E3%83%86%E3%82%B9%E3%83%88+%E7%8E%89%E6%89%8B%E7%AE%B1+%E5%AF%BE%E7%AD%96&hl=ja&gl=JP&ceid=JP:ja"),
    "93": ("自己分析 深掘り", "https://news.google.com/rss/search?q=%E8%87%AA%E5%B7%B1%E5%88%86%E6%9E%90+%E3%82%YI%E3%83%AB+%E3%82%AD%E3%83%A3%E3%83%AA%E3%82%A2%E8%A8%AD%E8%A8%88&hl=ja&gl=JP&ceid=JP:ja"),
    
    # === 【NEW】ES Examples & Writing Styles (Massive Expansion) ===
    "100": ("KDDI ES 通過", "https://news.google.com/rss/search?q=KDDI+%E3%82%A8%E3%83%B3%E3%83%88%E3%83%AA%E3%83%BC%E3%82%B7%E3%83%BC%E3%83%88+%E9%80%9A%E9%81%8E&hl=ja&gl=JP&ceid=JP:ja"),
    "101": ("エンジニア ES 例文", "https://news.google.com/rss/search?q=%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2+ES+%E4%BE%8B%E6%96%87+%E5%BF%97%E6%9C%9B%E5%8B%95%E6%A9%9F&hl=ja&gl=JP&ceid=JP:ja"),
    "102": ("ガクチカ 書き方", "https://news.google.com/rss/search?q=%E3%82%AC%E3%82%AF%E3%83%81%E3%82%AB+%E6%9B%B8%E3%81%8D%E6%96%B9+%E6%A7%8B%E6%88%90+PREP%E6%B3%95&hl=ja&gl=JP&ceid=JP:ja"),
    "103": ("伝わる文章 テクニック", "https://news.google.com/rss/search?q=%E4%BC%9D%E3%82%8F%E3%82%8B%E6%96%87%E7%AB%A0+%E3%83%86%E3%82%AF%E3%83%8B%E3%83%83%E3%82%AF+%E3%83%93%E3%82%B8%E3%83%8D%E3%82%B9&hl=ja&gl=JP&ceid=JP:ja"),
    "104": ("ロジカルライティング", "https://news.google.com/rss/search?q=%E3%83%AD%E3%82%B8%E3%82%AB%E3%83%AB%E3%83%A9%E3%82%A4%E3%83%86%E3%82%A3%E3%83%B3%E3%82%B0+%E5%B0%B1%E6%B4%BB&hl=ja&gl=JP&ceid=JP:ja"),
    "105": ("27卒 エンジニア 採用", "https://news.google.com/rss/search?q=27%E5%8D%92+%E3%82%A8%E3%83%B3%E3%82%B8%E3%83%8B%E3%82%A2+%E6%8E%A1%E7%94%A8+%E3%83%88%E3%83%AC%E3%83%B3%E3%83%89&hl=ja&gl=JP&ceid=JP:ja"),
}

# ... (Rest of sources implied)

# ...

def perform_serendipity_patrol(processed_ids, seen_titles):
    """
    【Serendipity Mode】
    定型的な情報が見つからない場合、AIが「未知の概念」や「意外な組み合わせ」を提案し、
    それを元に情報空間を探索するモード。
    """
    print("\n🔮 === SERENDIPITY MODE ACTIVATED (未知探索) ===")
    print("   既知のソースからの情報が枯渇しています。")
    print("   AIが「予期せぬ知的遭遇」を生成し、未知の領域をパトロールします...")
    
    if not llm:
        print("   [Error] AI unavailable for Serendipity Mode.")
        return []

    # 1. Generate Serendipity Seed
    prompt = """
    あなたは「知の探検家」です。
    通常のニュース探索では何も見つかりませんでした。
    ユーザー（27卒、エンジニア志望、哲学・社会構造に興味あり）のために、
    **「全く検索しようとも思わなかったが、知ると衝撃を受ける概念」**あるいは
    **「一見関係ないが、実は就活やキャリアに重大な示唆を与える歴史的事実/理学概念」**
    を1つ選定し、検索クエリを作成してください。

    例:
    - "サイバネティクス 経営管理 歴史"
    - "アクターネットワーク理論 ビジネス"
    - "エントロピー増大則 組織論"
    - "中世ギルド 現代エンジニア"

    出力は検索クエリ（日本語）のみにしてください。余計な文字は不要です。
    """
    try:
        seed_query = ask_llm(prompt).strip().replace('"', '')
        print(f"   🎲 Serendipity Seed: 『{seed_query}』")
        
        # 2. Search for this unknown concept
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(seed_query)}&hl=ja&gl=JP&ceid=JP:ja"
        items = get_rss_feed(url)
        
        # 3. Filter & Tag
        results = []
        for item in items:
            if item['link'] not in processed_ids and item['title'] not in seen_titles:
                item['source'] = f"Serendipity: {seed_query}"
                # Force High Priority analysis for these rare finds
                results.append(item)
        
        return results
        
    except Exception as e:
        print(f"   [Serendipity Fail] {e}")
        return []

def get_mynavi_data():
    """マイナビ2027からランキングとイベント情報を取得 (Direct Scrape)"""
    print(f"📡 [MyNavi] Scanning official site...", end="\r")
    items = []
    base_url = "https://job.mynavi.jp"
    
    # 1. Top Page for Rankings - Optimized
    try:
        url = "https://job.mynavi.jp/2027/"
        req = urllib.request.Request(url, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            
            # Find "Ranking" text and go up
            targets = soup.find_all(string=re.compile("ランキング"))
            seen = set()
            for t in targets:
                container = t.find_parent(['div', 'section', 'ul', 'dl'])
                if container:
                     links = container.find_all('a')
                     for a in links:
                         href = a.get('href', '')
                         if 'corpinfo' in href and href not in seen:
                             items.append({
                                 'title': f"[MyNavi Rank] {a.get_text(strip=True)}",
                                 'link': urllib.parse.urljoin(base_url, href),
                                 'summary': "マイナビ アクセスランキング掲載企業",
                                 'source': "MyNavi Ranking",
                                 'image_url': ""
                             })
                             seen.add(href)
                             if len(items) > 10: break
    except Exception as e:
        print(f"   [MyNavi Top Error] {e}")

    # 2. Event Page - Broadened
    try:
        url_evt = "https://job.mynavi.jp/conts/2027/event/index.html"
        req = urllib.request.Request(url_evt, headers={'User-Agent': get_random_user_agent()})
        with urllib.request.urlopen(req) as res:
            soup = BeautifulSoup(res.read(), 'html.parser')
            for a in soup.find_all('a'):
                txt = a.get_text(strip=True)
                href = a.get('href', '')
                if "event" in href and len(txt) > 8: 
                    items.append({
                            'title': f"[MyNavi Event] {txt}",
                            'link': urllib.parse.urljoin(base_url, href),
                            'summary': "マイナビ主催イベント情報",
                            'source': "MyNavi Event",
                            'image_url': ""
                        })
    except Exception as e:
         print(f"   [MyNavi Event Error] {e}")
         
    return items

def do_shukatsu_patrol():
    """就活パトロール実行"""
    print("\n" + "="*60)
    print("📋 === 就活インテリジェンスパトロール (Anti-Bot & Serendipity) ===")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    processed_ids = load_processed()
    all_items = []
    
    # 全ソースをスキャン
    # 全ソースをスキャン (Parallel Guard Risk-Hedge Mode)
    print("🛡️ Deploying Parallel Scouts (Risk-Hedge Mode)...")
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit all tasks
        future_to_source = {
            executor.submit(get_rss_feed, url): (key, name) 
            for key, (name, url) in SHUKATSU_SOURCES.items()
        }
        
        # Process as they complete (Robustness)
        for future in as_completed(future_to_source):
            key, name = future_to_source[future]
            try:
                # Timeout protection for individual feeds (Risk Hedge)
                items = future.result(timeout=15)
                if items:
                    print(f"   ✅ [{key}] {name}: {len(items)} items", end="\r")
                    for item in items:
                        if item['link'] not in processed_ids:
                            item['source'] = name
                            all_items.append(item)
            except Exception as e:
                # If one source dies, we just log it and CONTINUE.
                pass
    
    # === MyNavi Direct Integration ===
    try:
        mynavi_items = get_mynavi_data()
        all_items.extend(mynavi_items)
        if mynavi_items:
            print(f"   ✨ MyNavi: {len(mynavi_items)} items found.")
    except Exception as e:
        print(f"   [MyNavi Skip] {e}")

    # 重複排除
    seen_titles = set()
    unique_items = []
    for item in all_items:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_items.append(item)
    
    # Visual Processing for Items with Images
    print("\n👁️ Visual Cortex Scan...")
    for item in unique_items:
        if item.get('image_url'):
            try:
                # Basic temp download and process
                print(f"   Processing image for: {item['title'][:20]}...")
                tmp_img = os.path.join(SHUKATSU_DIR, f"temp_{int(time.time())}.jpg")
                urllib.request.urlretrieve(item['image_url'], tmp_img)
                ocr_text = image_to_markdown(tmp_img)
                if ocr_text:
                    item['summary'] += f"\n\n[Visual Cortex Analysis]\n{ocr_text}"
                if os.path.exists(tmp_img): os.remove(tmp_img)
            except Exception as e:
                print(f"   [Visual Fail] {e}")
    
    # アイテムが少ない場合はアクティブ検索で補強
    if len(unique_items) < 5:
        active_items = search_strategic_targets()
        for ai in active_items:
            if ai['link'] not in processed_ids and ai['title'] not in seen_titles:
                seen_titles.add(ai['title'])
                unique_items.append(ai)
    
    # ★★★ SERENDIPITY FALLBACK & AMPLIFICATION ★★★
    # 常に「未知探索」を発動して知見を広げる (Ambition Mode)
    print("\n🔮 Amplifying Serendipity (Ambition Mode)...")
    serendipity_items = perform_serendipity_patrol(processed_ids, seen_titles)
    unique_items.extend(serendipity_items)

    print(f"\n✅ スキャン完了: {len(unique_items)} 件の新規アイテム")
    
    if not unique_items:
        print("   （未知探索も含めて）新しい情報はありませんでした。")
        return 0
    
    # 最大50件を処理（並列化によりスループット向上）
    # 最大50件を処理（並列化によりスループット向上）

# ES難易度警告リスト（重いES・選考が厳しい企業）
ES_WARNING_COMPANIES = {
    "P&G": "⚠️ ES超難関：論理的思考力を問う設問が多い。早期準備必須。",
    "電通": "⚠️ ES難関：クリエイティブ性と自己分析の深さが求められる。",
    "博報堂": "⚠️ ES難関：独自の視点と表現力が重要。",
    "講談社": "⚠️ ES難関：出版への熱意と企画力を問われる。作文課題あり。",
    "集英社": "⚠️ ES難関：マンガへの造詣と企画力が必要。",
    "小学館": "⚠️ ES難関：幅広いジャンルへの理解が求められる。",
    "新潮社": "⚠️ 文学的素養と独自の視点が重視される。",
    "KADOKAWA": "⚠️ コンテンツへの理解と事業貢献のビジョンが必要。",
    "外資": "⚠️ 英語力・論理的思考・リーダーシップ経験が必須。",
    "国家公務員": "⚠️ 最難関：教養・専門試験の対策と、高い論理構成力が必須。",
    "省": "⚠️ 難関：各省庁の政策への深い理解と、国家への貢献意欲が問われる。",
}

# 重点リサーチ対象（企業 + 教養概念 + スキル）
STRATEGIC_TARGETS = [
    # Enterprises
    "P&G", "NTT", "デンソー", "ホンダ", "サイバーエージェント", 
    "トヨタ自動車", "KDDI", "ソニー", "キーエンス",
    "AGI Lab Prism", "AI LaTeX Editor Prism", "Overleaf Alternative AI", 
    "三菱商事", "三井物産", "伊藤忠商事", 
    "講談社", "集英社", "小学館", "KADOKAWA",
    "電通", "博報堂",
    
    # Liberal Arts & Concepts (Deep Dive Targets)
    "ポスト構造主義", "加速主義", "サイバネティクス",
    "認知科学", "ゲーム理論", "地政学 リスク",
    "生成AI 倫理", "トランスヒューマニズム",
    "量子コンピュータ 社会影響", "環境倫理学",
    "メディア論 (マクルーハン)", "資本主義の未来",
    "京都学派 西田幾多郎 テクノロジー", "オートポイエーシス システム論",
    "現象学 入門 エンジニア", "プラグマティズム 開発",

    # Practical Skills & Methods (How-To Deep Dive)
    "ロジカルシンキング フレームワーク", "フェルミ推定 対策",
    "ES通過 志望動機 構成", "グループディスカッション クラッシャー対策",
    "キャリアデザイン 20代", "エンジニア採用 ポートフォリオ",
    "KDDI ES 通過 例文", "ガクチカ 書き方 例文",
    "自己PR 書き方 エンジニア", "研究概要 書き方 文系"
]

# カレンダー保存先
CALENDAR_FILE = os.path.join(os.path.dirname(BASE_DIR), "../../data/precog_schedules.json")

# 処理済みログ
PROCESSED_FILE = os.path.join(SHUKATSU_DIR, "processed_shukatsu.json")

def load_processed():
    try:
        if os.path.exists(PROCESSED_FILE):
            with open(PROCESSED_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except: pass
    return set()

def save_processed(ids):
    try:
        with open(PROCESSED_FILE, "w", encoding="utf-8") as f:
            json.dump(list(ids)[-2000:], f)  # Keep more
    except: pass

# ===== AUTO-CATEGORIZATION ROUTER (Integrated from simulate_router.py) =====
CATEGORY_ROUTES = {
    "就活・ES関連": {
        "keywords": ["就活", "就職", "エントリーシート", "ES", "面接", "インターン", "企業", "志望動機", "自己PR", "マイページ", "採用", "27卒", "選考", "内定"],
        "priority": 10
    },
    "プログラミング・技術": {
        "keywords": ["コード", "プログラム", "python", "javascript", "バグ", "エラー", "開発", "GitHub", "エンジニア", "Tech", "SIer", "Java", "C++", "Rust", "AI", "機械学習"],
        "priority": 8
    },
    "ゲーム・エンタメ": {
        "keywords": ["ゲーム", "Unity", "Unreal", "任天堂", "ソニー", "RPG", "シミュレーション", "eスポーツ"],
        "priority": 7
    },
    "スケジュール": {
        "keywords": ["予定", "スケジュール", "カレンダー", "締切", "期限", "タスク", "TODO", "日程", "受付中"],
        "priority": 6
    },
    "リサーチ・教養": {
        "keywords": ["検索", "調査", "リサーチ", "調べる", "情報", "ニュース", "哲学", "思想", "歴史"],
        "priority": 5
    }
}

def classify_item(title: str, summary: str) -> str:
    """Classifies an item into a category based on keyword matching."""
    text = f"{title} {summary}".lower()
    scores = {}
    for category, info in CATEGORY_ROUTES.items():
        score = 0
        for kw in info["keywords"]:
            if kw.lower() in text:
                score += 1
        if score > 0:
            scores[category] = score + info["priority"] * 0.5
    
    if not scores:
        return "その他"
    return max(scores.items(), key=lambda x: x[1])[0]
# ========================================================================

def get_company_characteristics(company_name):
    """AIによる企業の『本質』深掘り調査"""
    if not llm: return "No LLM for profile analysis."
    
    prompt = f"""
あなたは百戦錬磨の就活メンターです。以下の企業の「表向きの顔」ではなく「本質的価値」と「27卒が狙うべき理由」を構造化してください。
企業名: {company_name}

以下の項目で要約して（計200文字程度）:
1. **主要武器**: 強みの源泉
2. **26-27卒への温度感**: 最近の採用傾向
3. **EGO適性**: 構造的思考やAI活用を好む文化か？
4. **裏の弱点**: 懸念されるリスク
"""
    try:
        return ask_llm(prompt)
    except:
        return "Analysis failed."

def get_random_user_agent():
    agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36'
    ]
    return random.choice(agents)

def get_rss_feed(url):
    """RSS/Atomフィードをパース (Anti-Bot Enhanced)"""
    max_retries = 3
    for attempt in range(max_retries):
        try:
            # Random Delay to behave like human
            time.sleep(random.uniform(1.5, 3.5))
            
            headers = {'User-Agent': get_random_user_agent()}
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=15) as response:
                xml_data = response.read()
            
            root = ET.fromstring(xml_data)
            items = []
            
            all_items = root.findall('.//item') + root.findall('.//{http://www.w3.org/2005/Atom}entry')
            
            for entry in all_items[:10]:
                t = entry.find('title')
                if t is None: t = entry.find('{http://www.w3.org/2005/Atom}title')
                title = t.text if t is not None else "No Title"
                
                l = entry.find('link')
                if l is None: l = entry.find('{http://www.w3.org/2005/Atom}link')
                link = l.text if l is not None and l.text else l.attrib.get('href', '') if l is not None else ""
                
                d = entry.find('description')
                if d is None: d = entry.find('{http://www.w3.org/2005/Atom}summary')
                if d is None: d = entry.find('{http://www.w3.org/2005/Atom}summary')
                desc = d.text if d is not None else ""
                
                # Image Extraction
                img_url = ""
                encl = entry.find('enclosure')
                if encl is not None and 'image' in encl.attrib.get('type', ''):
                    img_url = encl.attrib.get('url', '')
                elif encl is None:
                    # Try media:content
                    media = entry.find('{http://search.yahoo.com/mrss/}content')
                    if media is not None and 'image' in media.attrib.get('medium', ''):
                        img_url = media.attrib.get('url', '')

                items.append({'title': title, 'link': link, 'summary': desc or "", 'image_url': img_url})
            
            return items
            
        except urllib.error.HTTPError as e:
            if e.code == 429:
                print(f"   [429 Too Many Requests] Retrying in 5s... ({attempt+1}/{max_retries})")
                time.sleep(5)
            else:
                print(f"   [HTTP Error] {e.code}: {url[:30]}...")
                return []
        except Exception as e:
            # print(f"   [RSS Error] {e}") # Reduce noise
            return []
    return []

def load_user_context():
    """ユーザーの現在の関心事（コンテキスト）をロード"""
    context_file = os.path.abspath(os.path.join(BASE_DIR, "../../../data/user_context.json"))
    if not os.path.exists(context_file):
        return [], []
    try:
        with open(context_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('current_focus', []), data.get('priority_companies', [])
    except:
        return [], []

def search_strategic_targets():
    """重点対象企業のアクティブ・リサーチ実行"""
    print(f"📡 重点ターゲットの能動的リサーチを開始...")
    
    # Context Injection
    user_focus, user_companies = load_user_context()
    
    # Base targets + User Context
    active_targets = STRATEGIC_TARGETS.copy()
    if user_companies:
        print(f"   👤 User Priority Companies: {user_companies}")
        active_targets.extend(user_companies)
    
    # Pick a target (weighted slightly towards user context if available)
    if user_companies and random.random() < 0.4:
        target = random.choice(user_companies)
        print(f"   🔥 Context Hit! Focusing on: {target}")
    else:
        target = random.choice(active_targets)
    
    print(f"📡 【Active Research】Targeting: {target}...")
    
    # Combined search for News and PR
    queries = [
        f"{target} 採用 戦略 ニュース",
        f"{target} インターン 27卒",
        f"{target} プレスリリース 経営"
    ]
    
    # If user has specific focus topics, mix them in
    if user_focus:
        focus_topic = random.choice(user_focus)
        queries.append(f"{target} {focus_topic}")
        print(f"      running context query: {target} + {focus_topic}")
    
    all_active_items = []
    for q in queries:
        url = f"https://news.google.com/rss/search?q={urllib.parse.quote(q)}&hl=ja&gl=JP&ceid=JP:ja"
        all_active_items.extend(get_rss_feed(url))
        
    for item in all_active_items: item['source'] = f"Active:{target}"
    return all_active_items

def analyze_with_ai(title, content):
    """AIで就活関連性を分析"""
    if not llm:
        return {"relevance": "unknown", "summary": content[:100], "deadline": None, "company": None}
    
    # --- Feedback Loop Integration ---
    feedback_file = os.path.abspath(os.path.join(BASE_DIR, "../../../data/ai_feedback_loop.json"))
    active_instructions = ""
    if os.path.exists(feedback_file):
        try:
            with open(feedback_file, 'r', encoding='utf-8') as f:
                feedbacks = json.load(f)
                # Get the last 3 active high-priority instructions
                instructions = [f['instruction'] for f in feedbacks if f.get('status') == 'active'][:3]
                if instructions:
                    active_instructions = "\n【重要な修正指示・フィードバック】\n" + "\n".join([f"- {i}" for i in instructions])
        except: pass

    prompt = f"""あなたは27卒（2027年卒業者）向けの高度就活インテリジェンス・オフィサーです。
以下のニュースを**深層まで掘り下げて**分析し、戦略的なインテリジェンスを抽出してください。
{active_instructions}

タイトル: {title}
内容: {content[:1500]}

以下のJSON形式で回答してください。特に "swot" と "action_plan" は具体的に記述してください。
{{
    "relevance": "high/medium/low",
    "summary": "要約（50文字程度）",
    "strategic_analysis": {{
        "true_intent": "この情報の裏にある意図や、誰が得をするか（利権・宣伝色）を批判的に分析（150文字程度）",
        "swot": {{
            "strength": "この情報から見える企業の強み",
            "weakness": "この実態から推測される弱み・綻び",
            "opportunity": "就活生にとってのチャンス",
            "threat": "業界全体への脅威"
        }},
        "writing_technique": "もしこの情報がESや面接のテクニックに関するものであれば、具体的な『書き方の型』や『使えるフレーズ』を抽出してください。そうでなければ空欄で構いません。",
        "action_plan": "Yuto（ユーザー）が今すぐ、あるいは次の選考で取るべき具体的アクション。逆質問案や、OB訪問で確認すべき点など（150文字程度）"
    }},
    "bias_warning": "偏向報道やポジショントークの可能性を具体的に",
    "company": "企業名か null",
    "category": "出版/広告/メディア/IT/その他",
    "target_year": "2027",
    "priority_score": 1-10 (10が最高)
}}"""
    
    try:
        result = ask_llm(prompt)
        
        # JSONを抽出
        if "```json" in result:
            result = result.split("```json")[1].split("```")[0]
        elif "```" in result:
            result = result.split("```")[1].split("```")[0]
        
        # JSON部分を抽出
        import re
        start_idx = result.find('{')
        end_idx = result.rfind('}')
        if start_idx != -1 and end_idx != -1 and start_idx < end_idx:
            return json.loads(result[start_idx:end_idx+1])
        
        return json.loads(result.strip())
    except Exception as e:
        print(f"   [AI Parse Warn] {e}")
        return {"relevance": "medium", "summary": title[:50], "deadline": None, "company": None}

def analyze_academic_concept(title, summary, source):
    """
    教養・リベラルアーツ系トピックの「深掘り」を行う
    
    Args:
        title (str): ニュースタイトル
        summary (str): 要約
        source (str): 情報源
    
    Returns:
        dict: 深掘り分析結果 (Historical Context, Modern Relevance, Critical Perspective)
    """
    if "リベラルアーツ" not in source and "教養" not in source and "思想" not in source and "歴史" not in source and "科学技術" not in source:
        if "リベラルアーツ" not in title and "教養" not in title and "哲学" not in title and "思想" not in title:
           return None

    print(f"   🏛️ 教養・深掘り分析を実行中: {title[:20]}...")

    prompt = f"""
あなたはリベラルアーツの権威であり、世界を構造的に把握する哲学者です。
このトピックを単なるニュースとしてではなく、人類の知の系譜の中に位置づけてください。

トピック: {title}
内容: {summary[:800]}

以下の構成（Markdown）で、合計600文字程度で論じなさい:
1. **知の系譜 (Intellectual Genealogy)**: 過去の思想家（フッサール、フーコー、ハイデガー等）や歴史的事件との関連は？
2. **構造的分析 (Structural Significance)**: 現代の社会システムにおいて、なぜこの事象が「必然」として現れたのか？
3. **実存的武器 (Existential Weaponry)**: この知識を、自身のキャリアや面接、あるいは「世界との闘い」においてどう武器（概念装置）として使うべきか？

出力形式: Markdown
"""
    try:
        return ask_llm(prompt)
    except Exception as e:
        print(f"   [Academic Deep Dive Error] {e}")
        return None

def save_shukatsu_item(item, analysis):
    """就活アイテムを保存"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"SHUKATSU_{timestamp}.json"
    filepath = os.path.join(SHUKATSU_DIR, filename)
    
    data = {
        "title": item['title'],
        "link": item['link'],
        "raw_summary": item.get('summary', '')[:500],
        "ai_analysis": analysis,
        "critical_analysis": analysis.get("strategic_analysis", {}),
        "deep_strategic_dossier": analysis.get("deep_strategic_dossier", ""),
        "bias": analysis.get("bias_warning", ""),
        "collected_at": datetime.now().isoformat(),
        "source": item.get('source', 'unknown'),
        "score": analysis.get("priority_score", 5)
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return filename

def add_to_calendar(item, analysis):
    """締切がある場合はカレンダーに追加"""
    deadline = analysis.get('deadline')
    if not deadline:
        return
    
    try:
        calendar_path = os.path.abspath(os.path.join(BASE_DIR, "../../../data/precog_schedules.json"))
        os.makedirs(os.path.dirname(calendar_path), exist_ok=True)
        
        existing = []
        if os.path.exists(calendar_path):
            try:
                with open(calendar_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except: pass
        
        # 重複チェック
        for ex in existing:
            if ex.get('Event') == item['title'][:50]:
                return  # Already exists
        
        company = analysis.get('company', '不明')
        event_data = {
            "Date": deadline,
            "Time": "23:59",
            "Event": f"[就活] {company}: {item['title'][:40]}",
            "Type": "DEADLINE",
            "Priority": 10 if analysis.get('relevance') == 'high' else 5,
            "Status": "Pending",
            "Link": item.get('link', '')
        }
        
        existing.append(event_data)
        
        with open(calendar_path, 'w', encoding='utf-8') as f:
            json.dump(existing, f, indent=4, ensure_ascii=False)
        
        print(f"   📅 カレンダーに追加: {deadline}")
        
    except Exception as e:
        print(f"   [Calendar Error] {e}")

def check_es_warning(title, source):
    """ES難易度警告をチェック"""
    warnings = []
    for company, warning in ES_WARNING_COMPANIES.items():
        if company in title or company in source:
            warnings.append(warning)
    return warnings

def add_to_task_inbox(item, analysis, warnings):
    """
    問題・タスクを受信箱に追加（メールのように溜まる）
    これは「自己（Ego）」の成長記録にもなる
    """
    try:
        inbox_path = os.path.abspath(os.path.join(BASE_DIR, "../../../data/task_inbox.json"))
        os.makedirs(os.path.dirname(inbox_path), exist_ok=True)
        
        data = {"description": "", "inbox": []}
        if os.path.exists(inbox_path):
            try:
                with open(inbox_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            except: pass
        
        # 新しいタスクを作成
        task = {
            "id": datetime.now().strftime("%Y%m%d%H%M%S"),
            "type": "shukatsu",
            "title": item['title'][:60],
            "source": item.get('source', 'unknown'),
            "link": item.get('link', ''),
            "priority": analysis.get('relevance', 'medium'),
            "company": analysis.get('company'),
            "deadline": analysis.get('deadline'),
            "warnings": warnings,
            "ai_summary": analysis.get('summary', ''),
            "action_required": analysis.get('action_required', False),
            "status": "unread",  # unread / read / done
            "created_at": datetime.now().isoformat(),
            "self_note": ""  # ユーザーが後で書くメモ（自己成長用）
        }
        
        # 受信箱に追加
        if 'inbox' not in data:
            data['inbox'] = []
        data['inbox'].insert(0, task)  # 新しいものが上に
        
        # 最大100件まで保持
        data['inbox'] = data['inbox'][:100]
        
        with open(inbox_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"   📥 タスク受信箱に追加")
        
    except Exception as e:
        print(f"   [Inbox Error] {e}")

def generate_hyogo_summary():
    """兵庫県の採用情報を集計してサマリーを作成"""
    print("\n🗺️ 兵庫県・採用情報サマリーを作成中...")
    
    hyogo_items = []
    try:
        files = [f for f in os.listdir(SHUKATSU_DIR) if f.startswith("SHUKATSU_") and f.endswith(".json")]
        files.sort(reverse=True) # 最近のものから
        
        for f in files[:50]: # 直近50件をスキャン
            with open(os.path.join(SHUKATSU_DIR, f), "r", encoding="utf-8") as j:
                data = json.load(j)
                title = data.get('title', '')
                source = data.get('source', '')
                if "神戸" in title or "兵庫" in title or "神戸" in source or "兵庫" in source:
                    hyogo_items.append(data)
    except Exception as e:
        print(f"   [Summary Error] {e}")
        return

    if not hyogo_items:
        print("   該当するデータが見つかりませんでした。")
        return

    current_time_str = datetime.now().strftime('%Y/%m/%d %H:%M')
    summary_text = f"## 兵庫県 採用動向サマリー ({current_time_str})\n\n"
    for item in hyogo_items[:10]:
        analysis = item.get('ai_analysis', {})
        summary_text += f"- **{item['title'][:50]}**\n"
        summary_text += f"  - 企業: {analysis.get('company', '不明')}\n"
        summary_text += f"  - 要約: {analysis.get('summary', '情報なし')}\n"
        if analysis.get('deadline'):
            summary_text += f"  - ⚠️ 締切: {analysis['deadline']}\n"
        summary_text += f"  - [詳細]({item['link']})\n\n"

    # 保存
    summary_path = os.path.join(SHUKATSU_DIR, "HYOGO_RECRUIT_SUMMARY.md")
    with open(summary_path, "w", encoding="utf-8") as f:
        f.write(summary_text)
    
    # 知識ベース(Universe)にも重要情報として投げる
    try:
        from modules.ollama_smart_selector import ask_ollama
        brief_prompt = f"以下の兵庫県採用情報を100文字程度で総合的にまとめてください:\n{summary_text[:2000]}"
        brief = ask_llm(brief_prompt)
        
        # Universeに追加
        universe_path = os.path.abspath(os.path.join(BASE_DIR, "../../MEDIA/youtube_channel/data/universe.json"))
        if os.path.exists(universe_path):
            with open(universe_path, 'r', encoding='utf-8') as f:
                u_data = json.load(f)
            
            new_node = {
                "id": f"hyogo_shukatsu_{int(time.time())}",
                "title": f"兵庫県採用情報サマリー ({current_time_str})",
                "summary": brief,
                "group": "Shukatsu",
                "importance": 8,
                "timestamp": datetime.now().isoformat(),
                "metadata": {"type": "summary", "region": "Hyogo"}
            }
            u_data['nodes'].append(new_node)
            with open(universe_path, 'w', encoding='utf-8') as f:
                json.dump(u_data, f, indent=2, ensure_ascii=False)
            print("   🚀 Universeにサマリーを登録しました。")
    except: pass

    print(f"✅ サマリーを更新しました: {summary_path}")

def do_shukatsu_patrol():
    """就活パトロール実行"""
    print("\n" + "="*60)
    print("📋 === 就活インテリジェンスパトロール ===")
    print(f"   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    processed_ids = load_processed()
    all_items = []
    
    # 全ソースをスキャン
    for key, (name, url) in SHUKATSU_SOURCES.items():
        print(f"📡 [{key:>2}] {name}...", end="\r")
        items = get_rss_feed(url)
        
        for item in items:
            if item['link'] not in processed_ids:
                item['source'] = name
                all_items.append(item)
    
    # 重複排除
    seen_titles = set()
    unique_items = []
    for item in all_items:
        if item['title'] not in seen_titles:
            seen_titles.add(item['title'])
            unique_items.append(item)
    
    # アイテムが少ない場合はアクティブ検索で補強
    if len(unique_items) < 10:
        active_items = search_strategic_targets()
        for ai in active_items:
            if ai['link'] not in processed_ids and ai['title'] not in seen_titles:
                seen_titles.add(ai['title'])
                unique_items.append(ai)
    
    print(f"\n✅ スキャン完了: {len(unique_items)} 件の新規アイテム")
    
    if not unique_items:
        print("   新しい情報はありませんでした。")
        return 0
    
    # 最大50件を処理（並列化によりスループット向上）
    targets = unique_items[:50]
    
    print(f"\n🔍 AI分析開始 ({len(targets)}件) [Parallel Mode]...")
    
    def process_item(item):
        """1つのアイテムを分析・保存するスレッド関数"""
        try:
            # ES難易度警告チェック
            warnings = check_es_warning(item['title'], item.get('source', ''))
            
            # AI分析
            clean_summary = re.sub('<[^<]+?>', '', html.unescape(item.get('summary', '')))
            analysis = analyze_with_ai(item['title'], clean_summary)
            
            # 企業特性の深掘り調査
            company_name = analysis.get('company')
            if company_name and len(company_name) > 1 and company_name.lower() != "none":
                company_profile = get_company_characteristics(company_name)
                if company_profile:
                    analysis['company_profile'] = company_profile
                
                # 【New】High優先度の場合はさらにWebから深掘り
                if (analysis.get('relevance') == 'high' or analysis.get('priority_score', 0) >= 8) and deep_researcher:
                    print(f"      🚀 DEEP SCAN: Fetching Strategic IR/Plan for {company_name}...")
                    deep_dossier = deep_researcher.chained_strategic_research(company_name)
                    analysis['deep_strategic_dossier'] = deep_dossier
            
            # 教養・アカデミック深掘り
            academic_dive = analyze_academic_concept(item['title'], clean_summary, item.get('source', ''))
            if academic_dive:
                analysis['academic_deep_dive'] = academic_dive
            
            # 【NEW】UI/UX Analysis for High Relevance Items
            try:
                from apps.MEDIA.INTELLIGENCE_HUB.ui_analyzer import analyze_page_ui
                if analysis.get('relevance') == 'high' or analysis.get('priority_score', 0) >= 8:
                    print(f"      🎨 UI/UX Analysis: {item['title'][:20]}...")
                    ui_result = analyze_page_ui(item['link'])
                    if ui_result.get('status') != 'error':
                        analysis['ui_analysis'] = ui_result
            except Exception as e:
                print(f"      [UI Analysis Skip] {e}")

            # 保存
            filename = save_shukatsu_item(item, analysis)
            
            # 【NEW】スケジュール自動収集
            try:
                from apps.MEDIA.INTELLIGENCE_HUB.schedule_collector import collect_from_patrol_result
                patrol_data = {
                    'title': item['title'],
                    'link': item['link'],
                    'source': item.get('source', ''),
                    'ai_analysis': analysis
                }
                if collect_from_patrol_result(patrol_data):
                    print(f"      📅 Schedule Updated!")
            except Exception as e:
                pass  # サイレントフェイル
            
            # 高優先度または警告があればタスク受信箱に追加
            if analysis.get('relevance') == 'high' or warnings or analysis.get('action_required'):
                add_to_task_inbox(item, analysis, warnings)
                
            # 締切があればカレンダーに追加
            if analysis.get('deadline'):
                add_to_calendar(item, analysis)
                
            return f"   ✅ Done: {item['title'][:30]}"
        except Exception as e:
            return f"   ❌ Fail: {item['title'][:30]} ({e})"

    # スレッドプールで並列実行 (LLMのレート制限に注意しつつ5-10並列程度)
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(process_item, item) for item in targets]
        for future in as_completed(futures):
            print(future.result())
            # 処理済みに追加
            # (スレッドの戻り値等からリンクを取得して追加)
    
    # 全アイテムのリンクをProcessedに追加
    for item in targets:
        processed_ids.add(item['link'])
    
    save_processed(processed_ids)
    print(f"\n✅ 就活パトロール完了: {len(targets)}件を処理")
    
    # パトロール後に兵庫県サマリーを更新
    generate_hyogo_summary()
    
    return len(targets)


def check_command_queue():
    """コマンドキューを確認して優先タスクを取得"""
    queue_file = os.path.abspath(os.path.join(BASE_DIR, "../../../data/command_queue.json"))
    if not os.path.exists(queue_file):
        return None
    
    try:
        with open(queue_file, 'r', encoding='utf-8') as f:
            queue = json.load(f)
            
        if not queue:
            return None
            
        # 先頭のコマンドを取得 (Pendingのみ)
        cmd = None
        new_queue = []
        for c in queue:
            if c['status'] == 'pending' and not cmd:
                cmd = c
                c['status'] = 'processing' # ロック
            new_queue.append(c)
            
        # 更新
        with open(queue_file, 'w', encoding='utf-8') as f:
            json.dump(new_queue, f, indent=2, ensure_ascii=False)
            
        return cmd
    except Exception as e:
        print(f"   [Queue Error] {e}")
        return None

def perform_deep_dive_during_idle(forced_target=None):
    """アイドル時間に深掘り調査を実行"""
    print("\n🧐 === Deep Dive Mode (Idle Time Utilization) ===")
    
    if forced_target:
        print(f"🚀 COMMAND OVERRIDE: Prioritizing '{forced_target}'")
        target = forced_target
        # Active Search for specific target
        items = get_rss_feed(f"https://news.google.com/rss/search?q={urllib.parse.quote(target)}&hl=ja&gl=JP&ceid=JP:ja")
    else:
        target = random.choice(STRATEGIC_TARGETS)
        print(f"👉 Target: {target}")
        items = search_strategic_targets()
    
    # 2. 既存のprocessedと照合して新しいものがあれば分析
    processed_ids = load_processed()
    new_items = [i for i in items if i['link'] not in processed_ids]
    
    if new_items:
        print(f"   💡 Deep Diveで {len(new_items)} 件に新発見がありました。分析します。")
        for item in new_items[:3]: # 最大3つ
            print(f"   Analyzing: {item['title'][:20]}...")
            
            # コンテンツのクリーンアップ
            clean_summary = re.sub('<[^<]+?>', '', html.unescape(item.get('summary', '')))
            
            # 教養・概念ターゲットかどうか判定
            is_academic = any(concept in target for concept in ["思想", "哲学", "論", "主義", "史", "倫理", "科学", "社会"])
            
            analysis = analyze_with_ai(item['title'], clean_summary)
            
            # 教養ターゲットの場合はアカデミック分析を強制実行
            if is_academic:
                print(f"      🏛️ Applying Academic Lens for: {target}")
                academic_dive = analyze_academic_concept(item['title'], clean_summary, f"DeepDive:{target}")
                if academic_dive:
                    analysis['academic_deep_dive'] = academic_dive
                    # スコアを底上げ (教養は重要)
                    analysis['priority_score'] = max(analysis.get('priority_score', 0), 8)

            save_shukatsu_item(item, analysis)
            processed_ids.add(item['link'])
            
        save_processed(processed_ids)
    else:
        print(f"   🤔 {target} についての新しい表層情報はなし。思考を巡らせます...")
        time.sleep(2)

    print("✅ Deep Dive Completed.\n")

def start_auto_shukatsu():
    """自動パトロールループ (Overclock / Deep Search Mode)"""
    
    print("\n🔄 就活パトロール OVERCLOCK MODE 開始")
    print("   状態: Deep Loop Active (Wait -> Dive)")
    print("   Ctrl+C で停止\n")
    
    consecutive_empty_cycles = 0

    while True:
        try:
            # 0. Check Command Queue FIRST
            priority_cmd = check_command_queue()
            if priority_cmd:
                print(f"\n📨 COMMAND RECEIVED: {priority_cmd['action']} on {priority_cmd['args']}")
                if priority_cmd['action'] == 'deep_dive':
                    args = priority_cmd.get('args', {})
                    # Handle both old string args and new dict args
                    if isinstance(args, str):
                        query = args
                        search_type = "normal"
                    else:
                        query = args.get('query', 'Unknown')
                        search_type = args.get('type', 'normal')
                        
                    perform_deep_dive_during_idle(forced_target=query)
                    continue # Skip normal patrol loop to handle command

            count = do_shukatsu_patrol()
            if count is None: count = 0
            
            if count > 0:
                # 新しい情報が見つかった場合
                interval_min = 3
                consecutive_empty_cycles = 0
                print(f"🔥 {count}件の新着ヒット! {interval_min}分だけ休憩して次へ...")
                time.sleep(interval_min * 60)
            else:
                # 何も見つからなかった場合 -> Deep Dive実行
                consecutive_empty_cycles += 1
                
                print(f"💤 新着なし (連続: {consecutive_empty_cycles}回). Deep Diveを開始します...")
                
                # Deep Diveの実行
                perform_deep_dive_during_idle()
                
                # === TRIGGER TIER 2 AI (DEEP THINKER) ===
                # Now handled by separate daemon process (Core 4).
                # No direct invocation needed.
                # ========================================

                # 少し休む
                print("☕ ちょっと一息 (30秒)...")
                time.sleep(30)
        
        except KeyboardInterrupt:
            print("\n\n👋 就活パトロール終了")
            break
        except Exception as e:
            print(f"\n❌ エラー: {e}")
            time.sleep(60)  # 1分待って再試行

if __name__ == "__main__":
    if "--continuous" in sys.argv:
        start_auto_shukatsu()
    elif "--auto" in sys.argv:
        start_auto_shukatsu()
    else:
        do_shukatsu_patrol()
        print("\n💡 自動モードで実行するには: python shukatsu_patrol.py --auto")
