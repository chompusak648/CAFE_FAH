import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv(override=False)

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://app:app@localhost:5432/ragdb")
EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-004")
CHAT_MODEL = os.getenv("CHAT_MODEL", "gemini-2.5-flash")
EMBED_DIM = int(os.getenv("EMBED_DIM", 768))
ALLOWED_ORIGINS = [
    origin.strip()
    for origin in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:5173,http://localhost:5174,http://127.0.0.1:5173,http://127.0.0.1:5174",
    ).split(",")
    if origin.strip()
]

print(f"DEBUG: Initializing with CHAT_MODEL = {CHAT_MODEL}")

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# AI Utilities
client = genai.Client(api_key=GEMINI_API_KEY)

# Use gemini-1.5-flash and others as fallbacks
FALLBACK_MODELS = [
    CHAT_MODEL,
    "gemini-2.5-flash",
    "gemini-1.5-flash",
    "gemini-2.0-flash",
    
]
# Remove duplicates while preserving order
FALLBACK_MODELS = list(dict.fromkeys(FALLBACK_MODELS))

def generate_with_fallback(prompt: str = None, contents=None, config=None):
    """Generates content with automatic model fallback and retry logic for 429 errors."""
    last_err = None
    # Deduplicate while preserving order
    models_to_try = []
    for m in FALLBACK_MODELS:
        if m and m not in models_to_try:
            models_to_try.append(m)
            
    for model_name in models_to_try:
        retries = 2
        while retries >= 0:
            try:
                # Support both simple prompt and full contents
                input_contents = contents if contents is not None else prompt
                response = client.models.generate_content(
                    model=model_name,
                    contents=input_contents,
                    config=config
                )
                return response
            except Exception as e:
                err_str = str(e).lower()
                print(f"Generation attempt with {model_name} failed: {err_str}")
                
                if "429" in err_str or "resource_exhausted" in err_str or "quota" in err_str:
                    print(f"Quota hit for {model_name}, retrying... ({retries} retries left)")
                    retries -= 1
                    time.sleep(2)
                    last_err = e
                    continue
                else:
                    # For non-quota errors (like 404), switch to next model immediately
                    print(f"Non-quota error with {model_name}: {e}")
                    last_err = e
                    break 
    raise last_err if last_err else Exception("Generation failed with all fallback models.")
