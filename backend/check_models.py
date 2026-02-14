import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API Key not found")
else:
    genai.configure(api_key=api_key)
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                if '1.5' in m.name or 'flash' in m.name or 'pro' in m.name:
                    print(m.name)
    except Exception as e:
        print(f"Error listing models: {e}")
