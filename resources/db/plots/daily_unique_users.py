import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# SQL query to count unique users per day
query_daily_unique_users = """
SELECT DATE(created_at) AS day, COUNT(DISTINCT user_id) AS unique_users
FROM sittings
GROUP BY day
ORDER BY day;
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

# Executing the query
cur.execute(query_daily_unique_users)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting lists of dates and number of unique users
list_of_dates, list_of_unique_users = zip(*data)  # This unpacks the fetched data into two lists

# Your data
data = {
    'day': list_of_dates,
    'unique_users': list_of_unique_users
}

# Create a DataFrame
df = pd.DataFrame(data)
df['day'] = pd.to_datetime(df['day'])

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df['day'], df['unique_users'], marker='o', linestyle='-', color='green')
plt.title('Daily Unique Users')
plt.xlabel('Day')
plt.ylabel('Unique Users')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.show()
