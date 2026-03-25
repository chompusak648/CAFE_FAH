import os
from dotenv import load_dotenv
from google import genai

load_dotenv(override=True)
api_key = os.getenv("GEMINI_API_KEY")

try:
    client = genai.Client(api_key=api_key)
    models = client.models.list()
    with open("available_models.txt", "w", encoding="utf-8") as f:
        for m in models:
            f.write(f"{m.name}\n")
    print("Successfully wrote available_models.txt")
except Exception as e:
    with open("available_models.txt", "w", encoding="utf-8") as f:
        f.write(f"Error: {str(e)}")
    print(f"Error occurred: {e}")
