import json
import random
import time
import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Setup path
sys.path.insert(0, str(Path(__file__).parents[2].absolute()))

# Load Env for Gemini
load_dotenv(Path(__file__).parents[2] / ".env")

# Use unified Gemini client
from modules.gemini_client import GenerativeModel

class EgoSimulator:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_path = self.base_dir / "data" / "self_model.json"
        self.load_model()
        
    def load_model(self):
        if self.data_path.exists():
            with open(self.data_path, 'r', encoding='utf-8') as f:
                self.model = json.load(f)
        else:
            self.model = {}
            
    def save_model(self):
        with open(self.data_path, 'w', encoding='utf-8') as f:
            json.dump(self.model, f, indent=2, ensure_ascii=False)

    def _get_ego_prompt(self):
        vectors = self.model.get("ego_vectors", {})
        identity = self.model.get("identity", {})
        
        prompt = f"""
        You are the 'Ego Core' of {identity.get('name')}.
        Your archetype is: {identity.get('archetype')}.
        Your core values are: {', '.join(identity.get('core_values', []))}.
        
        Your internal 'Ego Vectors' (0.0 - 1.0) are:
        {json.dumps(vectors, indent=2)}
        
        Act as this persona. You are autonomous, rigorous, and constantly seeking evolution.
        Analyze choices not just by 'efficiency', but by how well they align with your High Novelty/Revolutionary nature.
        """
        return prompt

    def evaluate_action_llm(self, action_description):
        model = GenerativeModel('gemini-2.0-flash-exp')
        prompt = self._get_ego_prompt() + f"""
        
        Task: Evaluate the following action: "{action_description}"
        
        1. Assign a 'resonance_score' (0-100) based on how much this action aligns with my values.
        2. Provide a short, 1-sentence 'internal_monologue' justifying the score.
        
        Return JSON format: {{"score": int, "monologue": "string"}}
        """
        
        try:
            response = model.generate_content(prompt)
            txt = response.text.replace("```json", "").replace("```", "")
            data = json.loads(txt)
            return data.get("score", 50), data.get("monologue", "Analysis complete.")
        except Exception as e:
            return 50, f"Neural Error: {e}"

    def run_deep_reflection(self, current_context="General state"):
        model = GenerativeModel('gemini-2.0-flash-exp')
        
        moves = [
            "Deep Dive: Rust Optimization for Speed",
            "Creative Burst: Refine EGO UI Aesthetics",
            "Strange Loop: Study English via Recursive Self-Dialogue",
            "Focus Mode: Kodansha Entry Sheet Strategy",
            "System Maintenance: Refactor Codebase"
        ]
        
        prompt = self._get_ego_prompt() + f"""
        
        Current Situation: {current_context}
        Candidate Moves: {json.dumps(moves)}
        
        Perform a 'Shogi-style' deep search on these moves.
        1. Select the Best Move that maximizes my 'Revolutionary Potential'.
        2. Simulate the outcome.
        3. Explain WHY this is the best move for my evolution.
        
        Return JSON: {{"best_move": "string", "score": int, "reasoning": "string"}}
        """
        
        try:
            response = model.generate_content(prompt)
            txt = response.text.replace("```json", "").replace("```", "")
            data = json.loads(txt)
            
            # Save decision
            if 'decision_history' not in self.model:
                self.model['decision_history'] = []
            self.model['decision_history'].append({
                "timestamp": datetime.now().isoformat(),
                "decision": data,
                "context": current_context
            })
            self.save_model()
            
            return {
                "path": [data.get("best_move")],
                "score": data.get("score"),
                "thought": data.get("reasoning")
            }
        except Exception as e:
            return {"path": ["error_fallback"], "score": 0, "thought": str(e)}

    def train_from_memories(self, memory_text):
        """
        Ingests raw experiences/favorites and performs 'Deep Learning' on the Self Model.
        """
        model = GenerativeModel('gemini-2.0-flash-exp')
        
        current_identity = self.model.get("identity", {})
        current_vectors = self.model.get("ego_vectors", {})
        
        prompt = f"""
        You are the 'Meta-Cognition' module for {current_identity.get('name')}.
        
        Task: Analyze the user's "Interest Data & Narrative Profile" to refine their Self-Model.
        The input contains both a list of contents and a deep PERSONAL NARRATIVE (Chapters 1-5).
        
        [INPUT DATA]
        {memory_text}
        
        [CURRENT SELF MODEL]
        Archetype: {current_identity.get('archetype')}
        Vectors: {json.dumps(current_vectors)}
        
        [ANALYSIS REQUIRED]
        1. **Deep Narrative Extraction**: Identify the "Core Kernel" (e.g., loss of friend, control vs chaos).
        2. **Vector Alignment**: How do "Horse Riding (Physicality)" and "Shogi AI (Logic)" coexist? Adjust vectors to reflect this duality (e.g., High Logical AND High Physical/Emotional).
        3. **Archetype Evolution**: Propose a new Archetype Name that fuses "Narrative Healer" and "System Hacker".
        
        Return JSON:
        {{
            "analysis_summary": "A deep, psycho-analytical summary of the user's duality (Death/Logic, Horse/Code).",
            "vector_updates": {{ "existing_or_new_vector_name": float_value_0_to_1, ... }},
            "new_core_values": ["value1", "value2", ...],
            "refined_archetype": "string",
            "narrative_kernel": "A short summary of the 'Origin Story' for the AI to remember."
        }}
        """
        
        try:
            time.sleep(2) # Simulate thinking
            
            response = model.generate_content(prompt)
            txt = response.text.replace("```json", "").replace("```", "")
            data = json.loads(txt)
            
            # Apply Updates with Safety Checks
            if "vector_updates" in data:
                if "ego_vectors" not in self.model:
                    self.model["ego_vectors"] = {}
                for k, v in data["vector_updates"].items():
                    self.model["ego_vectors"][k] = v
                    
            if "new_core_values" in data:
                if "identity" not in self.model:
                    self.model["identity"] = {}
                self.model["identity"]["core_values"] = data["new_core_values"]
                
            if "refined_archetype" in data:
                if "identity" not in self.model:
                    self.model["identity"] = {}
                self.model["identity"]["archetype"] = data["refined_archetype"]
                
            # Store the Narrative Kernel specifically
            if "narrative_kernel" in data:
                if "identity" not in self.model:
                    self.model["identity"] = {}
                self.model["identity"]["origin_kernel"] = data["narrative_kernel"]

            # Log Training
            if "training_history" not in self.model:
                self.model["training_history"] = []
                
            self.model["training_history"].append({
                "timestamp": datetime.now().isoformat(),
                "input_sample": "Detailed Self-Analysis Profile (2025)",
                "analysis": data.get("analysis_summary"),
                "vectors_snapshot": self.model["ego_vectors"].copy()
            })
            
            self.save_model()
            return data
            
        except Exception as e:
            return {"status": "error", "message": f"Training Failed: {e}"}

if __name__ == "__main__":
    sim = EgoSimulator()
    print("Engine Ready.")
