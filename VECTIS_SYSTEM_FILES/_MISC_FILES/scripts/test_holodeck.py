from orchestrator import SecretaryOrchestrator
import os

def test_holodeck():
    orch = SecretaryOrchestrator()
    command = "最新の将棋AIに関連した就活のアイデアをホロデッキで出して"
    print(f"Testing command: {command}")
    
    orch.execute_command(command)
    
    # Verify outputs
    asset_dir = os.path.join("outputs", "assets")
    card_dir = os.path.join("outputs", "cards")
    
    print("\n--- Verification ---")
    if os.path.exists(asset_dir):
        assets = os.listdir(asset_dir)
        print(f"Assets created: {assets}")
    
    if os.path.exists(card_dir):
        cards = [f for f in os.listdir(card_dir) if f.startswith("[H]")]
        print(f"Holodeck cards created: {len(cards)}")
        for c in cards:
            print(f" - {c}")

if __name__ == "__main__":
    test_holodeck()
