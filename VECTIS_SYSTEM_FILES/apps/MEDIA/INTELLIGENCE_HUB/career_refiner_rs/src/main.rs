use chrono::Local;
use dotenvy::dotenv;
use glob::glob;
use serde::{Deserialize, Serialize};
use serde_json::json;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

#[derive(Debug, Deserialize, Serialize)]
struct Intelligence {
    title: String,
    collected_at: String,
    ai_analysis: Option<AiAnalysis>,
}

#[derive(Debug, Deserialize, Serialize)]
struct AiAnalysis {
    company: Option<String>,
    summary: Option<String>,
    strategic_analysis: Option<StrategicAnalysis>,
}

#[derive(Debug, Deserialize, Serialize)]
struct StrategicAnalysis {
    action_plan: Option<String>,
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    dotenv().ok();
    println!("🚀 EGO Career Refiner (Rust Edition) Initializing...");

    // Setup paths
    let base_dir = env::current_dir()?;
    let career_dir = base_dir.join("../../../CAREER");
    let shukatsu_data_dir = base_dir.join("data/shukatsu");
    let refined_dir = career_dir.join("REFINED_OUTPUTS");
    fs::create_dir_all(&refined_dir)?;

    // Scan ES files
    let pattern = format!("{}/*.md", career_dir.to_string_lossy());
    let es_files: Vec<PathBuf> = glob(&pattern)?
        .filter_map(Result::ok)
        .filter(|p| {
            let filename = p.file_name().unwrap_or_default().to_string_lossy();
            !["ES_COMPLETE_TEMPLATES.md", "ES_WRITING_GUIDE.md", "GAKUCHIKA_EQUESTRIAN_SA.md"]
                .contains(&filename.as_ref())
        })
        .collect();

    if es_files.is_empty() {
        println!("ℹ️ No ES drafts found to refine.");
        return Ok(());
    }

    for es_file in es_files {
        refine_es(&es_file, &shukatsu_data_dir, &refined_dir).await?;
    }

    Ok(())
}

async fn refine_es(
    file_path: &Path,
    intel_dir: &Path,
    output_dir: &Path,
) -> Result<(), Box<dyn std::error::Error>> {
    let filename = file_path.file_name().unwrap().to_string_lossy();
    println!("🔍 Refining: {}", filename);

    let original_content = fs::read_to_string(file_path)?;

    // Extract target company
    let targets = vec!["KDDI", "トヨタ", "ソニー", "電通", "博報堂", "講談社", "集英社", "P&G"];
    let target_company = targets.iter().find(|&&t| {
        original_content.contains(t) || filename.contains(t)
    });

    let mut intel_context = String::new();
    if let Some(company) = target_company {
        println!("   🏢 Detected Target: {}", company);
        let intel_list = load_latest_intelligence(company, intel_dir)?;
        if !intel_list.is_empty() {
            intel_context.push_str("\n### 関連する最新インテリジェンス:\n");
            for intel in intel_list {
                if let Some(analysis) = intel.ai_analysis {
                    intel_context.push_str(&format!("- **{}**\n", intel.title));
                    if let Some(summary) = analysis.summary {
                        intel_context.push_str(&format!("  - 分析: {}\n", summary));
                    }
                    if let Some(sa) = analysis.strategic_analysis {
                        if let Some(plan) = sa.action_plan {
                            intel_context.push_str(&format!("  - 推奨アクション: {}\n", plan));
                        }
                    }
                }
            }
        }
    } else {
        println!("   ⚠️ Target company not detected. Performing general refinement.");
    }

    let prompt = format!(
        r#"
あなたは伝説的なキャリアアドバイザー兼、戦略的就活ハッカーです。
以下のES下書きを、最新のインテリジェンス（あれば）を考慮して洗練（Refine）してください。

【ユーザーの核心的強み・世界観（不変）】
- **AIネイティブ時代の指揮官（Director）**: 単なる実装者ではなく、未完成なAIを統率するマネジメント能力。
- **重力への反逆（AntiGravity）**: 既存の非効率や「重い」システム、予定調和な回答を嫌い、本質的な価値（ What/Why ）にコミットする姿勢。
- **馬術SA級という直感**: 言葉が通じない「カオス」と対話し、信頼関係という「秩序」を導き出す観察眼。馬を「新人エンジニア」や「予測不能なエージェント」として捉える比喩。

【ユーザーの独自の語り口 (Voice Patterns)】
- ゲームやシステム設計の比喩を用いる（βテスト、バグ、ログインボーナス、パズル力、実装者vs意思決定者）。
- 「〜と考えています」といった弱気な結びを避け、「〜と確信しています」「〜にフルコミットします」「〜を先取りします」といった指揮官らしい断定を用いる。
- AI用語（コンテキスト、フォールバック）を、自身の哲学の一部として自然に織り交ぜる。

【変換例（Before/After）】
- **Before (AI-ish)**: 「貴社の技術力に惹かれ、自分の強みを活かして貢献したいと考えています。」
- **After (User-like)**: 「汎用化する技術を『ログインボーナス』として享受するのではなく、それを操る『指揮官』としての価値を貴社で証明したいと確信しています。」
- **Before (AI-ish)**: 「馬術部での経験を通じて、粘り強さを身につけました。」
- **After (User-like)**: 「言葉の通じない馬という『予測不能なエージェント』との対話を通じて、混沌から秩序を導き出す観察眼（SA級）を研ぎ澄ませてきました。」

【現在のES下書き】
---
{}
---

{}

【指示】
1. **徹底した脱・AI構文**: 「〜に惹かれました」「〜に魅力を感じました」「〜に貢献したい」といったテンプレート表現は禁止です。代わりに、ユーザーのManifestoにあるような「指揮官」「重力への反逆」「未完成な技術へのコミット」という文脈で語ってください。
2. **指揮官の視点**: 技術を単なる「手段」ではなく、マネジメント対象として捉えるディレクターの立場から記述してください。
3. **具体的なインテリジェンスの「刺し】**: パトロール結果にある特定キーワード（例：KDDIの『未来のコンビニ』など）を、自身の「AI指揮能力」や「環境設計」の文脈で再解釈して組み込んでください。
4. **文字数遵守**: 400文字前後（設問に応じて）を厳守。

出力形式：
# Refined (Authentic User Voice): [元のファイル名]
## 修正後のドラフト
...
## Voice Logic (なぜこの「自分らしい」表現にしたか)
...
"#,
        original_content, intel_context
    );

    match ask_llm(&prompt).await {
        Ok(refined_content) => {
            let timestamp = Local::now().format("%Y%m%d_%H%M%S").to_string();
            let output_filename = format!("REFINED_{}_{}", timestamp, filename);
            let output_path = output_dir.join(&output_filename);

            fs::write(&output_path, refined_content)?;
            println!("   ✅ Saved to: {}", output_filename);
        }
        Err(e) => {
            println!("   ❌ Error: {}", e);
        }
    }

    Ok(())
}

