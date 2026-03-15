
import sys
import datetime

def run():
    print("=== Tax Logger ===")
    print("Category: Dev")
    print("Description: Micro tool for Tax Logger")
    print("-" * 30)
    # LOGIC
    print(f'Logged at {datetime.datetime.now()}')
    print("-" * 30)
    input("Press Enter to close...")

if __name__ == "__main__":
    run()
