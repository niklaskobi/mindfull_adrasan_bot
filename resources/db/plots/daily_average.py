import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_HOST

# SQL query to calculate the average duration per user per day
query_avg_duration_per_user_per_day = """
SELECT DATE(created_at) AS day, user_id, AVG(duration_m) AS avg_duration
FROM sittings
GROUP BY day, user_id
ORDER BY day, user_id;
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
cur.execute(query_avg_duration_per_user_per_day)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting lists of dates, user_ids, and average durations
list_of_dates, list_of_user_ids, list_of_avg_durations = zip(*data)  # This unpacks the fetched data into three lists

# Your data
data = {
    'day': list_of_dates,
    'user_id': list_of_user_ids,
    'avg_duration': list_of_avg_durations
}

# Create a DataFrame
df = pd.DataFrame(data)
df['day'] = pd.to_datetime(df['day'])

# Since the plot might become too cluttered if we plot every user separately,
# let's calculate the daily average across all users for visualization.
daily_avg_df = df.groupby('day')['avg_duration'].mean().reset_index()

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(daily_avg_df['day'], daily_avg_df['avg_duration'], marker='o', linestyle='-', color='red')
plt.title('Average Duration per User per Day')
plt.xlabel('Day')
plt.ylabel('Average Duration (minutes)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.show()
