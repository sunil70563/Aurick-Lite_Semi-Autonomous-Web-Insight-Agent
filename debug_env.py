from dotenv import load_dotenv
import os

print("--- Debugging Environment ---")
print(f"Current CWD: {os.getcwd()}")
env_path = os.path.join(os.getcwd(), '.env')
print(f"Checking for .env at: {env_path}")
print(f"File exists: {os.path.exists(env_path)}")

loaded = load_dotenv()
print(f"load_dotenv returned: {loaded}")

key = os.getenv("GROQ_API_KEY")
if key:
    print(f"GROQ_API_KEY found: {key[:5]}... (length: {len(key)})")
else:
    print("ERROR: GROQ_API_KEY is None or Empty")
