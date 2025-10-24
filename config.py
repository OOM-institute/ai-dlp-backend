import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    MONGODB_URI = os.getenv("MONGODB_URI")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

settings = Settings()