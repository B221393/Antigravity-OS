import os
import sys
import re
import difflib

# Import UnifiedLLM (Phi-4)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../")))
from EGO_SYSTEM_FILES.modules.unified_llm import UnifiedLLM

class VectisCoder:
    def __init__(self):
        # Switched to Gemini (Flash) for "Coworker" level intelligence & speed
        self.llm = UnifiedLLM(provider="gemini", model_name="gemini-2.0-flash-exp")
        
    def request_edit(self, file_path, instruction):
        """
        Main entry point. Phi-4 analyzes the file and proposes a change.
        """
        if not os.path.exists(file_path):
            return f"[ERROR] File not found: {file_path}"
            
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            
        # 1. Ask Phi-4 for the code change
        prompt = f"""
        【ROLE: Expert Python/System Engineer】
        You are an autonomous coding agent.
        
        【TASK】
        The user wants to modify the following file: {os.path.basename(file_path)}
        Instruction: "{instruction}"
        
        【FILE CONTENT】
        {content}
        
        【OUTPUT FORMAT】
        You MUST return the modification in this STRICT format:
        
        <<<SEARCH>>>
        (The exact code block to be replaced. Must match the file content exactly.)
        <<<REPLACE>>>
        (The new code block to insert.)
        <<<END>>>
        
        Do not explain. Just provide the blocks.
        """
        
        print("...Thinking (Phi-4)...")
        response = self.llm.generate(prompt)
        
        # 2. Parse Response
        edits = self._parse_edits(response)
        if not edits:
            return f"[FAIL] Could not understand Phi-4's code proposal.\nRaw Output:\n{response}"
            
        # 3. Apply Edits Safely
        return self._apply_safe_edits(file_path, content, edits)

    def _parse_edits(self, text):
        """Extract SEARCH/REPLACE blocks."""
        pattern = r"<<<SEARCH>>>\n?(.*?)<<<REPLACE>>>\n?(.*?)<<<END>>>"
        matches = re.findall(pattern, text, re.DOTALL)
        return matches

    def _apply_safe_edits(self, file_path, original_content, edits):
        """
        Applies edits but COMMENTS OUT the old code instead of deleting it.
        """
        new_content = original_content
        applied_count = 0
        
        for search_block, replace_block in edits:
            search_block = search_block.strip()
            # replace_block = replace_block.strip() # Don't strip replacement fully to keep indent? 
            # Actually strip is safer for matching, but we need to be careful with indentation.
            
            if search_block not in new_content:
                # Try relaxed matching (ignore whitespace) or just skip
                print(f"[WARN] Could not find strict match for block:\n{search_block[:50]}...")
                continue
                
            # Create Safe Replacement (Commented Old + New)
            commented_old = "\n".join([f"# [OLD] {line}" for line in search_block.split('\n')])
            safe_block = f"""
# ================= [EGO AUTO-EDIT START] =================
{commented_old}
# ------------------------------------------------------------
{replace_block}
# ================= [EGO AUTO-EDIT END] ===================
"""
            # Perform Replacement
            new_content = new_content.replace(search_block, safe_block, 1)
            applied_count += 1
            
        if applied_count > 0:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            return f"[SUCCESS] Applied {applied_count} edits to {os.path.basename(file_path)}. Old code was commented out."
        else:
            return "[FAIL] No matching code blocks found to replace."

if __name__ == "__main__":
    # Test CLI
    if len(sys.argv) < 3:
        print("Usage: python agent.py <file_path> <instruction>")
    else:
        agent = VectisCoder()
        res = agent.request_edit(sys.argv[1], sys.argv[2])
        print(res)
