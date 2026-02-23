import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    MAX_HISTORY_MESSAGES = 10
    MODEL_NAME = "gemini-1.5-flash"
    TEMPERATURE = 0.7
