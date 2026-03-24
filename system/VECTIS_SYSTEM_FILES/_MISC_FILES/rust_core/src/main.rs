use std::env;
use std::io::{self, Write};
use std::process::Command;

fn smart_route_model(text: &str) -> &'static str {
    let text_lower = text.to_lowercase();
    let complex_triggers = [
        "code",
        "python",
        "script",
        "analyze",
        "reason",
        "plan",
        "strategy",
        "why",
        "how to",
        "create",
        "generate",
        "summary",
        "summarize",
        "job",
        "career",
        "philosophy",
        "complex",
        "math",
        "calculate",
        "study",
        "rust",
    ];

    if text.split_whitespace().count() > 15 {
        return "phi4";
    }

    for trigger in complex_triggers.iter() {
        if text_lower.contains(trigger) {
            return "phi4";
        }
    }

    "llama3.2:latest"
}

fn call_ollama(model: &str, prompt: &str) {
    println!("\n[RUST CORE] Using Brain: {}", model);
    print!("[RUST CORE] Thinking...");
    io::stdout().flush().unwrap();

    let output = Command::new("ollama")
        .arg("run")
        .arg(model)
        .arg(prompt)
        .output()
        .expect("Failed to execute ollama command");

    println!("\r[RUST CORE] Response:   "); // Clear 'Thinking'
    println!("{}", String::from_utf8_lossy(&output.stdout));

    if !output.stderr.is_empty() {
        eprintln!("Error: {}", String::from_utf8_lossy(&output.stderr));
    }
}

fn main() {
    let args: Vec<String> = env::args().collect();

    // Simple Interactive Mode if no args
    if args.len() < 2 {
        println!("========================================");
        println!("   🦀 VECTIS RUST CORE (NATIVE) 🦀");
        println!("   Power: Extreme | Memory: Safety");
        println!("========================================");

        loop {
            print!("\nYOU > ");
            io::stdout().flush().unwrap();

            let mut input = String::new();
            match io::stdin().read_line(&mut input) {
                Ok(_) => {
                    let input = input.trim();
                    if input == "exit" {
                        break;
                    }
                    if input.is_empty() {
                        continue;
                    }

                    let model = smart_route_model(input);
                    call_ollama(model, input);
                }
                Err(error) => println!("error: {}", error),
            }
        }
    } else {
        // CLI Mode
        let input = &args[1];
        let model = smart_route_model(input);
        call_ollama(model, input);
    }
}
