
from typing import List, Dict, Any
import random

class MockApp:
    """
    A simulated GUI application (SNS 'Twutter') with intentional UX defects.
    """
    def __init__(self):
        self.current_screen = "login"
        self.is_logged_in = False
        self.dark_mode = False

    def get_state(self) -> Dict[str, Any]:
        """Returns the current UI tree (DOM-like structure)."""
        if self.current_screen == "login":
            return {
                "screen_id": "login",
                "title": "Welcome to Twutter",
                "elements": [
                    {"id": "input_user", "type": "input", "label": "User Name (Min 8 chars, 1 symbol)", "value": ""},
                    {"id": "input_pass", "type": "input", "label": "Password", "value": "admin123", "is_masked": False}, # DEFECT: Password visible
                    {"id": "btn_login", "type": "button", "text": "Go", "color": "#cccccc", "size": "small"}, # DEFECT: Small, low contrast
                    {"id": "btn_cancel", "type": "button", "text": "Cancel", "color": "#ff0000", "size": "large"}, # DEFECT: Cancel is prominent
                    {"id": "link_forgot", "type": "link", "text": "Forgot?", "size": "tiny"}
                ]
            }
        elif self.current_screen == "home":
             return {
                "screen_id": "home",
                "title": "Home Feed",
                "elements": [
                    {"id": "btn_menu", "type": "icon", "icon": "hamburger", "alt": "Menu"}, # DEFECT: Confusing icon for some
                    {"id": "btn_settings", "type": "button", "text": "Settings", "position": "top-right"},
                    {"id": "feed_list", "type": "list", "items": ["User A: Hello", "User B: Buy Crypto"]},
                    {"id": "btn_post", "type": "button", "text": "New Tweet", "position": "top-left"}, # DEFECT: Hard to reach
                    {"id": "ad_banner", "type": "image", "src": "ad.jpg", "size": "fullscreen"} # DEFECT: Intrusive ad
                ]
            }
        elif self.current_screen == "settings":
            return {
                "screen_id": "settings",
                "title": "Settings",
                "elements": [
                    {"id": "text_title", "type": "text", "label": "Settings"},
                    {"id": "toggle_dark_mode", "type": "toggle", "label": "Dark Mode (Beta)", "value": self.dark_mode},
                    {"id": "btn_back", "type": "button", "label": "Back"}
                ]
            }
        return {}

    def interact(self, action: str, element_id: str, value: str = None) -> str:
        """Simulates user interaction. Returns feedback string."""
        if self.current_screen == "login":
            if element_id == "btn_login":
                # DEFECT: Annoying validation
                if random.random() < 0.3:
                    error_log = """
[ERROR] Tb_UserValidationException: 503 Service Unavailable
   at com.twutter.auth.AuthService.login(AuthService.java:404)
   at com.twutter.ui.LoginFragment.onClick(LoginFragment.java:99)
   ... core dumped.
"""
                    print(f"\033[91m{error_log}\033[0m") # Red text
                    return "Error 503: Internal Server Error (See console)" 
                
                self.is_logged_in = True
                self.current_screen = "home"
                return "Login Successful. Redirecting..."
            
            elif element_id == "btn_cancel":
                return "App Closed."
            
            elif element_id == "input_pass":
                return f"Typed password: {value}"
            
        elif self.current_screen == "home":
             if element_id == "btn_post":
                 print("\033[93m[WARN] MainThread blocked for 2000ms due to heavy asset loading.\033[0m")
                 return "Opened Post Modal (Slow loading...)"
             if element_id == "btn_menu":
                 return "Menu opened."
             if element_id == "btn_settings":
                 self.current_screen = "settings"
                 return "Navigated to Settings."
                 
        elif self.current_screen == "settings":
            if element_id == "toggle_dark_mode":
                # DEFECT: Does nothing visually
                self.dark_mode = not self.dark_mode
                return f"Dark Mode toggled to {self.dark_mode} (But no visual change happened!)"
            if element_id == "btn_back":
                self.current_screen = "home"
                return "Back to Home."

        return "Action ignored."
