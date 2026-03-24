
import sys
import os

# Add modules to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "VECTIS_SYSTEM_FILES")))

from modules.researcher import ResearchAgent
from modules.unified_llm_client import GEMINI_API_KEY, GROQ_API_KEY

def main():
    print("🚀 Starting Deep Strategic Research...")
    
    agent = ResearchAgent(gemini_api_key=GEMINI_API_KEY, groq_api_key=GROQ_API_KEY)
    
    targets = ["株式会社SHIFT", "株式会社メイテック"]
    
    full_report = "# Strategic Analysis Report: SHIFT & Meitec\n\n"
    
    for target in targets:
        print(f"\nScanning {target}...")
        try:
            report = agent.chained_strategic_research(target)
            full_report += report + "\n\n---\n\n"
            
            # Save individual report
            safe_name = target.replace("株式会社", "")
            agent.save_summary_to_file(report, filename=f"VECTIS_SYSTEM_FILES/data/companies/{safe_name}_Strategic_analysis.md")
            
        except Exception as e:
            print(f"Error scanning {target}: {e}")
            full_report += f"## Error for {target}\n{e}\n\n"

    # Save combined
    with open("VECTIS_SYSTEM_FILES/data/companies/DEEP_STRATEGIC_REPORT.md", "w", encoding="utf-8") as f:
        f.write(full_report)
        
    print("\n✅ Deep Research Complete. Output saved to VECTIS_SYSTEM_FILES/data/companies/")

if __name__ == "__main__":
    main()