fn load_latest_intelligence(
    company_name: &str,
    intel_dir: &Path,
) -> Result<Vec<Intelligence>, Box<dyn std::error::Error>> {
    let pattern = format!("{}/SHUKATSU_*.json", intel_dir.to_string_lossy());
    let mut relevant_data = Vec::new();

    for entry in glob(&pattern)? {
        let path = entry?;
        let content = fs::read_to_string(&path)?;
        let intel: Intelligence = match serde_json::from_str(&content) {
            Ok(i) => i,
            Err(_) => continue,
        };

        let is_relevant = intel.title.to_lowercase().contains(&company_name.to_lowercase()) || 
            intel.ai_analysis.as_ref()
                .and_then(|a| a.company.as_ref())
                .map(|c| c.to_lowercase().contains(&company_name.to_lowercase()))
                .unwrap_or(false);

        if is_relevant {
            relevant_data.push(intel);
        }
    }

    relevant_data.sort_by(|a, b| b.collected_at.cmp(&a.collected_at));
    Ok(relevant_data.into_iter().take(3).collect())
}

async fn ask_llm(prompt: &str) -> Result<String, Box<dyn std::error::Error>> {
    // 1. Gemini (via official API)
    if let Ok(api_key) = env::var("GEMINI_API_KEY") {
        println!("   [LLM] Trying Gemini Pro...");
        let client = reqwest::Client::new();
        let url = format!(
            "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={}",
            api_key
        );

        let body = json!({
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 8192
            }
        });

        let res = client.post(url).json(&body).send().await?;
        if res.status().is_success() {
            let json: serde_json::Value = res.json().await?;
            if let Some(text) = json["candidates"][0]["content"]["parts"][0]["text"].as_str() {
                return Ok(text.to_string());
            }
        } else {
             println!("   [LLM] ⚠️ Gemini failed: {}", res.status());
        }
    }

    // 2. Groq (via official API)
    if let Ok(api_key) = env::var("GROQ_API_KEY") {
        println!("   [LLM] Trying Groq...");
        let client = reqwest::Client::new();
        let body = json!({
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        });

        let res = client.post("https://api.groq.com/openai/v1/chat/completions")
            .header("Authorization", format!("Bearer {}", api_key))
            .json(&body)
            .send().await?;

        if res.status().is_success() {
            let json: serde_json::Value = res.json().await?;
            if let Some(text) = json["choices"][0]["message"]["content"].as_str() {
                return Ok(text.to_string());
            }
        }
    }

    // 3. Ollama (Local Fallback)
    println!("   [LLM] Trying Ollama (fallback)...");
    let client = reqwest::Client::new();
    let body = json!({
        "model": "gemma2:9b",
        "prompt": prompt,
        "stream": false
    });

    let res = client.post("http://localhost:11434/api/generate")
        .json(&body)
        .send().await?;

    if res.status().is_success() {
        let json: serde_json::Value = res.json().await?;
        if let Some(text) = json["response"].as_str() {
            return Ok(text.to_string());
        }
    }

    Err("All LLM providers failed".into())
}
