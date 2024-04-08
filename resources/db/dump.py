import subprocess
from datetime import datetime

from app.core.consts import DB_USER, DB_HOST

current_date = datetime.now().strftime("%Y-%m-%d")

# Define the path and name of the dump file with the current date
dump_file_path = f"./resources/db/dumps/dump_{current_date}.sql"

# Construct the pg_dump command
command = f"pg_dump -U {DB_USER} -h {DB_HOST} -p 5432 postgres > {dump_file_path}"

# Execute the command
try:
    subprocess.run(command, shell=True, check=True)
    print("Database dump created successfully.")
except subprocess.CalledProcessError:
    print("Error occurred while creating database dump.")
