use clap::Parser;
use colored::*;
use rayon::prelude::*;
use std::fs::File;
use std::io::{self, BufRead, BufReader};
use std::path::Path;
use walkdir::WalkDir;

#[derive(Parser)]
struct Args {
    #[arg(default_value = ".")]
    path: String,
}

fn count_lines(path: &Path) -> io::Result<usize> {
    let file = File::open(path)?;
    let reader = BufReader::new(file);
    let mut count = 0;
    for _ in reader.lines() {
        count += 1;
    }
    Ok(count)
}

fn main() {
    let args = Args::parse();
    println!("{}", "⚡ Flash Count: Calculating LOC...".cyan().bold());

    let entries: Vec<_> = WalkDir::new(&args.path)
        .into_iter()
        .filter_map(|e| e.ok())
        .filter(|e| e.file_type().is_file())
        .collect();

    let total_lines: usize = entries
        .par_iter()
        .map(|entry| {
            let path = entry.path();
            // Simple filter for code/text files by extension could be added here
            if let Ok(lines) = count_lines(path) {
                // optional: println!("  {}: {}", path.display(), lines);
                lines
            } else {
                0
            }
        })
        .sum();

    println!("📂 Files Scanned: {}", entries.len());
    println!(
        "📝 Total Lines: {}",
        total_lines.to_string().yellow().bold()
    );
}
