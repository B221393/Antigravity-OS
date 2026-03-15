"""
VECTIS OS - Keyboard Layout Manager
===================================
大西配列(Onishi Layout)とQWERTY切り替え

Features:
- 大西配列 ⇔ QWERTY の切り替え
- 設定の永続化
- アプリケーション全体で共有
"""

import json
import os
from pathlib import Path
from typing import Dict, Optional

class KeyboardLayoutManager:
    """キーボードレイアウト管理クラス"""
    
    # 大西配列 o24 正式マッピング
    ONISHI_LAYOUT = {
        # Lower case
        'q': 'q', 'w': 'l', 'e': 'u', 'r': ',', 't': '.',
        'y': 'f', 'u': 'w', 'i': 'r', 'o': 'y', 'p': 'p',
        'a': 'e', 's': 'i', 'd': 'a', 'f': 'o', 'g': '-',
        'h': 'k', 'j': 't', 'k': 'n', 'l': 's', ';': 'h',
        'z': 'z', 'x': 'x', 'c': 'c', 'v': 'v', 'b': ';',
        'n': 'g', 'm': 'd', ',': 'm', '.': 'j', '/': 'b',
        # Upper case
        'Q': 'Q', 'W': 'L', 'E': 'U', 'R': '<', 'T': '>',
        'Y': 'F', 'U': 'W', 'I': 'R', 'O': 'Y', 'P': 'P',
        'A': 'E', 'S': 'I', 'D': 'A', 'F': 'O', 'G': '_',
        'H': 'K', 'J': 'T', 'K': 'N', 'L': 'S', ' :': 'H',
        'Z': 'Z', 'X': 'X', 'C': 'C', 'V': 'V', 'B': ':',
        'N': 'G', 'M': 'D', '<': 'M', '>': 'J', '?': 'B',
    }
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize layout manager
        
        Postcondition: self.current_layout is loaded from config
        """
        if config_path is None:
            base_dir = Path(__file__).parent.parent
            config_path = base_dir / "config" / "llm_config.json"
        
        self.config_path = Path(config_path)
        self.current_layout = self._load_layout()
    
    def _load_layout(self) -> str:
        """
        Load keyboard layout from config
        
        Returns: "onishi" or "qwerty"
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            layout = config.get("features", {}).get("keyboard_layout", "qwerty")
            return layout
        except (FileNotFoundError, json.JSONDecodeError):
            return "qwerty"
    
    def _save_layout(self, layout: str):
        """
        Save keyboard layout to config
        
        Precondition: layout is either "onishi" or "qwerty"
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            config = {"features": {}}
        
        if "features" not in config:
            config["features"] = {}
        
        config["features"]["keyboard_layout"] = layout
        
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def toggle_layout(self) -> str:
        """
        Toggle between Onishi and QWERTY layouts
        
        Returns: New layout name
        """
        new_layout = "qwerty" if self.current_layout == "onishi" else "onishi"
        self.current_layout = new_layout
        self._save_layout(new_layout)
        return new_layout
    
    def set_layout(self, layout: str):
        """
        Set specific layout
        
        Precondition: layout is either "onishi" or "qwerty"
        """
        if layout not in ["onishi", "qwerty"]:
            raise ValueError(f"Invalid layout: {layout}. Must be 'onishi' or 'qwerty'")
        
        self.current_layout = layout
        self._save_layout(layout)
    
    def get_current_layout(self) -> str:
        """Get current layout name"""
        return self.current_layout
    
    def is_onishi_active(self) -> bool:
        """Check if Onishi layout is active"""
        return self.current_layout == "onishi"
    
    def convert_text(self, text: str, to_layout: Optional[str] = None) -> str:
        """
        Convert text based on keyboard layout
        
        Args:
            text: Input text
            to_layout: Target layout ("onishi" or "qwerty"). If None, use current layout
            
        Returns: Converted text
        
        Reasoning: Allows input conversion for Onishi layout users
        """
        if to_layout is None:
            to_layout = self.current_layout
        
        if to_layout == "qwerty":
            return text  # No conversion needed
        
        # Convert to Onishi
        result = []
        for char in text:
            if char in self.ONISHI_LAYOUT:
                result.append(self.ONISHI_LAYOUT[char])
            else:
                result.append(char)
        
        return ''.join(result)
    
    def get_layout_info(self) -> Dict[str, str]:
        """Get current layout information"""
        return {
            "current_layout": self.current_layout,
            "is_onishi": str(self.is_onishi_active()),
            "mapping_size": str(len(self.ONISHI_LAYOUT)) if self.is_onishi_active() else "N/A"
        }


# === CONVENIENCE FUNCTIONS ===

_global_layout_manager = None

def get_layout_manager() -> KeyboardLayoutManager:
    """
    Get global keyboard layout manager instance (singleton)
    
    Usage:
        manager = get_layout_manager()
        manager.toggle_layout()
    """
    global _global_layout_manager
    if _global_layout_manager is None:
        _global_layout_manager = KeyboardLayoutManager()
    return _global_layout_manager


def toggle_keyboard_layout() -> str:
    """
    Quick toggle function
    
    Returns: New layout name
    """
    manager = get_layout_manager()
    new_layout = manager.toggle_layout()
    print(f"🎹 Keyboard layout switched to: {new_layout.upper()}")
    return new_layout


# === TESTING ===

if __name__ == "__main__":
    print("=" * 60)
    print("VECTIS OS - Keyboard Layout Manager Test")
    print("=" * 60)
    
    manager = KeyboardLayoutManager()
    
    # Show current layout
    info = manager.get_layout_info()
    print(f"\n📋 Current Layout: {info['current_layout'].upper()}")
    print(f"   Is Onishi: {info['is_onishi']}")
    
    # Toggle test
    print(f"\n🔄 Toggling layout...")
    new_layout = manager.toggle_layout()
    print(f"   New layout: {new_layout.upper()}")
    
    # Test conversion
    if manager.is_onishi_active():
        test_text = "hello"
        converted = manager.convert_text(test_text)
        print(f"\n🧪 Conversion test:")
        print(f"   Input (QWERTY): {test_text}")
        print(f"   Output (Onishi): {converted}")
    
    # Toggle back
    manager.toggle_layout()
    print(f"\n↩️ Toggled back to: {manager.get_current_layout().upper()}")
    
    print("\n" + "=" * 60)
