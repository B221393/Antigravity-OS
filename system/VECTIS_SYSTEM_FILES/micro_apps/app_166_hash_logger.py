
import sys
import datetime

def run():
    print("=== Hash Logger ===")
    print("Category: System")
    print("Description: Micro tool for Hash Logger")
    print("-" * 30)
    # LOGIC
    print(f'Logged at {datetime.datetime.now()}')
    print("-" * 30)
    input("Press Enter to close...")

if __name__ == "__main__":
    run()
