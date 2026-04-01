import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
key = os.getenv("GEMINI_API_KEY")

print(f"Key detected: {key[:4]}...{key[-4:]}") # Shows first/last 4 chars
print(f"Key length: {len(key) if key else '0'}")

genai.configure(api_key=key)

try:
    model = genai.GenerativeModel('gemini-3-flash-preview')
    response = model.generate_content("Testing 1-2-3")
    print("SUCCESS: Key is valid!")
except Exception as e:
    print(f"FAILURE: {e}")
