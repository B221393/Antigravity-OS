
import time
import random
import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

SENTENCES = [
    "The quick brown fox jumps over the lazy dog.",
    "Python is a powerful programming language.",
    "EGO is the ultimate productivity system.",
    "Artificial Intelligence will revolutionize the world.",
    "Keep calm and code on.",
    "Debugging is like being the detective in a crime movie."
]

def main():
    clear()
    print("⌨️  EGO TYPING SPEED TEST ⌨️")
    print("===============================")
    input("Press Enter to start...")

    score = 0
    rounds = 3

    for i in range(rounds):
        clear()
        target = random.choice(SENTENCES)
        print(f"Round {i+1}/{rounds}")
        print("\nType this:")
        print(f"\033[1;36m{target}\033[0m")
        print("------------------------------------------")
        
        start_time = time.time()
        user_input = input("> ")
        end_time = time.time()
        
        duration = end_time - start_time
        wpm = (len(user_input) / 5) / (duration / 60)
        
        if user_input == target:
            print(f"\n✅ Perfect! Time: {duration:.2f}s | WPM: {wpm:.1f}")
            score += wpm
        else:
            print(f"\n❌ Mismatch! Time: {duration:.2f}s")
        
        time.sleep(2)

    avg_wpm = score / rounds
    print(f"\n🏆 TEST COMPLETE. Average WPM: {avg_wpm:.1f}")
    if avg_wpm > 40:
        print("Rating: 🚀 Neural Interface Compatible")
    else:
        print("Rating: 🐢 Needs Calibration")
    
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
