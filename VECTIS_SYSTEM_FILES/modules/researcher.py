import time
import urllib.request
import urllib.parse
import json
import os
import sys

# Setup path for modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from groq import Groq
try:
    from ddgs.ddgs import DDGS
except ImportError:
    DDGS = None

from modules.gemini_client import GenerativeModel

class ResearchAgent:
    def __init__(self, gemini_api_key=None, groq_api_key=None):
        # Initialize using unified client
        self.gemini_model = GenerativeModel('gemini-pro')
        
        self.groq_client = None
        if groq_api_key:
            self.groq_client = Groq(api_key=groq_api_key)

    def _call_llm(self, prompt):
        """Helper to decide between Groq and Gemini for text tasks."""
        from modules.api_tracker import APITracker
        
        if self.groq_client:
            try:
                APITracker().increment("Groq")
                chat_completion = self.groq_client.chat.completions.create(
                    messages=[{"role": "user", "content": prompt}],
                    model="llama-3.3-70b-versatile",
                )
                return chat_completion.choices[0].message.content
            except Exception as e:
                print(f"Groq failed, falling back to Gemini: {e}")
        
        APITracker().increment("Gemini (Text)")
        response = self.gemini_model.generate_content(prompt)
        return response.text.strip()

    def summarize_results(self, topics, data):
        prompt = f"REQ:{topics}\nDATA:{data}\nTASK:Extract key pts. Structured summary. Gap analysis. MINIMAL TEXT."
        return self._call_llm(prompt)

    def generate_search_queries(self, user_request):
        prompt = f"REQ:{user_request}\nGEN:3-5 Google search queries. LIST ONLY."
        return self._call_llm(prompt)

    def fetch_url(self, url):
        """Abe-style: Std lib with User-Agent to avoid 403s. Enhanced for cleaner text."""
        import urllib.request
        from bs4 import BeautifulSoup
        try:
            req = urllib.request.Request(
                url, 
                data=None, 
                headers={
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
                }
            )
            with urllib.request.urlopen(req, timeout=15) as response:
                html_content = response.read().decode('utf-8', errors='ignore')
                
                # Use BeautifulSoup to extract meaningful text only
                soup = BeautifulSoup(html_content, 'html.parser')
                
                # Remove scripted elements
                for script in soup(["script", "style", "nav", "footer", "header"]):
                    script.decompose()
                
                text = soup.get_text(separator='\n')
                lines = [line.strip() for line in text.splitlines() if line.strip()]
                return "\n".join(lines)[:10000]
        except Exception as e:
            return f"FETCH_ERR:{e}"

    def generate_steps(self, instructions):
        prompt = f"REQ:{instructions}\nTASK:Break down into 3-5 minimalist actionable steps (e.g., RESEARCH topic, BROWSE url, LOG status).\nFORMAT:Step 1: ...\nStep 2: ..."
        return self._call_llm(prompt)
    def save_summary_to_file(self, content, filename=None):
        """Vectis: Export with LLM-generated summary filename + timestamp."""
        import datetime
        import re
        
        if filename is None:
            # 1. Ask LLM for a filename summary
            try:
                # Use a small prompt to get a concise title
                prompt = f"""
                TASK: Summarize the following text into a filename-safe string.
                - Max 15 chars.
                - Japanese or English ok.
                - No spaces, use underscores.
                - No extension.
                - CONTENT: {content[:500]}
                RETURN ONLY THE STRING.
                """
                title_candidate = self._call_llm(prompt).strip()
                title_candidate = title_candidate.replace("`", "").replace(".txt", "")
            except:
                title_candidate = "Summary"

            # 2. Sanitize for filename (remove invalid chars)
            safe_title = re.sub(r'[\\/*?:"<>|]', "", title_candidate) 
            safe_title = safe_title.replace(" ", "_").replace("　", "_").replace("\n", "")
            safe_title = safe_title[:30] # Limit length
            
            # 3. Add timestamp
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
            filename = os.path.join("outputs", "summaries", f"{safe_title}_{timestamp}.txt")
        
        # Ensure directory exists if it's a path
        dir_name = os.path.dirname(filename)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name)
            
        try:
            with open(filename, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"Exported to: {filename}")
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
    def generate_card_data(self, topic, content):
        """Standardize research into a .kcard JSON structure."""
        prompt = f"""
        TASK: Convert this research into a Game-Card format (JSON).
        TOPIC: {topic}
        CONTENT: {content}
        
        FORMAT:
        {{
            "title": "Topic name",
            "genre": "One of [Tech, News, Shogi, Career, Task, Other]",
            "rarity": "One of [Common, Uncommon, Rare, Epic, Legendary]",
            "content": "A flavor-text style summary (max 200 chars)",
            "source": "Summary of sources",
            "visual_seed": "A short image prompt for a card illustration"
        }}
        RETURN ONLY RAW JSON.
        """
        import json
        import re
        res_raw = self._call_llm(prompt)
        try:
            # Robust JSON extraction using regex
            json_match = re.search(r'\{.*\}', res_raw, re.DOTALL)
            if json_match:
                clean_json = json_match.group(0)
                data = json.loads(clean_json)
                import datetime
                data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                return data
            else:
                print(f"No JSON found in LLM response: {res_raw[:100]}")
                return None
        except Exception as e:
            print(f"Card JSON Parse Error: {e}\nRaw: {res_raw[:200]}")
            return None

    def extract_info(self, content, query):
        """Extract specific information from raw content based on a user query."""
        prompt = f"""
        TASK: Extract information from the provided text based on the user's request.
        REQUEST: {query}
        CONTENT: {content[:10000]} (Truncated if too long)
        
        OUTPUT FORMAT:
        - If asking for a list, provide a bulleted list.
        - If asking for a specific value, provide just that value.
        - Be concise and direct.
        """
        return self._call_llm(prompt)

    def search_web(self, query, max_results=3, region="jp-jp"):
        """Perform a real web search using DuckDuckGo."""
        from modules.api_tracker import APITracker
        APITracker().increment("DuckDuckGo")
        
        if not DDGS:
            return [{"title": "Error", "href": "", "body": "duckduckgo-search not installed."}]
        
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, region=region, max_results=max_results):
                    results.append(r)
        except Exception as e:
            print(f"Search failed: {e}")
            return []
        return results

    def chained_strategic_research(self, company_name):
        """
        [DEEP SCAN] Chained discovery: News -> IR -> Mid-term Plan -> Strategic Analysis
        """
        print(f"🔍 [DEEP SCAN] Initiating strategic chain for: {company_name}")
        
        queries = [
            f"{company_name} 投資家情報 IR 最新 資料",
            f"{company_name} 中期経営計画 戦略 2027",
            f"{company_name} 事業報告書 最新 アニュアルレポート"
        ]
        
        deep_intel = []
        
        for q in queries:
            results = self.search_web(q, max_results=2)
            for res in results:
                url = res.get('href')
                title = res.get('title')
                print(f"   ∟ Processing Link: {title}")
                
                # Tag as PDF if likely
                is_pdf = url.lower().endswith('.pdf') or "pdf" in title.lower()
                
                content = self.fetch_url(url)
                deep_intel.append({
                    "title": title,
                    "url": url,
                    "type": "IR/Plan" if not is_pdf else "PDF Document",
                    "snippet": content[:1500] # Representative chunk
                })
                
        # Consolidate into high-density strategic dossier
        context = json.dumps(deep_intel, ensure_ascii=False)
        prompt = f"""
あなたはVECTIS戦略分析局のトップです。
提供された企業（{company_name}）の公式ドキュメント（IR/中期経営計画等）から、
「27卒の就活生」が知るべき、企業の公式な「表向きの顔」と、そこから読み取れる「真の課題」を浮き彫りにしてください。

【対象】{company_name}
【ドキュメント提供】{context}

以下のフォーマット（Markdown）で報告せよ:
### 🏢 企業戦略の深層: {company_name}

#### 1. 公式ビジョン (Public Narrative)
- ドキュメントが強調している主要キーワードと将来像。

#### 2. アキレス腱 (Hidden Weakness)
- 計画や数字から読み取れる、企業が今最も恐れているリスクや課題。

#### 3. 27卒への実質的期待 (True Expectations for 2027 Grad)
- どの部署、どの能力が「喉から手が出るほど欲しい」のか。

#### 4. 面接で刺さる「鋭い一撃」 (Strategic Question)
- 凡百の学生が決して聞かない、経営計画の核心を突く逆質問案。
"""
        return self._call_llm(prompt)

# Alias for compatibility with Dashboard
Researcher = ResearchAgent
