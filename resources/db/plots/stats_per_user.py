import psycopg2
from datetime import datetime
from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# User ID for which to fetch the data
user_id = '571781026'  # Adjust the user ID as needed

# SQL queries to fetch the required data
query_data = """
SELECT
    SUM(duration_m) AS total_duration,
    AVG(duration_m) AS average_duration,
    COUNT(*) AS total_entries,
    MIN(created_at) AS first_entry_date,
    MAX(created_at) AS last_entry_date
FROM sittings
WHERE user_id = %s;
"""

# Establish the connection
conn = psycopg2.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=5432
)

try:
    # Creating a cursor object using the connection
    cur = conn.cursor()

    # Executing the query with parameter
    cur.execute(query_data, (user_id,))

    # Fetching data
    data = cur.fetchone()

    if data:
        total_duration, average_duration, total_entries, first_entry_date, last_entry_date = data
        # print(f"Total Duration: {total_duration} minutes")
        # print(f"Average Duration: {average_duration:.2f} minutes")
        # print(f"Total Entries: {total_entries}")
        print(f"Общая длительность: {total_duration} минуты")
        print(f"Средняя длительность: {average_duration:.2f} минуты")
        print(f"Общее количество медитаций: {total_entries}")

        # Calculate the percentage of days with an entry
        if first_entry_date and last_entry_date:
            total_days = (last_entry_date - first_entry_date).days + 1  # Including both first and last days
            active_days_query = """
            SELECT COUNT(DISTINCT created_at::date) AS active_days
            FROM sittings
            WHERE user_id = %s;
            """
            cur.execute(active_days_query, (user_id,))
            active_days = cur.fetchone()[0]
            percentage_active_days = (active_days / total_days) * 100 if total_days > 0 else 0
            # print(f"Percentage of Days with Entries: {percentage_active_days:.2f}%")
            print(f"Процент дней с медитациями: {percentage_active_days:.2f}%")
        else:
            print("No entries found to calculate active days.")
    else:
        print("No data found for user ID:", user_id)

finally:
    # Closing the cursor and connection
    cur.close()
    conn.close()
