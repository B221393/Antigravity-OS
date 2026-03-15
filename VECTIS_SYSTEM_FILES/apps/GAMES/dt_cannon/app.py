
import os
import time
import random

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def main():
    score = 0
    ammo = 10
    
    print("🎯 DT CANNON - STRESS RELIEF SYSTEM 🎯")
    print("=======================================")
    print("Destroy the distractions preventing your deep work!")
    time.sleep(1)

    targets = ["SNS Notification", "Useless Meeting", "Self Doubt", "YouTube Short", "Buggy Code"]

    while ammo > 0:
        clear()
        target = random.choice(targets)
        print(f"\n👾 ENEMY APPROACHING: [{target}]")
        print(f"❤️  AMMO: {ammo} | 🏆 SCORE: {score}")
        
        action = input("\n[F]ire Cannon / [R]eload / [Q]uit > ").upper()
        
        if action == "F":
            if random.random() > 0.2:
                print(f"\n💥 BOOM! You destroyed {target}!")
                score += 100
                ammo -= 1
            else:
                print(f"\n💨 MISS! {target} is laughing at you.")
                ammo -= 1
        elif action == "R":
            print("\n🔄 Reloading...")
            ammo = 10
            time.sleep(0.5)
        elif action == "Q":
            break
        
        time.sleep(0.8)

    print(f"\n🏁 GAME OVER. FINAL SCORE: {score}")
    print("Return to your work, Agent.")
    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()
