from python_scripts.paper_intel.arxiv_fetcher import ArxivFetcher
import json

def fetch_interesting_papers():
    fetcher = ArxivFetcher()
    queries = [
        "Autonomous Shipping Ship AI",
        "Railway Maintenance Deep Learning",
        "Rust Language Safety Control Systems"
    ]
    
    all_results = []
    print("=== Fetching Open Papers for Yuto's Career Strategy ===")
    
    for q in queries:
        print(f"[*] Searching for: {q}")
        results = fetcher.search(q, limit=1)
        if results:
            all_results.append(results[0])
            print(f"    Found: {results[0]['title']}")
        else:
            print(f"    No recent papers found for {q}")

    # 結果をJSONで一時保存
    with open("logs/fetched_papers_temp.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=4, ensure_ascii=False)
    
    return all_results

if __name__ == "__main__":
    fetch_interesting_papers()
