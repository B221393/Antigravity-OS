
import sys
import datetime

def run():
    print("=== Disk Logger 9 ===")
    print("Category: System")
    print("Description: Micro tool for Disk Logger 9")
    print("-" * 30)
    # LOGIC
    print(f'Logged at {datetime.datetime.now()}')
    print("-" * 30)
    input("Press Enter to close...")

if __name__ == "__main__":
    run()
