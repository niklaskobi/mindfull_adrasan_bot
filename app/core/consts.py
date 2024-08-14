import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# General ################################################
BOT_TOKEN = os.environ.get("BOT_TOKEN")
LOGGER_MAIN = "logger_main"

# Database ################################################
DB_USER = os.environ.get("DB_USER")
DB_PASSWORD = os.environ.get("DB_PASSWORD")
DB_HOST = os.environ.get("DB_HOST")
# DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_ENDPOINT}/postgres"
# postgres://u4btur5gruef61:p7376e40edd7c8a6ca46d8201eabc96152ccb789625a98457e9ac9381750731d5@c724r43q8jp5nk.cluster-czz5s0kz4scl.eu-west-1.rds.amazonaws.com:5432/d9pdlq44qev2ck
# This variable is directly controlled by heroku, don't change it
DATABASE_URL = os.environ.get("DATABASE_URL")
