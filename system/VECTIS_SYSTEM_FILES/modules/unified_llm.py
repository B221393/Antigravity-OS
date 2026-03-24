
import os
import sys
import json
import traceback

# Import Gemini as the default (for now)
# In future, this module can be expanded to support Ollama, OpenAI, etc.
# without breaking the rest of VECTIS.

try:
    from modules.gemini_client import GenerativeModel
    _HAS_GEMINI = True
except ImportError:
    _HAS_GEMINI = False
    
class UnifiedLLM:
    """
    Unified Interface for VECTIS LLM operations.
    Currently wraps Gemini, but designed to be extensible.
    """
    def __init__(self, provider="ollama", model_name="llama3.2:latest"):
        self.provider = provider
        self.model_name = model_name
        
        # Load Config or Auto-Optimize
        self.ollama_model = "phi4" 
        self.keep_alive = 0 
        
        if self.provider == "ollama":
            self._auto_optmize_ollama()
            
        self.client = None # Initialize to avoid AttributeError
        
        if self.provider == "gemini":
            if _HAS_GEMINI:
                self.client = GenerativeModel(model_name)
            else:
                self.client = None
                print("⚠️ Gemini Client not available.")

    def _auto_optmize_ollama(self):
        """Standard VECTIS Feature: Auto-Optimize based on RAM."""
        try:
            # 1. Check RAM
            import subprocess, re
            cmd = "wmic OS get FreePhysicalMemory /Value"
            res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            mem_match = re.search(r"FreePhysicalMemory=(\d+)", res.stdout)
            free_mb = int(mem_match.group(1)) // 1024 if mem_match else 4000
            
            # 2. Check Installed Models (Quickly)
            res_models = subprocess.run(["ollama", "list"], capture_output=True, text=True, encoding='utf-8')
            installed_text = res_models.stdout
            
            # 3. Decision Logic
            # High End (> 12GB Free) -> Phi4 / Keep Loaded for speed
            if free_mb > 12000 and "phi4" in installed_text:
                self.ollama_model = "phi4"
                self.keep_alive = "10m"
                print(f"[VECTIS AUTO-OPT] High RAM ({free_mb}MB). Mode: POWER (Phi4, Keep-Alive).")
                
            # Mid Range (> 6GB Free) -> Llama3.2 / Immediate Unload
            elif free_mb > 6000:
                if "llama3.2" in installed_text: self.ollama_model = "llama3.2:latest"
                elif "phi4" in installed_text: self.ollama_model = "phi4"
                self.keep_alive = 0
                print(f"[VECTIS AUTO-OPT] Mid RAM ({free_mb}MB). Mode: BALANCED (Immediate Unload).")
                
            # Low End -> 1B Model / Immediate Unload
            else:
                if "llama3.2:1b" in installed_text: self.ollama_model = "llama3.2:1b"
                elif "llama3.2" in installed_text: self.ollama_model = "llama3.2:latest"
                elif "gemma:2b" in installed_text: self.ollama_model = "gemma:2b"
                self.keep_alive = 0
                print(f"[VECTIS AUTO-OPT] Low RAM ({free_mb}MB). Mode: ECO ({self.ollama_model}).")
                
        except Exception as e:
            print(f"[VECTIS AUTO-OPT] Detection failed: {e}. Using Default.")


    def generate(self, prompt, provider=None, use_search=False, **kwargs):
        """
        Unified generation method.
        """
        active_provider = provider if provider else self.provider
        
        # 1. Search Phase (if requested)
        search_context = ""
        if use_search and active_provider != "gemini":
            # We use DuckDuckGo (local tool) to provide context for non-native providers (like Ollama).
            search_context = self.perform_web_search(prompt)

        # 2. Generation Phase
        if active_provider == "gemini":
            # Check for model switch
            if getattr(self, 'client', None):
                 current_client_model = getattr(self.client, 'model_name', None)
                 if current_client_model and current_client_model != self.model_name:
                     self.client = None # Force re-init

            # Lazy Init / Re-init checks
            if not getattr(self, 'client', None):
                if _HAS_GEMINI:
                    try:
                        self.client = GenerativeModel(self.model_name)
                    except Exception as e:
                        return f"[Gemini Init Error] {str(e)}"
                else:
                    return "[Gemini Error] Client library not imported."

        # Inject Search Context if available
        final_prompt = prompt
        if search_context:
            final_prompt = f"[CONTEXT]\n{search_context}\n\n[QUERY]\n{prompt}"

        # Truncate for Ollama (Stricter Safety: 6000 chars)
        max_ollama_chars = 6000
        if len(final_prompt) > max_ollama_chars:
            print(f"[UnifiedLLM] ⚠️ Ollama Input truncated ({len(final_prompt)} -> {max_ollama_chars} chars) for safety.")
            final_prompt = final_prompt[:max_ollama_chars] + "\n...(truncated)..."

        # STRATEGY: Cloud First (RAM Saving) -> Local Fallback
        
        # 1. Try Cohere (Fastest Cloud Text Gen)
        try:
             cohere_res = self._generate_cohere(final_prompt)
             if cohere_res and not cohere_res.startswith("[Cohere Error]"):
                 return cohere_res
        except Exception:
             pass

        # 2. Try Gemini (High Quality Cloud)
        if _HAS_GEMINI:
            # Lazy Init / Re-init checks for Gemini
            # Fix: If provider is NOT gemini (e.g. ollama), force a valid Gemini model name for fallback
            target_gemini_model = self.model_name if self.provider == "gemini" else "gemini-1.5-flash"
            
            current_client = getattr(self, 'client', None)
            current_model = getattr(current_client, 'model_name', None) if current_client else None

            if not current_client or current_model != target_gemini_model:
                try:
                    self.client = GenerativeModel(target_gemini_model)
                except Exception as e:
                    print(f"[Gemini Init Error] {str(e)}")
                    self.client = None # Ensure client is None if init fails
            
            if self.client:
                # Simple Retry Logic for 429 (Rate Limit)
                import time
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        res = self.client.generate_content(final_prompt, use_search=use_search)
                        res_text = res.text

                        # CRITICAL FIX: Handle error strings returned from the client
                        if isinstance(res_text, str) and res_text.strip().startswith("ERROR:"):
                            print(f"[UnifiedLLM] ⚠️ Upstream Gemini client error: {res_text.strip()}")
                            # Break the loop to trigger fallback to Ollama
                            break
                        
                        return res_text
                    except Exception as e:
                        if "429" in str(e):
                            if attempt < max_retries - 1:
                                wait_time = (attempt + 1) * 20
                                print(f"[Gemini] レート制限(429)待機中... ({wait_time}s)")
                                time.sleep(wait_time)
                                continue
                        print(f"[UnifiedLLM] ⚠️ Gemini Error: {e}.")
                        break # Break out of retry loop if other error or retries exhausted
        
        # 3. Fallback to Ollama (Local, ECO Mode)
        print(f"[UnifiedLLM] Cloud APIs failed. Falling back to local Ollama ({self.ollama_model})...")
        return self._generate_ollama(final_prompt)

    def perform_web_search(self, query):
        """
        Uses DuckDuckGo to search the web and returns raw results.
        Independent of Gemini (Google).
        """
        try:
            from duckduckgo_search import DDGS
        except ImportError:
            return "[Error] duckduckgo-search library not installed. Run: pip install duckduckgo-search"

        try:
            # Synchronous search
            results = []
            # ddgs.text() returns an iterator
            with DDGS() as ddgs:
                ddgs_gen = ddgs.text(query, max_results=5)
                if ddgs_gen:
                    for r in ddgs_gen:
                        title = r.get('title', 'No Title')
                        href = r.get('href', '#')
                        body = r.get('body', '')
                        results.append(f"Title: {title}\nURL: {href}\nSnippet: {body}\n")
            
            if not results:
                return "No search results found."
            
            return "\n---\n".join(results)

        except Exception as e:
            print(f"[Search Error] {e}")
            return f"[Search Error] {str(e)}"

    def _generate_ollama(self, prompt):
        import urllib.request
        import json

        # Introduce a fallback list for Ollama models
        model_candidates = list(dict.fromkeys([self.ollama_model, "gemma:2b", "llama3"]))
        
        for model in model_candidates:
            print(f"[UnifiedLLM] Attempting local generation with Ollama model: {model}...")
            url = "http://localhost:11434/api/generate"
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                "keep_alive": self.keep_alive,
                "options": {
                    "num_ctx": 4096
                }
            }
            try:
                req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
                with urllib.request.urlopen(req, timeout=45) as response: # Added timeout
                    result = json.loads(response.read().decode('utf-8'))
                    # On success, return the response
                    return result.get('response', '')
            except urllib.error.HTTPError as e:
                if e.code == 404:
                    print(f"[UnifiedLLM] ⚠️ Ollama model '{model}' not found (404). Trying next model...")
                    continue # Try the next model in the list
                else:
                    print(f"[UnifiedLLM] ⚠️ Ollama HTTP Error: {e}. Trying next provider...")
                    break # Break to try Cohere/Gemini
            except Exception as e:
                print(f"[UnifiedLLM] ⚠️ Ollama general error: {e}. Trying next provider...")
                break # Break to try Cohere/Gemini

        # If all Ollama models fail, proceed with the original cloud fallback chain
        print(f"[UnifiedLLM] ⚠️ All local Ollama models failed. Trying cloud fallbacks...")
        cohere_result = self._generate_cohere(prompt)
        if cohere_result and not cohere_result.startswith("[Cohere Error]"):
            return cohere_result
        
        if _HAS_GEMINI and self.client:
            print("[UnifiedLLM] Cohere failed. Trying Gemini...")
            try:
                res = self.client.generate_content(prompt)
                if isinstance(res.text, str) and not res.text.strip().startswith("ERROR:"):
                    return res.text
            except Exception as ge:
                print(f"[UnifiedLLM] Gemini also failed: {ge}")
        
        return f"[LLM Error] All local and cloud providers failed."

    def _generate_cohere(self, prompt):
        """Generate using Cohere API."""
        import urllib.request
        import json
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))
        
        api_key = os.getenv("COHERE_API_KEY")
        if not api_key:
            return "[Cohere Error] API key not configured."
        
        url = "https://api.cohere.com/v1/chat"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        # Truncate for Cohere
        max_chars = 4000
        if len(prompt) > max_chars:
            prompt = prompt[:max_chars] + "...(truncated)"
        
        data = {
            "model": "command", # Standard model
            "message": prompt,
            "temperature": 0.7
        }
        
        try:
            req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
            with urllib.request.urlopen(req, timeout=30) as response:
                result = json.loads(response.read().decode('utf-8'))
                return result.get('text', '')
        except Exception as e:
            print(f"[Cohere Error] {e}")
            return f"[Cohere Error] {e}"

    def generate_debate(self, topic_content):
        """
        Runs a 'Wall-Bash' debate between Gemini (Architect) and Ollama (Critic).
        Returns a dialogue string.
        """
        # 1. Gemini (Architect) Perspective
        gemini_prompt = f"""
        【Role: VECTIS Architect (Gemini)】
        Analyze this content deeply and provide a high-level strategic insight (The Core Thesis).
        Keep it concise (3 lines).
        Content: {topic_content[:2000]}
        """
        architect_view = self.generate(gemini_prompt, provider="gemini")
        
        # 2. Ollama (Critic) Perspective
        ollama_prompt = f"""
        [Role: VECTIS Critic (Ollama)]
        You are debating the VECTIS Architect.
        The Architect said: "{architect_view}"
        
        Critique this view. Find flaws, alternative angles, or practical hurdles.
        Be sharp and cynical. (Keep it short).
        """
        critic_view = self._generate_ollama(ollama_prompt)
        
        # 3. Architect Rebuttal
        rebuttal_prompt = f"""
        The Critic (Ollama) attacked your thesis with: "{critic_view}"
        Provide a final synthesis that incorporates this critique into a stronger truth.
        """
        synthesis = self.generate(rebuttal_prompt, provider="gemini")
        
        return f"""
╭── 🏛️ ARCHITECT (Gemini) ──────────────────────────
{architect_view.strip()}

╭── ⚡ CRITIC (Ollama) ─────────────────────────────
{critic_view.strip()}

╭── 💎 SYNTHESIS (Unified) ─────────────────────────
{synthesis.strip()}
"""


def create_llm_client():
    """Factory function to get the standard VECTIS LLM client."""
    return UnifiedLLM()
