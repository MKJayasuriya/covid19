import psycopg2

DB_NAME = "covid19"
USER = "covid19"
PASSWORD = "covid19"
HOST = "localhost"
PORT = "5432"

# Database connection
conn = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT
)
cur = conn.cursor()

# Read the SQL file
with open("migrations.sql", "r") as file:
    sql_queries = file.read()

# Execute the migration
cur.execute(sql_queries)
conn.commit()

print("Migration applied successfully!")

# Close connection
cur.close()
conn.close()
