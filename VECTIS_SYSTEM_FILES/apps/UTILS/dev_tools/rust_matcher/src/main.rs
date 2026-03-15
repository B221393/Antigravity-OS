use clap::Parser;
use rayon::prelude::*;
use std::collections::HashSet;
use std::error::Error;
use std::fs;

#[derive(Parser)]
struct Args {
    #[arg(short, long)]
    keywords: String, // Path to keywords.txt
    #[arg(short, long)]
    target: String, // Text to match against (or file path)
}

fn main() -> Result<(), Box<dyn Error>> {
    let args = Args::parse();

    // Load Keywords
    let kw_content = fs::read_to_string(&args.keywords).unwrap_or_default();
    let keywords: Vec<&str> = kw_content
        .lines()
        .map(|l| l.trim())
        .filter(|l| !l.is_empty() && !l.starts_with('#'))
        .collect();

    if keywords.is_empty() {
        println!("NO_MATCH");
        return Ok(());
    }

    // Target (Assume passed directly as string for simplicity in CLI usage, or file)
    let target_text = args.target.to_lowercase();

    // Parallel Match
    let matched: Vec<&str> = keywords
        .par_iter()
        .filter(|&&kw| target_text.contains(&kw.to_lowercase()))
        .cloned()
        .collect();

    if matched.is_empty() {
        println!("NO_MATCH");
    } else {
        // Output matched keywords comma separated
        println!("{}", matched.join(","));
    }

    Ok(())
}
