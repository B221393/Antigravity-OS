
import os
import json
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
from modules.researcher import ResearchAgent

class KnowledgeMapper:
    def __init__(self, researcher_agent):
        self.card_dir = os.path.join("outputs", "cards")
        self.output_dir = os.path.join("outputs", "maps")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
        self.researcher = researcher_agent

    def load_cards(self):
        cards = []
        if not os.path.exists(self.card_dir):
            return []
        for f in os.listdir(self.card_dir):
            if f.endswith(".kcard"):
                try:
                    with open(os.path.join(self.card_dir, f), "r", encoding="utf-8") as file:
                        c = json.load(file)
                        c['filename'] = f # Keep track of filename
                        cards.append(c)
                except: pass
        return cards

    def generate_map(self, user_instruction):
        """
        Analyzes cards based on user instruction and generates a 2D scatter plot.
        """
        cards = self.load_cards()
        if not cards:
            return "No cards found to map."
            
        # 1. Determine Axes
        print("Determining Map Axes...")
        axes_prompt = f"""
        TASK: Determine 2 comparison axes for a scatter plot based on the user's request.
        REQUEST: {user_instruction}
        
        OUTPUT format (JSON only):
        {{
            "x_axis": "Name of X axis (e.g. Market Size)",
            "y_axis": "Name of Y axis (e.g. Future Growth)",
            "x_min": "Label for low X",
            "x_max": "Label for high X",
            "y_min": "Label for low Y",
            "y_max": "Label for high Y"
        }}
        """
        import re
        try:
            res = self.researcher._call_llm(axes_prompt)
            match = re.search(r'\{.*\}', res, re.DOTALL)
            if match:
                axes = json.loads(match.group(0))
            else:
                # Fallback
                axes = {
                    "x_axis": "Relevance", "y_axis": "Impact",
                    "x_min": "Low", "x_max": "High", "y_min": "Low", "y_max": "High"
                }
        except:
            axes = {
                "x_axis": "Relevance", "y_axis": "Impact",
                "x_min": "Low", "x_max": "High", "y_min": "Low", "y_max": "High"
            }
            
        print(f"Axes determined: {axes['x_axis']} vs {axes['y_axis']}")

        # 2. Score Cards
        print("Scoring cards...")
        map_data = []
        
        # Batch processing or loop? Loop for simplicity now.
        for card in cards:
            content_snippet = f"Title: {card.get('title')}\nContent: {card.get('content')}"
            score_prompt = f"""
            TASK: Evaluate this content on two axes: "{axes['x_axis']}" and "{axes['y_axis']}".
            CONTENT: {content_snippet}
            
            Return two numbers (0-10), comma separated.
            Example: 5, 8
            """
            try:
                score_res = self.researcher._call_llm(score_prompt).strip()
                # Simple parsing finding two numbers
                nums = re.findall(r'\d+(?:\.\d+)?', score_res)
                if len(nums) >= 2:
                    x = float(nums[0])
                    y = float(nums[1])
                    map_data.append({"title": card.get("title"), "x": x, "y": y})
            except:
                pass
        
        if not map_data:
            return "Failed to score cards."

        # 3. Plot
        return self._plot_data(map_data, axes)

    def _plot_data(self, data, axes):
        print("Plotting map...")
        try:
            # Setup Font for Japanese
            plt.rcParams['font.family'] = 'MS Gothic' 
            
            plt.figure(figsize=(10, 8))
            
            xs = [d['x'] for d in data]
            ys = [d['y'] for d in data]
            labels = [d['title'] for d in data]
            
            plt.scatter(xs, ys, color='skyblue', s=100, alpha=0.7, edgecolors='blue')
            
            for i, label in enumerate(labels):
                plt.annotate(label, (xs[i], ys[i]), xytext=(5, 5), textcoords='offset points')
                
            plt.title(f"Vector Map: {axes['x_axis']} vs {axes['y_axis']}")
            plt.xlabel(f"{axes['x_axis']} ({axes['x_min']} -> {axes['x_max']})")
            plt.ylabel(f"{axes['y_axis']} ({axes['y_min']} -> {axes['y_max']})")
            plt.grid(True, linestyle='--', alpha=0.6)
            plt.xlim(0, 10.5)
            plt.ylim(0, 10.5)
            
            # Save
            filename = f"Map_{axes['x_axis']}_{axes['y_axis']}.png".replace(" ", "_")
            save_path = os.path.join(self.output_dir, filename)
            plt.savefig(save_path)
            plt.close()
            
            print(f"Map saved to: {save_path}")
            
            # Open the image automatically
            import subprocess
            subprocess.Popen(['start', save_path], shell=True)
            
            return f"Map created: {save_path}\nAxes: {axes['x_axis']} vs {axes['y_axis']}"
            
        except Exception as e:
            return f"Plotting failed: {e}"

if __name__ == "__main__":
    # Test
    # Mock researcher for standalone test? No, requires real keys.
    print("Mapper module needs Orchestrator.")
