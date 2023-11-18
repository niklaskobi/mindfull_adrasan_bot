import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# General ################################################
BOT_TOKEN = os.environ.get("BOT_TOKEN")
CHAT_ID_DEVELOPER = os.environ.get("CHAT_ID_DEVELOPER")
