//! VECTIS Core - High Performance Computation Library
//!
//! This Rust library provides optimized functions for:
//! - Keyword extraction
//! - Similarity calculation (Jaccard Index)
//! - File scanning
//! - Text analysis
//!
//! Exposed to Python via PyO3

use flate2::read::GzDecoder;
use flate2::write::GzEncoder;
use flate2::Compression;
use pyo3::prelude::*;
use rayon::prelude::*;
use regex::Regex;
use sha2::{Digest, Sha256};
use std::collections::{HashMap, HashSet};
use std::fs;
use std::io::{Read, Write};
use std::path::Path;
use unicode_normalization::UnicodeNormalization;

/// Keywords list for extraction (Japanese + English)
const KEYWORDS: &[&str] = &[
    // Tech
    "ai",
    "python",
    "rust",
    "javascript",
    "typescript",
    "react",
    "api",
    "gpu",
    "cpu",
    "llm",
    "機械学習",
    "深層学習",
    "ディープラーニング",
    "ニューラルネットワーク",
    "データサイエンス",
    "プログラミング",
    "コーディング",
    "開発",
    "エンジニア",
    "技術",
    "テクノロジー",
    // Business
    "ビジネス",
    "経済",
    "投資",
    "株",
    "マーケティング",
    "戦略",
    "経営",
    "起業",
    "スタートアップ",
    "生産性",
    "効率",
    "最適化",
    "自動化",
    "イノベーション",
    // Learning
    "学習",
    "勉強",
    "教育",
    "研究",
    "論文",
    "科学",
    "数学",
    "物理",
    "化学",
    "生物",
    "読書",
    "知識",
    "情報",
    "分析",
    "思考",
    "理論",
    "実践",
    // Job hunting
    "就活",
    "就職",
    "転職",
    "採用",
    "面接",
    "志望動機",
    "自己pr",
    "ガクチカ",
    "es",
    "企業",
    "会社",
    "業界",
    "キャリア",
    "将来",
    "成長",
    "挑戦",
    // Life
    "習慣",
    "健康",
    "運動",
    "睡眠",
    "食事",
    "メンタル",
    "ストレス",
    "モチベーション",
    "目標",
    "計画",
    "時間管理",
    "タスク",
    "優先順位",
    // Media
    "youtube",
    "動画",
    "ニュース",
    "ブログ",
    "sns",
    "twitter",
    "instagram",
    // Self-improvement
    "自己啓発",
    "成功",
    "努力",
    "継続",
    "挑戦",
    "失敗",
    "成長マインドセット",
    // TOEIC Specific (Business/Semi-academic)
    "negotiation",
    "contract",
    "inventory",
    "quarterly",
    "profit",
    "merger",
    "requisition",
    "commencement",
    "compliance",
    "logistics",
    "subsidiary",
    "見積もり",
    "契約",
    "在庫",
    "利益",
    "合併",
    "物流",
    "遵守",
    "開始",
];

/// Normalize text for comparison (lowercase + NFKC normalization)
fn normalize_text(text: &str) -> String {
    text.to_lowercase().nfkc().collect::<String>()
}

/// Extract keywords from text
#[pyfunction]
fn extract_keywords(text: &str) -> HashSet<String> {
    let normalized = normalize_text(text);
    let mut found = HashSet::new();

    for &kw in KEYWORDS {
        if normalized.contains(kw) {
            found.insert(kw.to_string());
        }
    }

    found
}

/// Calculate Jaccard similarity between two keyword sets
#[pyfunction]
fn jaccard_similarity(set_a: HashSet<String>, set_b: HashSet<String>) -> f64 {
    if set_a.is_empty() || set_b.is_empty() {
        return 0.0;
    }

    let intersection = set_a.intersection(&set_b).count();
    let union = set_a.union(&set_b).count();

    if union == 0 {
        0.0
    } else {
        (intersection as f64) / (union as f64) * 100.0
    }
}

