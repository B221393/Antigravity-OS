use std::env;
use sysinfo::{ProcessExt, System, SystemExt};

fn main() {
    let mut sys = System::new_all();
    sys.refresh_all();

    // Default targets
    let targets = vec!["python", "node", "streamlit", "powershell", "cmd"];

    let args: Vec<String> = env::args().collect();
    let safe_mode = !args.contains(&"--force".to_string());

    println!("🔫 Scanning for processes...");

    let mut killed = 0;

    for (pid, process) in sys.processes() {
        let name = process.name().to_lowercase();

        for t in &targets {
            if name.contains(t) {
                // Determine if we should kill ourselves?
                // We are 'process_killer', so avoid suicide until end?
                // sysinfo usually reports exe name.

                if name.contains("process_killer") {
                    continue;
                }

                // In safe mode, maybe just list? No, Panic button means KILL.
                // But let's skip "Code" (VS Code) or critical system.
                if name.contains("code") || name.contains("explorer") {
                    continue;
                }

                println!("Killing [{}] {} ...", pid, name);
                if process.kill() {
                    killed += 1;
                }
            }
        }
    }

    println!("💀 Eliminated {} processes.", killed);
}
