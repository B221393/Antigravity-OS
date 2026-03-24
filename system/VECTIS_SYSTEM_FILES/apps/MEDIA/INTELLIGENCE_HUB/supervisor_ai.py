
import time
import psutil
import os
import sys
from datetime import datetime

# Define processes to monitor
PROCESS_NAMES = [
    "shukatsu_patrol.py",
    "relay_patrol.py",
    "relay_analyzer.py",
    "relay_reporter.py",
    "deep_thinker.py"     # Intelligence Synthesis (Tier 2)
]

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def get_process_status():
    status_map = {name: "🔴 STOPPED" for name in PROCESS_NAMES}
    cpu_map = {name: 0.0 for name in PROCESS_NAMES}
    mem_map = {name: 0.0 for name in PROCESS_NAMES}

    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'cpu_percent', 'memory_info']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline:
                cmd_str = " ".join(cmdline)
                for target in PROCESS_NAMES:
                    if target in cmd_str:
                        status_map[target] = "🟢 RUNNING"
                        cpu_map[target] = proc.info['cpu_percent'] or 0.0
                        mem_map[target] = proc.info['memory_info'].rss / (1024 * 1024)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return status_map, cpu_map, mem_map

def main():
    print("Initializing EGO SUPERVISOR AI...")
    time.sleep(1)
    
    cycle_count = 0
    while True:
        clear_screen()
        status, cpu, mem = get_process_status()
        
        print(f"╔{'═'*56}╗")
        print(f"║   EGO SYSTEM MONITOR  (Supervisor AI)             ║")
        print(f"║   Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                              ║")
        print(f"╠{'═'*56}╣")
        
        for name in PROCESS_NAMES:
            s_icon = "🟢" if status[name].startswith("🟢") else "🔴"
            name_disp = name.ljust(20)
            c_val = cpu[name]
            m_val = mem[name]
            print(f"║ {s_icon} {name_disp} | CPU: {c_val:>4.1f}% | MEM: {m_val:>5.1f} MB ║")
            
        print(f"╚{'═'*56}╝")
        
        # --- Automated Intelligence Audit ---
        cycle_count += 1
        if cycle_count >= 20:
             print("\n🔍 Running Automated Intelligence Audit...")
             import subprocess
             try:
                 # Non-blocking run
                 subprocess.Popen([sys.executable, "intelligence_audit.py"], 
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
             except: pass
             cycle_count = 0
        else:
             print(f"\nNext audit in {20 - cycle_count} cycles...")

        print("\n[LOGS]")

        # --- GENERATE QUANTITATIVE REPORT (EGO_STATUS.txt) ---
        generate_status_report(status, cpu, mem)

        # Check for command queue
        queue_path = os.path.join(os.path.dirname(__file__), "../../../data/command_queue.json")
        if os.path.exists(queue_path):
             print(f"  Found command queue: {queue_path}")
        else:
             print(f"  No command queue active.")

        time.sleep(3)

def generate_status_report(status, cpu, mem):
    """Generates a quantitative text report for the user with Daily Delta tracking."""
    import json
    
    report_path = os.path.join(os.path.expanduser("~"), "Desktop", "app", "EGO_STATUS.txt")
    stats_json_path = os.path.join(os.path.dirname(__file__), "../../../data/daily_stats.json")
    
    racing_gen_total = 0 # Placeholder for this script
            
    patrol_count_total = 0
    patrol_data_dir = os.path.join(os.path.dirname(__file__), "data", "shukatsu")
    if os.path.exists(patrol_data_dir):
        try:
             patrol_count_total = len([name for name in os.listdir(patrol_data_dir) if os.path.isfile(os.path.join(patrol_data_dir, name))])
        except: pass

    thinker_size_kb = 0
    thinker_path = os.path.join(os.path.dirname(__file__), "../../../data/IDENTITY/STRATEGIC_SYNTHESIS.md")
    if os.path.exists(thinker_path):
        try:
            thinker_size_kb = os.path.getsize(thinker_path) / 1024
        except: pass

    today_str = datetime.now().strftime("%Y-%m-%d")
    daily_stats = {}
    
    if os.path.exists(stats_json_path):
        try:
            with open(stats_json_path, 'r') as f:
                daily_stats = json.load(f)
        except: pass
        
    if daily_stats.get("date") != today_str:
        daily_stats = {
            "date": today_str,
            "start_patrol_count": patrol_count_total,
            "start_thinker_kb": thinker_size_kb
        }
        try:
            with open(stats_json_path, 'w') as f:
                json.dump(daily_stats, f)
        except: pass

    delta_patrol = max(0, patrol_count_total - daily_stats.get("start_patrol_count", 0))
    delta_thinker = max(0, thinker_size_kb - daily_stats.get("start_thinker_kb", 0))

    try:
        with open(report_path, "w", encoding="utf-8") as f:
            f.write("██ EGO SYSTEM STATUS REPORT ██\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            
            f.write("[1] REAL-TIME LOAD (Current)\n")
            for name in PROCESS_NAMES:
                clean_name = name.split('.')[0].upper()
                state = "RUNNING" if status[name].startswith("🟢") else "STOPPED"
                f.write(f" • {clean_name:<18} : {state} | MEM: {mem[name]:>6.1f} MB | CPU: {cpu[name]:>4.1f}%\n")
            
            f.write("\n")
            f.write("[2] WORKLOAD METRICS (Quantitative)\n")
            f.write(f" • Intelligence Patrol (Items Analyzed)\n")
            f.write(f"    - Today's Work : +{delta_patrol} Items Analyzed\n")
            f.write(f"    - Total Data   : {patrol_count_total} Files Stored\n\n")
            
            f.write(f" • Deep Thinker Synthesis (Output Volume)\n")
            f.write(f"    - Today's Work : +{delta_thinker:.1f} KB Written\n")
            f.write(f"    - Total Wisdom : {thinker_size_kb:.1f} KB\n")
            
            f.write("\n" + "="*50 + "\n")
            f.write("EGO OPERATING SYSTEM - AUTOMATED MONITOR")
    except Exception:
        pass

if __name__ == "__main__":
    main()
