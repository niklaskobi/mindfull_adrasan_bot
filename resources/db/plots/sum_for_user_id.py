import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# User ID for which to plot the data
user_id = '571781026'  # Adjust the user ID to the one you're interested in; make sure it's a string since user_id is a String type in your model

# SQL query to fetch duration and dates of meditation sessions for a specific user
query_duration_over_time = """
SELECT created_at AS session_date, duration_m
FROM sittings
WHERE user_id = %s
ORDER BY created_at;
"""

# Establishing the connection
conn = psycopg2.connect(
    dbname="postgres",
    user=DB_USER,
    password=DB_PASSWORD,
    host=DB_HOST,
    port=5432
)

# Creating a cursor object using the connection
cur = conn.cursor()

# Executing the query with parameter
cur.execute(query_duration_over_time, (user_id,))

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Check if data is fetched
if not data:
    print("No data found for user ID:", user_id)
else:
    # Extracting session dates and durations
    session_dates, durations = zip(*data)  # Unpacks fetched data into two lists

    # Your data
    data = {
        'session_date': session_dates,
        'duration_m': durations
    }

    # Create a DataFrame
    df = pd.DataFrame(data)

    # Plotting
    plt.figure(figsize=(14, 6))  # Adjusted figure size for better visibility
    # plt.plot(df['session_date'], df['duration_m'], marker='o', linestyle='-', color='blue')
    plt.bar(df['session_date'], df['duration_m'], color='purple')
    plt.title(f'Meditation Duration Over Time for User {user_id}')
    plt.xlabel('Session Date')
    plt.ylabel('Duration in Minutes')

    plt.grid(True)
    plt.tight_layout()

    plt.show()
