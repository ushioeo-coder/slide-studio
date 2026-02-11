import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    print("API Key not set.")
    exit()

genai.configure(api_key=api_key)

print("--- Testing Image Generation ---")

candidates = [
    "models/imagen-3.0-generate-001",
    "gemini-2.0-flash-exp", 
    "models/gemini-2.0-flash-exp-image-generation"
]

prompt = "A futuristic city skyline at sunset, 8k resolution, cinematic lighting"

for model_name in candidates:
    print(f"\nTesting model: {model_name}")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content(
            prompt,
            generation_config=genai.GenerationConfig(response_mime_type="image/jpeg")
        )
        
        if response.parts:
            print("  SUCCESS: Image data received.")
            print(f"  Types: {[type(p) for p in response.parts]}")
        else:
            print("  FAILURE: No parts in response.")
            print(f"  Response text: {response.text}")
            
    except Exception as e:
        print(f"  ERROR: {e}")
