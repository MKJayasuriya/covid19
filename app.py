from flask import Flask, render_template, request
import psycopg2
import folium
import os
import pandas as pd
import geopandas as gpd
import json

DB_NAME = "covid19"
USER = "covid19"
PASSWORD = "covid19"
HOST = "localhost"
PORT = "5432"

app = Flask(__name__)

# Ensure static/maps directory exists
os.makedirs("static/maps", exist_ok=True)

# Connect to PostgreSQL
# Connect to PostgreSQL
def get_db_connection():
    return psycopg2.connect(
        dbname=DB_NAME,
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT
    )

# Get column names (districts)
def get_columns():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'covid_cases_tamil_nadu' AND column_name != 'date'")
    columns = [row[0] for row in cur.fetchall()]
    cur.close()
    conn.close()
    return columns

# Fetch COVID data based on filters
def get_covid_data(date_filter, district):
    conn = get_db_connection()
    cur = conn.cursor()

    columns = get_columns()

    if district and district in columns:
        query = f"SELECT date, {district} FROM covid_cases_tamil_nadu"
    else:
        query = "SELECT * FROM covid_cases_tamil_nadu"

    params = []
    if date_filter:
        query += " WHERE date = %s"
        params.append(date_filter)

    query += " ORDER BY date DESC"

    cur.execute(query, tuple(params))
    data = cur.fetchall()

    cur.close()
    conn.close()

    return columns, data

# Generate Tamil Nadu Heatmap
def generate_tn_heatmap(date_filter):
    conn = get_db_connection()
    cur = conn.cursor()

    columns = get_columns()

    # Fetch the latest data or specific date
    if date_filter:
        query = "SELECT * FROM covid_cases_tamil_nadu WHERE date = %s"
        cur.execute(query, (date_filter,))
        data = cur.fetchone()
    else:
        query = "SELECT * FROM covid_cases_tamil_nadu ORDER BY date DESC LIMIT 1"
        cur.execute(query)
        data = cur.fetchone()

    cur.close()
    conn.close()

    if not data:
        return

    # Convert data to a dictionary
    district_data = {columns[i]: data[i + 1] for i in range(len(columns))}

    # Load Tamil Nadu GeoJSON file
    geojson_path = "TamilNadu.geojson"
    tamilnadu_map = gpd.read_file(geojson_path)

    # Standardize district names
    tamilnadu_map["NAME_2"] = tamilnadu_map["NAME_2"].str.lower().str.strip()

    # Convert district_data into a DataFrame
    df = pd.DataFrame(list(district_data.items()), columns=["district", "cases"])
    df["district"] = df["district"].str.lower().str.strip()

    # Merge GeoJSON with COVID data
    merged_data = tamilnadu_map.merge(df, left_on="NAME_2", right_on="district", how="left").fillna(0)

    # Convert merged data to JSON
    merged_json = json.loads(merged_data.to_json())

    # Create Folium Map
    tamilnadu_center = [10.8505, 78.7047]
    m = folium.Map(location=tamilnadu_center, zoom_start=7)

    # Add Choropleth layer
    folium.Choropleth(
        geo_data=merged_json,
        name="COVID-19 Cases",
        data=df,
        columns=["district", "cases"],
        key_on="feature.properties.NAME_2",
        fill_color="Reds",
        fill_opacity=0.7,
        line_opacity=0.4,
        legend_name="COVID-19 Cases in Tamil Nadu",
    ).add_to(m)

    # Save the map
    m.save("static/maps/heatmap.html")

# Main Route
@app.route("/", methods=["GET"])
def index():
    date_filter = request.args.get("date", "")
    district = request.args.get("district", "")

    columns, data = get_covid_data(date_filter, district)

    # Generate Tamil Nadu Heatmap
    generate_tn_heatmap(date_filter)

    return render_template("index.html", data=data, columns=columns, selected_district=district, date_filter=date_filter)

if __name__ == "__main__":
    app.run(debug=True)