/// Calculate similarity matrix for multiple texts (parallel processing)
#[pyfunction]
fn calculate_similarity_matrix(texts: Vec<String>, threshold: f64) -> Vec<(usize, usize, f64)> {
    let keywords: Vec<HashSet<String>> = texts.par_iter().map(|t| extract_keywords(t)).collect();

    let n = keywords.len();
    let mut results = Vec::new();

    // Parallel similarity calculation
    let pairs: Vec<(usize, usize, f64)> = (0..n)
        .into_par_iter()
        .flat_map(|i| {
            let keywords_ref = &keywords;
            (i + 1..n)
                .filter_map(move |j| {
                    let set_i = &keywords_ref[i];
                    let set_j = &keywords_ref[j];

                    if set_i.is_empty() || set_j.is_empty() {
                        return None;
                    }

                    let intersection = set_i.intersection(set_j).count();
                    let union = set_i.union(set_j).count();

                    if union == 0 {
                        return None;
                    }

                    let similarity = (intersection as f64) / (union as f64) * 100.0;

                    if similarity >= threshold {
                        Some((i, j, similarity))
                    } else {
                        None
                    }
                })
                .collect::<Vec<_>>()
        })
        .collect();

    results.extend(pairs);
    results
}

/// Analyze content for 3D positioning
#[pyfunction]
fn analyze_content_3d(content: &str, title: &str) -> (f64, f64, f64) {
    let combined = normalize_text(&format!("{} {}", content, title));

    // X-axis: Entertainment (-50) vs Academic (+50)
    let entertainment_kw = [
        "おもしろ",
        "笑",
        "雑談",
        "ネタ",
        "爆笑",
        "エンタメ",
        "面白",
        "ゆる",
        "バラエティ",
    ];
    let academic_kw = [
        "研究", "論文", "理論", "分析", "専門", "学術", "科学", "哲学", "数学",
    ];

    let ent_score: f64 = entertainment_kw
        .iter()
        .filter(|k| combined.contains(*k))
        .count() as f64
        * 5.0;
    let acad_score: f64 = academic_kw.iter().filter(|k| combined.contains(*k)).count() as f64 * 5.0;
    let x = ent_score - acad_score;

    // Y-axis: Easy (-50) vs Hard (+50)
    let easy_kw = [
        "初心者",
        "簡単",
        "わかりやすい",
        "入門",
        "基礎",
        "やさしい",
        "はじめて",
    ];
    let hard_kw = [
        "高度",
        "専門的",
        "難解",
        "複雑",
        "詳細",
        "深い",
        "上級",
        "応用",
    ];

    let easy_score: f64 = easy_kw.iter().filter(|k| combined.contains(*k)).count() as f64 * 5.0;
    let hard_score: f64 = hard_kw.iter().filter(|k| combined.contains(*k)).count() as f64 * 5.0;
    let length_factor = (content.len() as f64 / 1000.0).min(20.0);
    let y = (hard_score - easy_score) + length_factor;

    // Z-axis: Theoretical (-50) vs Practical (+50)
    let theoretical_kw = ["なぜ", "考察", "歴史", "起源", "概念", "思想", "哲学"];
    let practical_kw = [
        "方法",
        "やり方",
        "コツ",
        "実践",
        "活用",
        "アクション",
        "使える",
        "ハウツー",
    ];

    let theoretical_score: f64 = theoretical_kw
        .iter()
        .filter(|k| combined.contains(*k))
        .count() as f64
        * 5.0;
    let practical_score: f64 = practical_kw
        .iter()
        .filter(|k| combined.contains(*k))
        .count() as f64
        * 5.0;
    let z = practical_score - theoretical_score;

    (x, y, z)
}

/// Batch analyze multiple contents (parallel)
#[pyfunction]
fn batch_analyze_3d(contents: Vec<(String, String)>) -> Vec<(f64, f64, f64)> {
    contents
        .par_iter()
        .map(|(content, title)| analyze_content_3d(content, title))
        .collect()
}

/// Scan directory for files with specific extensions
#[pyfunction]
fn scan_files(directory: &str, extensions: Vec<String>) -> Vec<(String, u64, u64)> {
    let path = Path::new(directory);

    if !path.exists() || !path.is_dir() {
        return Vec::new();
    }

    let ext_set: HashSet<String> = extensions.into_iter().map(|e| e.to_lowercase()).collect();

    walkdir(path, &ext_set)
}

fn walkdir(path: &Path, extensions: &HashSet<String>) -> Vec<(String, u64, u64)> {
    let mut results = Vec::new();

    if let Ok(entries) = fs::read_dir(path) {
        for entry in entries.filter_map(|e| e.ok()) {
            let entry_path = entry.path();

            if entry_path.is_dir() {
                results.extend(walkdir(&entry_path, extensions));
            } else if entry_path.is_file() {
                if let Some(ext) = entry_path.extension() {
                    let ext_str = ext.to_string_lossy().to_lowercase();
                    if extensions.contains(&ext_str) {
                        let file_path = entry_path.to_string_lossy().to_string();
                        let size = entry.metadata().map(|m| m.len()).unwrap_or(0);
                        let mtime = entry
                            .metadata()
                            .and_then(|m| m.modified())
                            .map(|t| {
                                t.duration_since(std::time::UNIX_EPOCH)
                                    .unwrap_or_default()
                                    .as_secs()
                            })
                            .unwrap_or(0);

                        results.push((file_path, size, mtime));
                    }
                }
            }
        }
    }

    results
}

