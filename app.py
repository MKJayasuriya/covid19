from flask import Flask, render_template, request
import psycopg2


DB_NAME = "covid19"
USER = "covid19"
PASSWORD = "covid19"
HOST = "localhost"
PORT = "5432"

app = Flask(__name__)


# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )


# Fetch all column names (districts)
def get_columns():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'covid_cases_tamil_nadu' AND column_name != 'date'")
    columns = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return columns

# Route with flexible filtering


@app.route("/", methods=["GET"])
def index():
    date_filter = request.args.get("date", "")
    district = request.args.get("district", "")  # Empty means all districts

    columns = get_columns()

    conn = get_db_connection()
    cur = conn.cursor()

    if district and district in columns:
        query = f"SELECT date, {district} FROM covid_cases_tamil_nadu"
    else:
        query = "SELECT * FROM covid_cases_tamil_nadu"

    params = []

    if date_filter:
        query += " WHERE date = %s"
        params.append(date_filter)

    query += " ORDER BY date DESC"

    print("query", query)
    cur.execute(query, tuple(params))
    data = cur.fetchall()

    cur.close()
    conn.close()

    return render_template("index.html", data=data, columns=columns, selected_district=district, date_filter=date_filter)


if __name__ == "__main__":
    app.run(debug=True)
