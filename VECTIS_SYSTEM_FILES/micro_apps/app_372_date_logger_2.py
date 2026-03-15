
import sys
import datetime

def run():
    print("=== Date Logger 2 ===")
    print("Category: Health")
    print("Description: Micro tool for Date Logger 2")
    print("-" * 30)
    # LOGIC
    print(f'Logged at {datetime.datetime.now()}')
    print("-" * 30)
    input("Press Enter to close...")

if __name__ == "__main__":
    run()
