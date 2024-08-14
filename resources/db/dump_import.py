# import os
# import psycopg2
#
# DATABASE_URL = os.environ['MIGRATE_PG_NEW_DB_URL']
#
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
#
import subprocess
import os
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()
# Define your Heroku DB credentials or use environment variables for security
HEROKU_DB_URL = os.getenv('DATABASE_URL')

# Get the current date to match the dump file name
current_date = datetime.now().strftime("%Y-%m-%d")

# Define the path to the dump file you created earlier
dump_file_path = f"./resources/db/dumps/dump_{current_date}.sql"

# Construct the psql command to restore the dump file to the Heroku database
command = f"psql {HEROKU_DB_URL} < {dump_file_path}"

# Execute the command
try:
    subprocess.run(command, shell=True, check=True)
    print("Database restored to Heroku successfully.")
except subprocess.CalledProcessError:
    print("Error occurred while restoring the database to Heroku.")
