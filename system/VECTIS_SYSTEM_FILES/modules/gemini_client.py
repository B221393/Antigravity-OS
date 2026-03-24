"""
VECTIS Gemini Client - Unified API wrapper for google.genai SDK
This version assumes a clean environment where genai.configure() works as expected.
"""
import os
import warnings
import time
import random
from dotenv import load_dotenv

# Load environment from the project root .env file
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Module-level state
_SDK_AVAILABLE = False
_GENAI_SDK = None
_GOOGLE_EXCEPTIONS = None

# --- Initialization ---
try:
    import google.genai as genai
    from google.api_core import exceptions as google_exceptions

    _GENAI_SDK = genai
    _GOOGLE_EXCEPTIONS = google_exceptions

    if GEMINI_API_KEY:
        genai.configure(api_key=GEMINI_API_KEY)
        _SDK_AVAILABLE = True
        print("GEMINI_CLIENT: SDK configured successfully.")
    else:
        warnings.warn("GEMINI_CLIENT: GEMINI_API_KEY not found in .env file.", RuntimeWarning)

except ImportError:
    warnings.warn(
        "GEMINI_CLIENT: The 'google.genai' package is not installed.",
        ImportWarning
    )
except Exception as e:
    warnings.warn(f"GEMINI_CLIENT: Failed to configure Gemini API: {e}", RuntimeWarning)


def generate_content(prompt: str, model_name: str = "gemini-1.5-flash-latest", use_search: bool = False) -> str:
    """
    Unified content generation function with robust retry and fallback logic.
    """
    if not _SDK_AVAILABLE:
        return "ERROR: Gemini SDK not available or configured."

    max_retries = 5
    base_wait_time = 5
    # Prioritize the stable 'gemini-pro' and use the requested model as a fallback
    model_candidates = list(dict.fromkeys(["gemini-pro", model_name]))
    last_error = "No error recorded."

    for model_to_try in model_candidates:
        print(f"🧠 Attempting to use Gemini model: {model_to_try}")
        for attempt in range(max_retries):
            try:
                model = _GENAI_SDK.GenerativeModel(model_to_try)
                response = model.generate_content(prompt)
                print(f"✅ Gemini ({model_to_try}) generated content successfully.")
                return response.text

            except _GOOGLE_EXCEPTIONS.ResourceExhausted as e:
                wait_time = base_wait_time * (2 ** attempt) + random.uniform(0, 1)
                last_error = e
                print(f"⚠️ Gemini Rate Limit (429). Attempt {attempt + 1}/{max_retries}. Retrying in {wait_time:.2f}s...")
                time.sleep(wait_time)
                continue

            except (_GOOGLE_EXCEPTIONS.NotFound, ValueError) as e:
                last_error = e
                print(f"❌ Gemini Model Not Found or Invalid ('{model_to_try}'): {e}. Trying next model...")
                break

            except Exception as e:
                last_error = e
                print(f"❌ An unexpected error occurred with model '{model_to_try}': {e}")
                break
        
    final_error_message = f"ERROR: Gemini API call failed for all candidate models. Last error: {last_error}"
    print(final_error_message)
    return final_error_message


class GenerativeModel:
    """
    Compatibility wrapper for legacy code.
    """
    def __init__(self, model_name: str = "gemini-1.5-flash-latest"):
        self.model_name = model_name
    
    def generate_content(self, prompt: str, use_search: bool = False):
        text = generate_content(prompt, self.model_name, use_search=use_search)
        return _ResponseWrapper(text)


class _ResponseWrapper:
    """
    Mimics the `.text` property of the old SDK's response object.
    """
    def __init__(self, text: str):
        self.text = text

def configure(api_key: str = None):
    """ No-op for old code. """
    pass
