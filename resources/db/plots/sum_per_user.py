import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# SQL query to sum the minutes of meditation sessions per user
query_minutes_per_user = """
SELECT user_id, SUM(duration_m) AS total_minutes
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
cur.execute(query_minutes_per_user)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting user IDs and their total meditation minutes
user_ids, total_minutes = zip(*data)  # This unpacks the fetched data into two lists

# Your data
data = {
    'user_id': user_ids,
    'total_minutes': total_minutes
}

# Create a DataFrame
df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(14, 6))  # Adjusted figure size for better visibility
plt.bar(df['user_id'], df['total_minutes'], color='skyblue')
plt.title('Total Meditation Minutes per User')
plt.xlabel('User ID')
plt.ylabel('Total Meditation Minutes')

# Rotating x-axis labels if there are many users to prevent overlap
plt.xticks(rotation=90)

plt.grid(axis='y')  # Grid lines only for y-axis
plt.tight_layout()

plt.show()
