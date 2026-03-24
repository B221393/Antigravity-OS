import os
import json
import sys
import time
from pathlib import Path
from datetime import datetime

# Setup Path
BASE_DIR = Path(__file__).resolve().parents[2]
import sys
sys.path.append(str(BASE_DIR))
sys.path.append(str(BASE_DIR / "VECTIS_SYSTEM_FILES"))

try:
    import vectis_core
    from modules.researcher import ResearchAgent
    from dotenv import load_dotenv
    load_dotenv(str(BASE_DIR / "VECTIS_SYSTEM_FILES" / ".env"))
    researcher = ResearchAgent(os.getenv("GEMINI_API_KEY"), os.getenv("GROQ_API_KEY"))
except Exception as e:
    print(f"Init Error: {e}")
    sys.exit(1)

def run_neural_compression():
    """
    VECTIS NEURAL CONDENSER:
    1. Scan all .kcard and .synapse files.
    2. Group by Semantic Hash (Rust-powered).
    3. If multiple items have the same hash, COMPRESS into a single 'Neural Seed'.
    4. Physically compress old/large content using Gzip.
    """
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 🧬 NEURAL COMPRESSION: INITIALIZING")
    
    knowledge_dir = BASE_DIR / "VECTIS_SYSTEM_FILES" / "apps" / "job_hunting" / "scanned"
    files = list(knowledge_dir.glob("*.kcard")) + list(knowledge_dir.glob("*.synapse"))
    
    hash_map = {}
    
    print(f"🔍 Analyzing {len(files)} information nodes...")
    
    for f in files:
        try:
            with open(f, "r", encoding="utf-8") as fin:
                data = json.load(fin)
                content = data.get("content", "")
                # Rust Semantic Hash
                s_hash = vectis_core.generate_semantic_hash(content)
                
                if s_hash not in hash_map:
                    hash_map[s_hash] = []
                hash_map[s_hash].append((f, data))
        except: continue

    compressed_count = 0
    
    for s_hash, items in hash_map.items():
        if len(items) > 1:
            print(f"📂 Found Redundancy Group [{s_hash[:8]}] - {len(items)} items")
            
            # Semantic Merge
            titles = [it[1].get("title") for it in items]
            combined_content = "\n---\n".join([it[1].get("content") for it in items])
            
            merge_prompt = f"""
            以下は内容が重複している複数の知識ノードです。
            これらを「VECTIS Neural Seed」として、元の意味を失わずに最小の文字数（独自の圧縮形式）で1つの高度な要約にまとめてください。
            
            タイトル一覧: {titles}
            内容:
            {combined_content}
            
            出力形式:
            - Title: 代表的なタイトル
            - Seed: 圧縮されたニューラル・シード（非常に高密度な要ary）
            """
            
            try:
                merged_text = researcher._call_llm(merge_prompt)
                
                # Save the new seed
                seed_id = f"neural_seed_{s_hash[:10]}"
                with open(knowledge_dir / f"{seed_id}.kcard", "w", encoding="utf-8") as fout:
                    json.dump({
                        "title": f"🧬 Neural Seed: {items[0][1].get('title')}",
                        "genre": "NeuralCompressed",
                        "rarity": "Mythic",
                        "content": merged_text,
                        "hashes_merged": [s_hash],
                        "source": "VECTIS NEURAL CONDENSER",
                        "created_at": datetime.now().isoformat()
                    }, fout, indent=2, ensure_ascii=False)
                
                # Delete original redundants
                for f_path, _ in items:
                    f_path.unlink()
                
                compressed_count += len(items) - 1
            except: pass
            
    # Physical Compression for large files
    for f in list(knowledge_dir.glob("*.kcard")):
        if f.stat().st_size > 5000: # Over 5KB
            print(f"💾 Physical Compression applied to: {f.name}")
            with open(f, "r", encoding="utf-8") as fin:
                raw = fin.read()
                compressed_blob = vectis_core.compress_data(raw)
            
            # Save as binary file .vcc (Vectis Compressed Core)
            with open(f.with_suffix(".vcc"), "wb") as fbin:
                fbin.write(compressed_blob)
            f.unlink()
            compressed_count += 1

    print(f"✨ COMPRESSION COMPLETE: {compressed_count} operations performed.")

if __name__ == "__main__":
    run_neural_compression()
