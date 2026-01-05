import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

class Settings:
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    HEADLESS = os.getenv("HEADLESS", "false").lower() == "true"
    DEFAULT_MODEL = "llama-3.1-70b-versatile"
    MAX_STEPS = int(os.getenv("MAX_STEPS", 10))

settings = Settings()