/// Read file content (with UTF-8 fallback)
#[pyfunction]
fn read_file_content(path: &str) -> Option<String> {
    fs::read_to_string(path).ok()
}

/// Parse JSON file
#[pyfunction]
fn parse_json_file(path: &str) -> Option<String> {
    let content = fs::read_to_string(path).ok()?;
    // Just validate it's valid JSON and return as string
    let _: serde_json::Value = serde_json::from_str(&content).ok()?;
    Some(content)
}

/// Calculate relevance for TOEIC preparation (Business context score)
#[pyfunction]
fn calculate_toeic_relevance(text: &str) -> f64 {
    let normalized = normalize_text(text);
    let toeic_keywords = [
        "office",
        "meeting",
        "colleague",
        "client",
        "project",
        "deadline",
        "email",
        "presentation",
        "report",
        "schedule",
        "appointment",
        "travel",
        "itinerary",
        "flight",
        "hotel",
        "reservation",
        "shopping",
        "warranty",
        "refund",
        "customer",
        "service",
    ];

    let count = toeic_keywords
        .iter()
        .filter(|k| normalized.contains(*k))
        .count();

    (count as f64 * 10.0).min(100.0)
}

/// Get keyword count for sorting/ranking
#[pyfunction]
fn count_keywords(text: &str) -> usize {
    extract_keywords(text).len()
}

/// Calculate batch keyword counts (parallel)
#[pyfunction]
fn batch_keyword_counts(texts: Vec<String>) -> Vec<usize> {
    texts
        .par_iter()
        .map(|t| extract_keywords(t).len())
        .collect()
}

/// Perform Gzip compression on text (returning binary data as Vec<u8>)
#[pyfunction]
fn compress_data(data: &str) -> Vec<u8> {
    let mut encoder = GzEncoder::new(Vec::new(), Compression::default());
    encoder.write_all(data.as_bytes()).unwrap();
    encoder.finish().unwrap()
}

/// Decompress Gzip data
#[pyfunction]
fn decompress_data(data: Vec<u8>) -> Option<String> {
    let mut decoder = GzDecoder::new(&data[..]);
    let mut s = String::new();
    decoder.read_to_string(&mut s).ok()?;
    Some(s)
}

/// Generate a 'Semantic Hash' (SHA256 of normalized keywords) to identify redundant content
#[pyfunction]
fn generate_semantic_hash(text: &str) -> String {
    let keywords = extract_keywords(text);
    let mut sorted_kws: Vec<_> = keywords.into_iter().collect();
    sorted_kws.sort();
    let normalized_stream = sorted_kws.join("|");

    let mut hasher = Sha256::new();
    hasher.update(normalized_stream);
    format!("{:x}", hasher.finalize())
}

/// Python module definition
#[pymodule]
fn vectis_core(m: &Bound<'_, PyModule>) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(extract_keywords, m)?)?;
    m.add_function(wrap_pyfunction!(jaccard_similarity, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_similarity_matrix, m)?)?;
    m.add_function(wrap_pyfunction!(analyze_content_3d, m)?)?;
    m.add_function(wrap_pyfunction!(batch_analyze_3d, m)?)?;
    m.add_function(wrap_pyfunction!(scan_files, m)?)?;
    m.add_function(wrap_pyfunction!(read_file_content, m)?)?;
    m.add_function(wrap_pyfunction!(parse_json_file, m)?)?;
    m.add_function(wrap_pyfunction!(count_keywords, m)?)?;
    m.add_function(wrap_pyfunction!(batch_keyword_counts, m)?)?;
    m.add_function(wrap_pyfunction!(calculate_toeic_relevance, m)?)?;
    m.add_function(wrap_pyfunction!(compress_data, m)?)?;
    m.add_function(wrap_pyfunction!(decompress_data, m)?)?;
    m.add_function(wrap_pyfunction!(generate_semantic_hash, m)?)?;
    Ok(())
}
