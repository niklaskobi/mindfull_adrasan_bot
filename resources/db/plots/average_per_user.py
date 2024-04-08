import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# SQL query to calculate the average duration per user
query_avg_duration_per_user = """
SELECT user_id, AVG(duration_m) AS avg_duration
FROM sittings
GROUP BY user_id
ORDER BY user_id;
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
cur.execute(query_avg_duration_per_user)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting user IDs and their average durations
user_ids, avg_durations = zip(*data)  # This unpacks the fetched data into two lists

# Your data
data = {
    'user_id': user_ids,
    'avg_duration': avg_durations
}

# Create a DataFrame
df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(14, 6))  # Adjusted figure size here
plt.scatter(df['user_id'], df['avg_duration'], color='purple')
plt.title('Average Duration per User')
plt.xlabel('User ID')
plt.ylabel('Average Duration (minutes)')

# Rotating x-axis labels
plt.xticks(rotation=90)  # Rotating labels by 90 degrees

plt.grid(True)
plt.tight_layout()

plt.show()
