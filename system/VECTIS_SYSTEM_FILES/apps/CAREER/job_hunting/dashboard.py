"""
VECTIS - Job Hunt Dashboard
===========================
就活総合管理ダッシュボード

Features:
- 企業・選考管理
- ES進捗トラッキング
- 面接準備
- スケジュール管理
- AIレビュー統合（Unified LLM）
- Job HQ（ES Dojo）連携
- K-Cards知識データベース連携
- Personal Core自己分析統合
- Obsidian Vault自動保存
"""

import streamlit as st
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent.parent / "modules"))

try:
    from unified_llm import create_llm_client
    from obsidian_vault import quick_note
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False
    print("Warning: Unified LLM not available. AI features disabled.")

# Page config
st.set_page_config(
    page_title="就活ダッシュボード - VECTIS",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Professional & Clean
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    .stApp {
        background: transparent;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: bold;
    }
    .company-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .urgent {
        border-left-color: #ef4444 !important;
    }
    .in-progress {
        border-left-color: #f59e0b !important;
    }
    .completed {
        border-left-color: #10b981 !important;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .status-pending { background: #fef3c7; color: #92400e; }
    .status-progress { background: #dbeafe; color: #1e40af; }
    .status-done { background: #d1fae5; color: #065f46; }
    .status-rejected { background: #fee2e2; color: #991b1b; }
</style>
""", unsafe_allow_html=True)

# Data file paths
DATA_DIR = Path(__file__).parent
COMPANIES_FILE = DATA_DIR / "companies.json"
ES_FILE = DATA_DIR / "es_progress.json"

def load_data(filename):
    """データファイル読み込み"""
    if filename.exists():
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_data(filename, data):
    """データファイル保存"""
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_personal_core():
    """Personal Core読み込み"""
    core_file = DATA_DIR / "personal_core.md"
    if core_file.exists():
        with open(core_file, 'r', encoding='utf-8') as f:
            return f.read()
    return "Personal Coreファイルが見つかりません"

def load_kcards():
    """K-Cardsファイル読み込み"""
    kcards = []
    for kcard_file in DATA_DIR.glob("*.kcard"):
        try:
            with open(kcard_file, 'r', encoding='utf-8') as f:
                content = f.read()
                kcards.append({
                    "filename": kcard_file.name,
                    "content": content,
                    "size": len(content)
                })
        except:
            continue
    return kcards

def ai_review_es(es_text, company_name=""):
    """UnifiedLLMでES添削"""
    if not LLM_AVAILABLE:
        return "❌ AI機能が利用できません。Unified LLMが正しくインストールされているか確認してください。"
    
    try:
        llm = create_llm_client()
        
        prompt = f"""
以下のESを添削してください。企業名: {company_name}

【ES内容】
{es_text}

【添削観点】
1. 論理構成の明確さ
2. 具体性・エピソードの説得力
3. 企業とのマッチング
4. 文章の読みやすさ
5. 改善提案

具体的なアドバイスをお願いします。
"""
        
        response = llm.generate(prompt, temperature=0.7, max_tokens=1000)
        return response
    
    except Exception as e:
        return f"❌ AI添削エラー: {str(e)}"

def save_to_obsidian(title, content, tags=None):
    """Obsidian Vaultに保存"""
    try:
        if tags is None:
            tags = ["job-hunt"]
        path = quick_note(title, content, tags=tags)
        return True, str(path)
    except Exception as e:
        return False, str(e)

def match_with_core(content, content_type="ES"):
    """内容とPersonal Coreの親和性をAI診断"""
    if not LLM_AVAILABLE:
        return "❌ AI機能が利用できません。"
    
    personal_core = load_personal_core()
    
    try:
        llm = create_llm_client()
        prompt = f"""
【就活本質マッチング診断】
以下の「{content_type}」が、ユーザーの「Personal Core（核心）」とどの程度一致しているか分析してください。

---
【ユーザーのPersonal Core】
{personal_core}

---
【対象の{content_type}】
{content}
---

診断項目:
1. **本質的一致度 (0-100%)**:
2. **強みの活用状況**:
3. **乖離点・改善案**:
4. **面接でのキラーフレーズ提案**:

プロフェッショナルな就活アドバイザーの視点で、辛口かつ建設的に評価してください。
"""
        return llm.generate(prompt, temperature=0.7)
    except Exception as e:
        return f"❌ 診断エラー: {str(e)}"

def get_job_strategy(kcard_content):
    """K-Card（知識）を就活戦略に変換"""
    if not LLM_AVAILABLE:
        return "❌ AI機能が利用できません。"
    
    try:
        llm = create_llm_client()
        prompt = f"""
以下の知識を「出版業界・メディア業界の就活」でどう武器にするか、具体的な戦略を立ててください。

---
【知識内容（K-Card）】
{kcard_content}
---

戦略案:
1. **志望動機への組み込み方**:
2. **逆質問での活用例**:
3. **「面白い企画」への昇華案**:
4. **自己分析との紐付け**:

特に、情報の「編集」や「パッケージング」という観点を重視してください。
"""
        return llm.generate(prompt, temperature=0.8)
    except Exception as e:
        return f"❌ 戦略策定エラー: {str(e)}"

def main():
    st.title("💼 就活ダッシュボード")
    st.caption("VECTIS Job Hunt Management System")
    
    # Sidebar
    with st.sidebar:
        st.header("🎯 クイックアクション")
        
        if st.button("➕ 新規企業登録", use_container_width=True):
            st.session_state.show_add_company = True
        
        if st.button("📝 ES作成", use_container_width=True):
            st.session_state.show_add_es = True
        
        if st.button("🔄 データ更新", use_container_width=True):
            st.rerun()
        
        st.divider()
        
        st.header("📊 フィルター")
        status_filter = st.multiselect(
            "ステータス",
            ["選考中", "ES提出済", "面接予定", "内定", "不合格"],
            default=["選考中", "ES提出済", "面接予定"]
        )
        
        priority_filter = st.selectbox(
            "優先度",
            ["すべて", "高", "中", "低"]
        )
    
    # Load data
    companies = load_data(COMPANIES_FILE)
    es_data = load_data(ES_FILE)
    
    # Main content
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
        "📊 ダッシュボード", 
        "🏢 企業管理", 
        "📝 ES管理", 
        "📅 スケジュール",
        "🤖 AI添削",
        "🎯 Personal Core",
        "📚 K-Cards"
    ])
    
    with tab1:
        # KPI Metrics
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("総エントリー数", len(companies), "+3")
        
        with col2:
            in_progress = len([c for c in companies if c.get("status") == "選考中"])
            st.metric("選考中", in_progress)
        
        with col3:
            es_completed = len([e for e in es_data if e.get("completed")])
            st.metric("ES完成", f"{es_completed}/{len(es_data)}")
        
        with col4:
            # 今週の面接数
            st.metric("今週の予定", "2件")
        
        st.divider()
        
        # 締切が近い企業
        st.subheader("🔥 締切が近い企業")
        
        urgent_companies = sorted(
            [c for c in companies if c.get("deadline")],
            key=lambda x: x.get("deadline", "9999-12-31")
        )[:5]
        
        if urgent_companies:
            for company in urgent_companies:
                deadline = datetime.fromisoformat(company["deadline"])
                days_left = (deadline - datetime.now()).days
                
                urgency_class = "urgent" if days_left <= 3 else "in-progress" if days_left <= 7 else ""
                
                st.markdown(f"""
                <div class="company-card {urgency_class}">
                    <h3>{company['name']}</h3>
                    <p><strong>締切:</strong> {company['deadline']} <span style="color: {'red' if days_left <= 3 else 'orange'};">（残り{days_left}日）</span></p>
                    <p><strong>ステータス:</strong> <span class="status-badge status-progress">{company.get('status', '未設定')}</span></p>
                    <p>{company.get('notes', '')}</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("締切が設定されている企業はありません")
        
        st.divider()
        
        # 進捗状況
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("📈 選考ステージ分布")
            
            if companies:
                status_counts = {}
                for c in companies:
                    status = c.get("status", "未設定")
                    status_counts[status] = status_counts.get(status, 0) + 1
                
                import pandas as pd
                df = pd.DataFrame(list(status_counts.items()), columns=["ステータス", "件数"])
                st.bar_chart(df.set_index("ステータス"))
            else:
                st.info("データがありません")
        
        with col2:
            st.subheader("✅ 今週のタスク")
            st.markdown("- [ ] 講談社 ES最終確認")
            st.markdown("- [ ] テレビ朝日 面接準備")
            st.markdown("- [ ] リクルート OB訪問")
    
    with tab2:
        st.header("🏢 企業管理")
        
        # 新規企業登録
        if st.session_state.get("show_add_company"):
            with st.expander("➕ 新規企業登録", expanded=True):
                with st.form("add_company_form"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        company_name = st.text_input("企業名 *", placeholder="例: 株式会社○○")
                        industry = st.selectbox("業界", ["出版", "放送", "IT", "広告", "メーカー", "その他"])
                        position = st.text_input("職種", placeholder="例: 編集職")
                    
                    with col2:
                        deadline = st.date_input("締切日")
                        priority = st.select_slider("優先度", options=["低", "中", "高"], value="中")
                        status = st.selectbox("ステータス", ["未応募", "ES作成中", "ES提出済", "選考中", "面接予定", "内定", "不合格"])
                    
                    notes = st.text_area("メモ", placeholder="企業情報、選考フロー、OB訪問メモなど")
                    
                    submitted = st.form_submit_button("登録", use_container_width=True)
                    
                    if submitted and company_name:
                        new_company = {
                            "id": str(datetime.now().timestamp()),
                            "name": company_name,
                            "industry": industry,
                            "position": position,
                            "deadline": deadline.isoformat(),
                            "priority": priority,
                            "status": status,
                            "notes": notes,
                            "created_at": datetime.now().isoformat()
                        }
                        companies.append(new_company)
                        save_data(COMPANIES_FILE, companies)
                        st.success(f"✅ {company_name} を登録しました!")
                        st.session_state.show_add_company = False
                        st.rerun()
        
        # 企業一覧
        st.subheader("📋 登録企業一覧")
        
        if companies:
            # フィルタリング
            filtered = companies
            if status_filter:
                filtered = [c for c in filtered if c.get("status") in status_filter]
            if priority_filter != "すべて":
                filtered = [c for c in filtered if c.get("priority") == priority_filter]
            
            for i, company in enumerate(filtered):
                with st.expander(f"{'⭐' if company.get('priority')=='高' else ''} {company['name']} - {company.get('status', '未設定')}"):
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.write(f"**業界:** {company.get('industry', '-')}")
                        st.write(f"**職種:** {company.get('position', '-')}")
                        st.write(f"**締切:** {company.get('deadline', '-')}")
                    
                    with col2:
                        st.write(f"**優先度:** {company.get('priority', '-')}")
                        st.write(f"**ステータス:** {company.get('status', '-')}")
                    
                    with col3:
                        if st.button("🗑️ 削除", key=f"del_{i}"):
                            companies.remove(company)
                            save_data(COMPANIES_FILE, companies)
                            st.rerun()
                    
                    if company.get('notes'):
                        st.info(company['notes'])
        else:
            st.info("まだ企業が登録されていません。サイドバーから登録してください。")
    
    with tab3:
        st.header("📝 ES管理")
        
        # ES作成フォーム
        with st.expander("✍️ 新規ES作成"):
            with st.form("new_es_form"):
                col1, col2 = st.columns(2)
                
                with col1:
                    es_company = st.selectbox("企業", [c["name"] for c in companies] if companies else ["企業を登録してください"])
                    es_question = st.text_input("設問", placeholder="例: 志望動機を教えてください")
                
                with col2:
                    es_deadline = st.date_input("締切")
                    es_word_limit = st.number_input("文字数制限", min_value=100, max_value=2000, value=400)
                
                es_content = st.text_area("回答内容", height=200, placeholder="ESの内容を記入してください...")
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.form_submit_button("💾 保存", use_container_width=True):
                        # ES保存
                        new_es = {
                            "id": str(datetime.now().timestamp()),
                            "company": es_company,
                            "question": es_question,
                            "content": es_content,
                            "word_limit": es_word_limit,
                            "deadline": es_deadline.isoformat(),
                            "completed": False,
                            "created_at": datetime.now().isoformat()
                        }
                        es_data.append(new_es)
                        save_data(ES_FILE, es_data)
                        st.success("✅ ESを保存しました!")
                        st.rerun()
                
                with col2:
                    if st.form_submit_button("📝 Obsidian保存", use_container_width=True):
                        success, path = save_to_obsidian(
                            f"ES_{es_company}_{es_question[:20]}",
                            f"# {es_company} - {es_question}\n\n{es_content}",
                            tags=["es", "job-hunt"]
                        )
                        if success:
                            st.success(f"✅ Obsidianに保存しました: {path}")
                        else:
                            st.error(f"❌ 保存失敗: {path}")
            
            # AI Matching for new ES
            if es_content:
                if st.button("⚖️ 自己分析との一致度を診断", use_container_width=True):
                    with st.spinner("診断中..."):
                        diag = match_with_core(es_content, "ES (新規作成)")
                        st.subheader("⚖️ 本質マッチング診断結果")
                        st.markdown(diag)
        
        # ES一覧
        st.subheader("📋 作成済みES")
        if es_data:
            for i, es in enumerate(es_data):
                with st.expander(f"{'✅' if es.get('completed') else '⏳'} {es.get('company', '不明')} - {es.get('question', '')[:30]}..."):
                    st.write(f"**文字数:** {len(es.get('content', ''))} / {es.get('word_limit', 0)}")
                    st.write(f"**締切:** {es.get('deadline', '-')}")
                    st.text_area("内容", es.get('content', ''), height=150, key=f"es_view_{i}", disabled=True)
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("⚖️ 診断", key=f"diag_es_{i}"):
                            diag = match_with_core(es.get('content', ''), "ES (保存済み)")
                            st.info(diag)
                    with col2:
                        if st.button("🗑️ 削除", key=f"del_es_{i}"):
                            es_data.remove(es)
                            save_data(ES_FILE, es_data)
                            st.rerun()
        else:
            st.info("まだESが作成されていません")
    
    with tab4:
        st.header("📅 スケジュール")
        st.info("スケジュール機能は次のバージョンで実装予定です")
        
        # 簡易リマインダー
        st.subheader("🔔 今週の予定")
        upcoming = sorted([c for c in companies if c.get("deadline")], 
                         key=lambda x: x.get("deadline", "9999-12-31"))[:5]
        
        for company in upcoming:
            deadline = datetime.fromisoformat(company["deadline"])
            days_left = (deadline - datetime.now()).days
            
            if days_left <= 7:
                st.warning(f"⚠️ **{company['name']}** - 締切: {company['deadline']} ({days_left}日後)")
    
    with tab5:
        st.header("🤖 AI添削（Unified LLM）")
        
        if not LLM_AVAILABLE:
            st.error("❌ Unified LLMが利用できません。モジュールをインストールしてください。")
        else:
            st.info("✅ AI添削機能が利用可能です（Ollama/Gemini/Groq）")
            
            # ES選択
            if es_data:
                selected_es = st.selectbox(
                    "添削するESを選択",
                    es_data,
                    format_func=lambda x: f"{x.get('company', '不明')} - {x.get('question', '')[:40]}..."
                )
                
                st.text_area("ES内容", selected_es.get('content', ''), height=200, disabled=True)
                
                if st.button("🤖 AI添削を実行", use_container_width=True):
                    with st.spinner("AI添削中..."):
                        review = ai_review_es(
                            selected_es.get('content', ''),
                            selected_es.get('company', '')
                        )
                        
                        st.subheader("📝 添削結果")
                        st.markdown(review)
                        
                        # Obsidian保存
                        if st.button("💾 添削結果をObsidianに保存"):
                            success, path = save_to_obsidian(
                                f"AI添削_{selected_es.get('company')}_{datetime.now().strftime('%Y%m%d')}",
                                f"# AI添削結果\n\n## ES内容\n{selected_es.get('content')}\n\n## 添削\n{review}",
                                tags=["ai-review", "es"]
                            )
                            if success:
                                st.success(f"✅ 保存完了: {path}")
            else:
                st.warning("添削するESがありません。先にESを作成してください。")
    
    with tab6:
        st.header("🎯 Personal Core（自己分析）")
        
        personal_core = load_personal_core()
        st.markdown(personal_core)
        
        st.divider()
        
        st.subheader("💡 ESへの活用")
        st.info("""
        **Personal Coreの使い方:**
        1. 「核心となる本質」を全ESで一貫
        2. 「武器となるコピー」を適宜引用
        3. 企業ごとに表現をカスタマイズ
        """)
        
        # Personal Coreからキーフレーズ抽出
        if st.button("✨ AIでキーフレーズ抽出", use_container_width=True):
            if LLM_AVAILABLE:
                with st.spinner("抽出中..."):
                    llm = create_llm_client()
                    prompt = f"""
以下の自己分析から、ESや面接で使える強力なキーフレーズを5つ抽出してください。

{personal_core}

各フレーズは1-2文程度で、インパクトがあるものを。
"""
                    result = llm.generate(prompt, temperature=0.8)
                    st.markdown(result)
            else:
                st.error("AI機能が利用できません")
    
    with tab7:
        st.header("📚 K-Cards（知識データベース）")
        
        kcards = load_kcards()
        st.info(f"**登録K-Cards数:** {len(kcards)}件")
        
        # 検索
        search_query = st.text_input("🔍 K-Cards検索", placeholder="キーワードを入力...")
        
        if search_query:
            filtered_kcards = [k for k in kcards if search_query.lower() in k["content"].lower()]
            st.write(f"**検索結果:** {len(filtered_kcards)}件")
        else:
            filtered_kcards = kcards
        
        # K-Cards表示
        for i, kcard in enumerate(filtered_kcards[:10]):  # 最初の10件
            with st.expander(f"📄 {kcard['filename']} ({kcard['size']}bytes)"):
                st.text_area("内容", kcard['content'], height=200, key=f"kcard_{i}", disabled=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("📝 ESに活用", key=f"use_kcard_{i}"):
                        st.info("この知識をESに統合してください")
                with col2:
                    if st.button("⚔️ 就活戦略に変換", key=f"strat_kcard_{i}"):
                        with st.spinner("戦略策定中..."):
                            strat = get_job_strategy(kcard['content'])
                            st.subheader(f"⚔️ {kcard['filename']} の就活活用戦略")
                            st.markdown(strat)
        
        if len(filtered_kcards) > 10:
            st.info(f"他{len(filtered_kcards) - 10}件のK-Cardsがあります")

if __name__ == "__main__":
    # Initialize session state
    if "show_add_company" not in st.session_state:
        st.session_state.show_add_company = False
    if "show_add_es" not in st.session_state:
        st.session_state.show_add_es = False
    
    main()
