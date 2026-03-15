
from typing import Dict, Any, List

class UXAgent:
    def __init__(self, persona: str):
        self.persona = persona
        self.internal_monologue = []

    def critique(self, state: Dict[str, Any]) -> str:
        """Analyzes the current screen state based on persona."""
        screen = state.get("screen_id", "unknown")
        elements = state.get("elements", [])
        
        critique = ""
        
        if self.persona == "GRANDMOTHER":
            critique = self._critique_grandma(elements)
        elif self.persona == "UI_DESIGNER":
            critique = self._critique_designer(elements)
        elif self.persona == "HACKER":
            critique = self._critique_hacker(elements)
        elif self.persona == "GEN_Z":
            critique = self._critique_gen_z(elements, state)
            
        self.internal_monologue.append(f"Thinking: {critique}")
        return critique

    def act(self, state: Dict[str, Any]) -> Dict[str, str]:
        """Decides next action based on state and persona."""
        elements = state.get("elements", [])
        screen = state.get("screen_id")
        
        # Simple heuristic logic for PoC
        if screen == "login":
            login_btn = next((e for e in elements if e["id"] == "btn_login"), None)
            
            if self.persona == "GRANDMOTHER":
                # Grandma gets confused by cancel button being prominent
                cancel_btn = next((e for e in elements if e["id"] == "btn_cancel"), None)
                if cancel_btn and cancel_btn.get("size") == "large":
                    return {"action": "tap", "target": "btn_cancel", "reason": "It was the biggest red button!"}
            
            if self.persona == "GEN_Z":
                 # Gen Z complains but eventually tries to login
                 pass 

            if login_btn:
                return {"action": "tap", "target": "btn_login", "reason": "Trying to log in..."}
        
        elif screen == "home":
             # Gen Z looks for settings (Dark Mode)
             if self.persona == "GEN_Z":
                 settings_btn = next((e for e in elements if e["id"] == "btn_settings"), None)
                 if settings_btn:
                     return {"action": "tap", "target": "btn_settings", "reason": "Looking for Dark Mode"}
        
        elif screen == "settings":
             if self.persona == "GEN_Z":
                 toggle = next((e for e in elements if e["id"] == "toggle_dark_mode"), None)
                 if toggle:
                     return {"action": "tap", "target": "toggle_dark_mode", "reason": "My eyes need this."}

        # Default: Random action or wait
        return {"action": "wait", "target": "none", "reason": "Don't know what to do."}

    def _critique_grandma(self, elements: List[Dict]) -> str:
        complaints = []
        for e in elements:
            if e.get("size") in ["small", "tiny"]:
                complaints.append(f"I can't see this '{e.get('text')}' text! It's too small!")
            if e.get("icon") == "hamburger":
                complaints.append("Why is there a hamburger here? I'm not hungry!")
            if "Input" in e.get("type", "") and "User Name" in e.get("label", ""):
                 complaints.append("User Name? Is that my real name or my email?")
        
        if not complaints: return "Everything looks nice deary."
        return " / ".join(complaints)

    def _critique_designer(self, elements: List[Dict]) -> str:
        issues = []
        for e in elements:
            if e.get("id") == "btn_login" and e.get("color") == "#cccccc":
                issues.append("Primary action 'Login' is greyed out/low contrast. Bad affordance.")
            if e.get("id") == "btn_cancel" and e.get("color") == "#ff0000":
                issues.append("Destructive action 'Cancel' is too prominent/scary.")
            if e.get("position") == "top-left" and e.get("id") == "btn_post":
                issues.append("Post button is in the 'Thumb Zone' blind spot (Top-Left).")
        
        if not issues: return "Aesthetically acceptable."
        return "DESIGN_FLAW: " + " | ".join(issues)

    def _critique_hacker(self, elements: List[Dict]) -> str:
        vulns = []
        for e in elements:
            if e.get("id") == "input_pass" and not e.get("is_masked", True):
                vulns.append("CRITICAL: Password field is NOT masked! Shoulder surfing risk.")
            if e.get("type") == "input":
                vulns.append(f"Testing SQL Injection on {e['id']}...")
        
        if not vulns: return "Secure... for now."
        return "SECURITY_ALERT: " + " | ".join(vulns)

    def _critique_gen_z(self, elements: List[Dict], state: Dict) -> str:
        complaints = []
        full_text = str(elements).lower()
        
        if "dark" not in full_text:
            complaints.append("No Dark Mode? My eyes are burning. 💀")
            
        if state.get("screen_id") == "login":
            complaints.append("Login takes too many clicks. Where is 'Sign in with Google'?")
            
        if "slow" in full_text or "loading" in full_text:
             complaints.append("This app is lagging. I'm deleting it.")
             
        if not complaints: return "Mid."
        return "GEN_Z_RAGE: " + " + ".join(complaints)
