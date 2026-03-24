
import time
import os
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    clear()
    print("🏰 KNOWLEDGE SPIRE (Tower Defense Quiz) 🏰")
    print("==========================================")
    print("Defend the Spire by answering technical questions!")
    input("Press Enter to start...")

    spire_health = 100
    questions = [
        {"q": "What is the command to list files in Linux?", "a": "ls"},
        {"q": "What does HTTP stand for?", "a": "hypertext transfer protocol"},
        {"q": "Which Python keyword defines a function?", "a": "def"},
        {"q": "What is the capital of Japan?", "a": "tokyo"},
        {"q": "Is Python compiled or interpreted?", "a": "interpreted"}
    ]

    for q_data in questions:
        if spire_health <= 0:
            break
            
        clear()
        print(f"❤️  Spire Health: {spire_health}")
        print(f"\n🛡️  INCOMING ATTACK: {q_data['q']}")
        
        answer = input("Your Defnese > ").lower().strip()
        
        if answer == q_data['a']:
            print("\n✨ BLOCK SUCCESSFUL! The enemy is repealed.")
        else:
            print(f"\n💥 FAILURE! Correct answer: {q_data['a']}")
            spire_health -= 25
            
        time.sleep(1.5)

    clear()
    if spire_health > 0:
        print(f"🏆 VICTORY! The Spire stands tall. Health: {spire_health}")
    else:
        print("🔥 DEFEAT. The Spire has fallen.")
        
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
