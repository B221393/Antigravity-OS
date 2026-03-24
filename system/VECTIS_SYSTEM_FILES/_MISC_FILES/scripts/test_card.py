from orchestrator import SecretaryOrchestrator
import os

def test_card_generation():
    orch = SecretaryOrchestrator()
    # Mocking research and card creation
    command = "大西配列について詳しく調べてカードにして"
    print(f"Testing command: {command}")
    orch.execute_command(command)
    
    # Check if cards directory has content
    card_dir = "cards"
    if os.path.exists(card_dir):
        files = os.listdir(card_dir)
        print(f"Cards in {card_dir}: {files}")
        for f in files:
            if f.endswith(".kcard"):
                print(f"SUCCESS: Found kcard file {f}")
    else:
        print("FAILURE: cards directory not found.")

if __name__ == "__main__":
    test_card_generation()
