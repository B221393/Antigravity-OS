"""
VECTIS OS - Obsidian Daily Note Manager
=======================================
Obsidianスタイルの日付ベースメモ管理システム
"""

import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional

# Fix Windows console encoding
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

class ObsidianVault:
    """
    Obsidian Vault Manager
    
    Features:
    - Daily note creation with date-based folders
    - Template support
    - Auto-linking between notes
    - Markdown export
    """
    
    def __init__(self, vault_path: Optional[str] = None):
        """
        Initialize Obsidian vault
        
        Postcondition: Vault directory structure is created
        """
        if vault_path is None:
            base_dir = Path(__file__).parent.parent
            vault_path = base_dir / "obsidian_vault"
        
        self.vault_path = Path(vault_path)
        self.vault_path.mkdir(parents=True, exist_ok=True)
        
        # Create standard folders
        self._init_structure()
    
    def _init_structure(self):
        """
        Create standard Obsidian folder structure
        
        Reasoning: Organized structure improves note findability
        """
        folders = [
            "templates",
            "attachments",
            "archive"
        ]
        
        for folder in folders:
            (self.vault_path / folder).mkdir(exist_ok=True)
        
        # Create default template if not exists
        template_path = self.vault_path / "templates" / "daily.md"
        if not template_path.exists():
            self._create_default_template()
    
    def _create_default_template(self):
        """Create default daily note template"""
        template_content = """# {{date}}

## 🎯 Today's Goals
- [ ] 

## 📝 Notes


## 💡 Ideas


## 🔗 Links


---
Created: {{timestamp}}
Tags: #daily-note
"""
        template_path = self.vault_path / "templates" / "daily.md"
        with open(template_path, 'w', encoding='utf-8') as f:
            f.write(template_content)
    
    def create_daily_note(self, date: Optional[datetime] = None) -> Path:
        """
        Create daily note for specified date
        
        Args:
            date: Target date (default: today)
            
        Returns:
            Path to created note
            
        Precondition: Vault is initialized
        Postcondition: Daily note exists for the date
        Reasoning: Date-based organization matches Obsidian's daily note pattern
        """
        if date is None:
            date = datetime.now()
        
        # Create date folder: YYYY-MM-DD
        date_str = date.strftime("%Y-%m-%d")
        date_folder = self.vault_path / date_str
        date_folder.mkdir(exist_ok=True)
        
        # Create daily note
        note_path = date_folder / "daily.md"
        
        if not note_path.exists():
            # Load template
            template_path = self.vault_path / "templates" / "daily.md"
            if template_path.exists():
                with open(template_path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"# {date_str}\n\n"
            
            # Replace placeholders
            content = content.replace("{{date}}", date_str)
            content = content.replace("{{timestamp}}", datetime.now().isoformat())
            
            # Write note
            with open(note_path, 'w', encoding='utf-8') as f:
                f.write(content)
        
        return note_path
    
    def create_note(
        self, 
        title: str, 
        content: str = "", 
        date: Optional[datetime] = None,
        tags: list = None
    ) -> Path:
        """
        Create a new note
        
        Args:
            title: Note title
            content: Note content (markdown)
            date: Date to associate (default: today)
            tags: List of tags
            
        Returns:
            Path to created note
        """
        if date is None:
            date = datetime.now()
        
        date_str = date.strftime("%Y-%m-%d")
        date_folder = self.vault_path / date_str
        date_folder.mkdir(exist_ok=True)
        
        # Sanitize filename
        safe_title = "".join(c for c in title if c.isalnum() or c in (' ', '-', '_'))
        safe_title = safe_title.strip().replace(' ', '_')
        
        note_path = date_folder / f"{safe_title}.md"
        
        # Build content
        full_content = f"# {title}\n\n{content}\n\n---\n"
        full_content += f"Created: {datetime.now().isoformat()}\n"
        
        if tags:
            full_content += f"Tags: {' '.join(f'#{tag}' for tag in tags)}\n"
        
        with open(note_path, 'w', encoding='utf-8') as f:
            f.write(full_content)
        
        return note_path
    
    def get_recent_notes(self, days: int = 7) -> list:
        """
        Get notes from recent days
        
        Args:
            days: Number of days to look back
            
        Returns:
            List of note paths
        """
        notes = []
        today = datetime.now()
        
        for i in range(days):
            target_date = today - timedelta(days=i)
            date_str = target_date.strftime("%Y-%m-%d")
            date_folder = self.vault_path / date_str
            
            if date_folder.exists():
                for note_file in date_folder.glob("*.md"):
                    notes.append(note_file)
        
        return notes
    
    def search_notes(self, query: str) -> list:
        """
        Search notes by content
        
        Args:
            query: Search query
            
        Returns:
            List of matching note paths
        """
        matches = []
        
        for note_file in self.vault_path.rglob("*.md"):
            # Skip templates
            if "templates" in str(note_file):
                continue
            
            try:
                with open(note_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if query.lower() in content.lower():
                    matches.append(note_file)
            except:
                pass
        
        return matches
    
    def get_vault_stats(self) -> dict:
        """Get vault statistics"""
        total_notes = len(list(self.vault_path.rglob("*.md")))
        date_folders = len([d for d in self.vault_path.iterdir() if d.is_dir() and d.name.count('-') == 2])
        
        return {
            "total_notes": total_notes,
            "date_folders": date_folders,
            "vault_path": str(self.vault_path)
        }


# === CONVENIENCE FUNCTIONS ===

def quick_note(title: str, content: str = "", tags: list = None) -> Path:
    """
    Quickly create a note for today
    
    Usage:
        quick_note("Meeting Notes", "Discussed project timeline", tags=["work", "meeting"])
    """
    vault = ObsidianVault()
    return vault.create_note(title, content, tags=tags)


def today_note() -> Path:
    """
    Get or create today's daily note
    
    Usage:
        path = today_note()
        print(f"Daily note: {path}")
    """
    vault = ObsidianVault()
    return vault.create_daily_note()


# === TESTING ===

if __name__ == "__main__":
    print("=" * 60)
    print("VECTIS OS - Obsidian Vault Manager Test")
    print("=" * 60)
    
    vault = ObsidianVault()
    
    # Create today's note
    print("\n[1] Creating today's daily note...")
    daily = vault.create_daily_note()
    print(f"    Created: {daily}")
    
    # Create a custom note
    print("\n[2] Creating custom note...")
    note = vault.create_note(
        "Test Note",
        "This is a test note with some content.",
        tags=["test", "demo"]
    )
    print(f"    Created: {note}")
    
    # Get stats
    print("\n[3] Vault Statistics:")
    stats = vault.get_vault_stats()
    for key, value in stats.items():
        print(f"    {key}: {value}")
    
    # Recent notes
    print("\n[4] Recent notes (last 7 days):")
    recent = vault.get_recent_notes(7)
    for i, note_path in enumerate(recent[:5], 1):
        print(f"    {i}. {note_path.name} ({note_path.parent.name})")
    
    print("\n" + "=" * 60)
    print("✅ Vault setup complete!")
    print(f"📁 Location: {vault.vault_path}")
    print("=" * 60)
