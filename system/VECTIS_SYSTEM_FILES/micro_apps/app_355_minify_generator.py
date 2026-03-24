
import sys
import datetime

def run():
    print("=== Minify Generator ===")
    print("Category: Hobby")
    print("Description: Micro tool for Minify Generator")
    print("-" * 30)
    # LOGIC
    print(f'Generated: {hash(datetime.datetime.now())}')
    print("-" * 30)
    input("Press Enter to close...")

if __name__ == "__main__":
    run()
