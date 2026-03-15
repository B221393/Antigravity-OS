import os
import sqlite3
import numpy as np
import google.generativeai as genai
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# .envの読み込み
BASE_DIR = Path(__file__).parent.parent.parent
load_dotenv(BASE_DIR / "_config" / ".env")

# パスの設定
RESEARCH_DIR = BASE_DIR / "VECTIS_SYSTEM_FILES" / "KNOWLEDGE" / "RESEARCH"
INTEL_LOG_PATH = BASE_DIR / "VECTIS_SYSTEM_FILES" / "CAREER" / "STRATEGIC_INTEL_LOG.md"
DB_PATH = BASE_DIR / "_media" / "papers" / "vectis_knowledge.db"

class KnowledgeIndexer:
    """Gemini Embedding 2 Preview を活用したナレッジ・インデクサー"""

    def __init__(self, model_name: str = "models/gemini-embedding-2-preview"):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY not found in .env")
        
        genai.configure(api_key=api_key)
        self.model_name = model_name
        self._init_db()

    def _init_db(self):
        """SQLiteデータベースの初期化"""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_path TEXT UNIQUE,
                title TEXT,
                content TEXT,
                embedding BLOB,
                date_added TEXT
            )
        """)
        conn.commit()
        conn.close()

    def get_embedding(self, text: str) -> np.ndarray:
        """テキストをベクトル化する"""
        result = genai.embed_content(
            model=self.model_name,
            content=text,
            task_type="retrieval_document",
            title="VECTIS Knowledge Node"
        )
        return np.array(result['embedding'], dtype=np.float32)

    def index_file(self, file_path: Path):
        """個別のファイルをインデックスに登録する"""
        if not file_path.exists():
            return
            
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            
        # タイトルの抽出（簡易版：ファイル名から取得）
        title = file_path.stem
        
        # 埋め込みの生成
        embedding = self.get_embedding(content[:8192]) # モデルの制限に合わせて
        embedding_blob = embedding.tobytes()
        
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO knowledge (source_path, title, content, embedding, date_added)
            VALUES (?, ?, ?, ?, ?)
        """, (str(file_path), title, content, embedding_blob, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        print(f"Indexed: {title}")

    def index_all_research(self):
        """RESEARCHディレクトリ内の全論文をインデックス化"""
        for file in RESEARCH_DIR.glob("*.md"):
            self.index_file(file)
            
    def index_intel_log(self):
        """戦略的知性ログをインデックス化"""
        self.index_file(INTEL_LOG_PATH)

if __name__ == "__main__":
    indexer = KnowledgeIndexer()
    print("Indexing VECTIS Research Knowledge...")
    indexer.index_all_research()
    print("Indexing Strategic Intel Log...")
    indexer.index_intel_log()
    print("Indexing Complete.")
