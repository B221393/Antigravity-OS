use clap::Parser;
use colored::*;
use rayon::prelude::*;
use std::fs;
use std::path::Path;
use walkdir::WalkDir;

#[derive(Parser, Debug)]
#[command(author, version, about, long_about = None)]
struct Args {
    /// Keyword to search for
    #[arg(short, long)]
    query: String,

    /// Directory to search in (default: current dir)
    #[arg(short, long, default_value = ".")]
    path: String,

    /// Show line contents
    #[arg(short, long)]
    verbose: bool,
}

fn main() {
    let args = Args::parse();

    println!(
        "{}",
        format!(
            "⚡ Flash Grep: Searching for '{}' in '{}'",
            args.query, args.path
        )
        .bold()
        .cyan()
    );

    let entries: Vec<_> = WalkDir::new(&args.path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .collect();

    println!("📂 Files scanned: {}", entries.len());

    entries.par_iter().for_each(|entry| {
        let path = entry.path();
        if let Ok(content) = fs::read_to_string(path) {
            if content.contains(&args.query) {
                print_match(path, &content, &args.query, args.verbose);
            }
        }
    });
}

fn print_match(path: &Path, content: &str, query: &str, verbose: bool) {
    // Simple lock to prevent garbled output is avoided for speed in this simple example,
    // but individual prints are atomic-ish on line basis usually.
    // For strictly clean output in huge parallelism, we'd use a mutex or channel.

    // Just finding the file is often enough
    println!("{} {}", "✅ Found in:".green(), path.display());

    if verbose {
        for (i, line) in content.lines().enumerate() {
            if line.contains(query) {
                println!("   {}: {}", (i + 1).to_string().yellow(), line.trim());
            }
        }
    }
}
