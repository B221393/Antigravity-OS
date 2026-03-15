use clap::{Parser, Subcommand};
use rayon::prelude::*;
use regex::Regex;
use std::collections::HashMap;
use std::fs::{self, File};
use std::io::{self, BufRead, BufReader, Write};
use std::path::Path;

#[derive(Parser)]
#[command(name = "vectis_core")]
#[command(about = "High-performance core utilities for EGO OS", long_about = None)]
struct Cli {
    #[command(subcommand)]
    command: Commands,
}

#[derive(Subcommand)]
enum Commands {
    /// Scan logs for errors and stats
    ScanLogs {
        #[arg(short, long)]
        path: String,
        #[arg(short, long, default_value_t = 50)]
        limit: usize,
    },
    /// Calculate stats from CSV
    CalcStats {
        #[arg(short, long)]
        file: String,
        #[arg(short, long)]
        column: String,
    },
    /// System health check (fast file scan)
    HealthCheck {
        #[arg(short, long)]
        root: String,
    },
}

fn main() {
    let cli = Cli::parse();

    match &cli.command {
        Commands::ScanLogs { path, limit } => scan_logs(path, *limit),
        Commands::CalcStats { file, column } => calc_stats(file, column),
        Commands::HealthCheck { root } => health_check(root),
    }
}

// --- Implementations ---

fn scan_logs(path: &str, limit: usize) {
    let p = Path::new(path);
    if !p.exists() {
        println!("{{ \"error\": \"Path not found\" }}");
        return;
    }

    // Logic: If file, tail it. If dir, find LAST_ERROR.md and others.
    // For simplicity, we assume pointing to a log file or dir and we return JSON.

    let mut results = Vec::new();

    if p.is_file() {
        if let Ok(file) = File::open(p) {
            let reader = BufReader::new(file);
            // Naive tail: read all, take last N. For huge logs, seek from end is better but this is MVP.
            let lines: Vec<String> = reader.lines().filter_map(|l| l.ok()).collect();
            let count = lines.len();
            let start = if count > limit { count - limit } else { 0 };

            for i in start..count {
                results.push(lines[i].clone());
            }
        }
    } else if p.is_dir() {
        // Find "LAST_ERROR.md" or .log files
        for entry in walkdir::WalkDir::new(p).into_iter().filter_map(|e| e.ok()) {
            if entry
                .path()
                .extension()
                .map_or(false, |e| e == "md" || e == "log" || e == "jsonl")
            {
                // Scan logic could go here
            }
        }
    }

    // Output as JSON
    let json_out = serde_json::json!({
        "lines": results,
        "count": results.len()
    });
    println!("{}", json_out.to_string());
}

fn calc_stats(file: &str, col: &str) {
    // fast CSV read
    let mut rdr = match csv::Reader::from_path(file) {
        Ok(r) => r,
        Err(_) => {
            println!("{{ \"error\": \"CSV error\" }}");
            return;
        }
    };

    let headers = rdr.headers().cloned().unwrap_or_default();
    let col_idx = headers.iter().position(|h| h == col);

    if let Some(idx) = col_idx {
        let mut sum = 0.0;
        let mut count = 0;
        let mut min = f64::MAX;
        let mut max = f64::MIN;

        for result in rdr.records() {
            if let Ok(record) = result {
                if let Some(val_str) = record.get(idx) {
                    if let Ok(val) = val_str.parse::<f64>() {
                        sum += val;
                        count += 1;
                        if val < min {
                            min = val;
                        }
                        if val > max {
                            max = val;
                        }
                    }
                }
            }
        }

        if count > 0 {
            let avg = sum / count as f64;
            println!(
                "{}",
                serde_json::json!({
                    "sum": sum,
                    "avg": avg,
                    "min": min,
                    "max": max,
                    "count": count
                })
            );
        } else {
            println!("{{ \"error\": \"No numeric data\" }}");
        }
    } else {
        println!("{{ \"error\": \"Column not found\" }}");
    }
}

fn health_check(root: &str) {
    // Parallel file walk to count files and check size
    let walker = walkdir::WalkDir::new(root);
    let (count, size) = walker
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        // .par_bridge() // Rayon bridge for iterator
        .fold((0, 0), |(c, s), e| {
            (c + 1, s + e.metadata().map(|m| m.len()).unwrap_or(0))
        });

    println!(
        "{}",
        serde_json::json!({
            "total_files": count,
            "total_size_bytes": size,
            "status": "OK"
        })
    );
}
