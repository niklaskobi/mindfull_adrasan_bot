import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# General ################################################
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID_DEVELOPER = os.environ.get("CHAT_ID_DEVELOPER")
LOGGER_MAIN = "logger_main"

# Database ################################################
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_ENDPOINT = os.environ.get("DB_ENDPOINT")
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}/postgres"
