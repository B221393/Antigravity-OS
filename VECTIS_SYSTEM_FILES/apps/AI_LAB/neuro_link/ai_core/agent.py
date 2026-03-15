"""
EGO Neuro-Link: Agent Logic Core
================================
This module defines the "Brain" of the AI.
It uses Object-Oriented Programming (OOP) to define a standard interface.

Class Structure:
- BaseAgent: The abstract template for any AI.
- RuleBasedAgent: A simple AI that follows 'If-Then' logic (like Scratch).
"""

import random
import json
from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseAgent(ABC):
    """
    Abstract Base Class for all EGO Agents.
    Enforces that every agent MUST have a 'think' method.
    """
    def __init__(self, name: str):
        self.name = name
        print(f"🧠 [Agent System] Initialized agent: {self.name}")

    @abstractmethod
    def think(self, game_state: Dict[str, Any]) -> str:
        """
        Input: Game State (JSON dictionary)
        Output: Action Command (String: 'JUMP', 'LEFT', 'RIGHT', 'IDLE')
        """
        pass

class RuleBasedAgent(BaseAgent):
    """
    A concrete agent that uses explicit rules.
    Good for understanding "Scratch-like" logic in Python.
    """
    def think(self, game_state: Dict[str, Any]) -> str:
        # 1. Parse Perception (What do I see?)
        # Expecting state like: {"player_x": 50, "enemy_x": 60}
        px = game_state.get("player_x", 0)
        ex = game_state.get("enemy_x", 0)
        
        # 2. Logic Chain (The "Scratch" Blocks)
        # Rule 1: If close to enemy, Jump!
        distance = abs(px - ex)
        if distance < 20 and distance > 0:
            return "JUMP"
        
        # Rule 2: Randomly move to patrol
        if random.random() < 0.05:
            return random.choice(["LEFT", "RIGHT", "DASH"])
            
        return "IDLE"

class LLMAgent(BaseAgent):
    """
    Future expansion: AI that uses Gemini to decide actions.
    """
    def think(self, game_state: Dict[str, Any]) -> str:
        # Placeholder for Neuro-Link Phase 3
        return "IDLE"
