import json
import os
import datetime

class HolodeckEngine:
    def __init__(self, researcher, card_engine=None):
        self.researcher = researcher
        self.card_engine = card_engine
        self.output_dir = os.path.join("outputs", "assets")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_multidimensional_ideas(self, seed_topic):
        """
        Generates advanced ideas by intersecting 5 dimensions.
        """
        prompt = f"""
        TASK: Multidimensional Idea Holodeck.
        SEED: {seed_topic}
        
        Analyze this topic across 5 Vector Dimensions:
        1. [I] Inside (Values/Passion): User's core motivation.
        2. [O] Outside (Market): What industries or society needs.
        3. [S] Skill (Competency): What expertise is required.
        4. [F] Future (Trends): How it evolves in 5 years.
        5. [X] X-Factor (Intersection): A creative/unexpected 'wildcard' idea.
        
        FORMAT: Return a JSON object with:
        - "summary": A brief meta-analysis.
        - "vectors": {{ "Inside": "...", "Outside": "...", "Skill": "...", "Future": "...", "X_Factor": "..." }}
        - "ideas": [ {{ "title": "...", "description": "...", "dimensions_hit": ["I", "S", etc.] }} ] (Return 3 high-quality ideas)
        
        RETURN RAW JSON ONLY.
        """
        
        response = self.researcher._call_llm(prompt)
        try:
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                data = json.loads(json_match.group(0))
                data["timestamp"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
                data["seed"] = seed_topic
                return data
            return None
        except Exception as e:
            print(f"Holodeck JSON Error: {e}")
            return None

    def save_session(self, data):
        """Save the session data as a JSON log."""
        if not data: return
        filename = f"holodeck_{data['seed'].replace(' ', '_')}.json"
        path = os.path.join(self.output_dir, filename)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
        print(f"Holodeck session saved: {path}")
        return path

    def export_ideas_as_cards(self, data):
        """Convert Holodeck ideas into Knowledge Cards."""
        if not self.card_engine or not data: return
        
        card_paths = []
        for idea in data.get("ideas", []):
            card_data = {
                "title": f"[H] {idea['title']}",
                "genre": "Career",
                "rarity": "Epic",
                "content": idea['description'],
                "source": f"Holodeck Interaction (Seed: {data['seed']})",
                "visual_seed": idea['title'],
                "timestamp": data['timestamp']
            }
            path = self.card_engine.save_kcard(card_data)
            card_paths.append(path)
        return card_paths
