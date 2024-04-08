import psycopg2
import pandas as pd
import matplotlib.pyplot as plt

from app.core.consts import DB_USER, DB_PASSWORD, DB_URL, DB_HOST

# SQL query to execute
query_daily_duration_sums = """
SELECT DATE(created_at) AS day, SUM(duration_m) AS total_duration
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
cur.execute(query_daily_duration_sums)

# Fetching all rows from the database
data = cur.fetchall()

# Closing the cursor and connection
cur.close()
conn.close()

# Extracting lists of dates and total durations
list_of_dates, list_of_total_durations = zip(*data)  # This unpacks the fetched data into two lists

# Proceed with your existing code to create a DataFrame and plot
# Your data
data = {
    'day': list_of_dates,
    'total_duration': list_of_total_durations
}

# Create a DataFrame
df = pd.DataFrame(data)
df['day'] = pd.to_datetime(df['day'])

# Plotting
plt.figure(figsize=(12, 6))
plt.plot(df['day'], df['total_duration'], marker='o', linestyle='-', color='blue')
plt.title('Daily Total Duration')
plt.xlabel('Day')
plt.ylabel('Total Duration (minutes)')
plt.xticks(rotation=45)
plt.grid(True)
plt.tight_layout()

plt.show()
