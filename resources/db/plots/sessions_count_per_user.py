import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# SQL query to count the number of meditation sessions per user
query_sessions_per_user = """
SELECT user_id, COUNT(*) AS meditation_count
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
cur.execute(query_sessions_per_user)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting user IDs and their number of meditation sessions
user_ids, meditation_counts = zip(*data)  # This unpacks the fetched data into two lists

# Your data
data = {
    'user_id': user_ids,
    'meditations': meditation_counts
}

# Create a DataFrame
df = pd.DataFrame(data)

# Plotting
plt.figure(figsize=(14, 6))  # Adjusted figure size for better visibility
plt.bar(df['user_id'], df['meditations'], color='teal')
plt.title('Number of Meditations per User')
plt.xlabel('User ID')
plt.ylabel('Number of Meditations')

# Rotating x-axis labels if there are many users to prevent overlap
plt.xticks(rotation=90)

plt.grid(axis='y')  # Grid lines only for y-axis
plt.tight_layout()

plt.show()
