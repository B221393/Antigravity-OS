
import os
import sys
import subprocess
import re
from datetime import datetime

class VectisRLM:
    """
    VECTIS Recursive Language Model (RLM) Lite Engine.
    
    Inspired by 'Recursive Language Models' (Zhang et al., 2025).
    Instead of loading entire files into context, this engine enables the LLM
    to write and execute Python scripts to process 'External Environments' (files).
    """
    def __init__(self, llm_client):
        self.llm = llm_client
        self.temp_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "../temp_rlm"))
        os.makedirs(self.temp_dir, exist_ok=True)

    def process_large_file(self, file_path, user_query, max_steps=3):
        """
        Main Loop for RLM.
        1. Analyzes user query.
        2. Generates Python code to inspect `file_path`.
        3. Executes code/grep to get partial results.
        4. Synthesizes answer or Loops.
        """
        if not os.path.exists(file_path):
            return f"[RLM Error] File not found: {file_path}"
            
        file_size = os.path.getsize(file_path)
        context_preview = self._read_head(file_path)
        
        history = []
        
        for step in range(max_steps):
            # 1. Prompt LLM to write code or answer
            prompt = f"""
[SYSTEM: RECURSIVE LANGUAGE MODEL ENGINE]
You are an intelligent agent capable of processing huge files by writing Python code.
You cannot see the whole file at once. You must use Python to read/search/filter it.

TARGET FILE: {file_path}
FILE SIZE: {file_size} bytes
HEAD PREVIEW: {context_preview}

USER QUERY: {user_query}

HISTORY OF ACTIONS:
{self._format_history(history)}

[INSTRUCTIONS]
- If you have enough info to answer, start your response with "ANSWER:".
- If you need more info, write a Python script block (```python ... ```) to read/process the file.
- You can use 'print()' in python to see results.
- Do NOT try to read the whole file. Read chunks, grep specific terms, or count lines.
            """
            
            response = self.llm.generate(prompt, provider="phi4") # Use fast local model
            
            # 2. Check for Answer
            if "ANSWER:" in response:
                return response.split("ANSWER:")[-1].strip()
                
            # 3. Extract and Execute Code
            code = self._extract_code(response)
            if code:
                output = self._execute_code(code, file_path)
                history.append({"action": "python_execution", "code": code, "output": output})
            else:
                # LLM didn't give code or answer? Fail safe.
                history.append({"action": "think", "content": response})
                
        return "[RLM] Limit reached. Last state: " + str(history[-1])

    def _read_head(self, path, lines=10):
        try:
            with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                return "".join([f.readline() for _ in range(lines)])
        except: return "(Unreadable)"

    def _extract_code(self, text):
        match = re.search(r"```python(.*?)```", text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    def _execute_code(self, code, file_path):
        """Executes the specialized python code safely."""
        # We need to make sure the script knows the file path
        # Inject variable 'TARGET_FILE'
        injected_code = f"TARGET_FILE = r'{file_path}'\n" + code
        
        script_path = os.path.join(self.temp_dir, f"script_{int(datetime.now().timestamp())}_{os.getpid()}.py")
        
        try:
            with open(script_path, "w", encoding="utf-8") as f:
                f.write(injected_code)
                
            res = subprocess.run([sys.executable, script_path], capture_output=True, text=True, timeout=10)
            return res.stdout + res.stderr
            
        except Exception as e:
            return str(e)
            
        finally:
            # METABOLIC CLEANUP: Remove waste product
            if os.path.exists(script_path):
                try:
                    os.remove(script_path)
                except: pass

    def _format_history(self, hist):
        out = ""
        for h in hist:
            if "code" in h:
                out += f"> Executed Code. Output:\n{h['output'][:500]}\n"
            if "content" in h:
                out += f"> Thought: {h['content'][:100]}\n"
        return out
