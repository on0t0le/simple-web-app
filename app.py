import os
from flask import Flask, jsonify
from influxdb import InfluxDBClient

# Flask application
app = Flask(__name__)

# InfluxDB configuration from environment variables
influx_enabled = os.getenv("INFLUXDB_ENABLED", True)
host = os.getenv("INFLUXDB_HOST", "localhost")
port = int(os.getenv("INFLUXDB_PORT", 8086))
database = os.getenv("INFLUXDB_DATABASE", "your_database")

# Function to create database if it doesn't exist
def create_database_if_not_exists(db_name):
    databases = client.get_list_database()
    if not any(db['name'] == db_name for db in databases):
        client.create_database(db_name)

if influx_enabled is True:
    # Initialize InfluxDB client
    client = InfluxDBClient(host=host, port=port)
    # Ensure the database exists
    create_database_if_not_exists(database)

    # Switch to the desired database
    client.switch_database(database)

# Visitor counter
visitor_count = 0

@app.route('/')
def index():
    global visitor_count
    visitor_count += 1

    # Prepare the data in the InfluxDB format
    data = [
        {
            "measurement": "visitor_count",
            "tags": {
                "location": "home_page"
            },
            "fields": {
                "count": visitor_count
            }
        }
    ]
    if influx_enabled is True:
        # Write data to InfluxDB
        client.write_points(data)

    return f"Visitor count: {visitor_count}"

@app.route('/readiness', methods=['GET'])
def readiness():
    return jsonify(message="OK"), 200

@app.route('/noreadiness', methods=['GET'])
def noreadiness():
    return jsonify(message="NOT OK"), 418

@app.route('/liveness', methods=['GET'])
def liveness():
    return jsonify(message="OK"), 200

@app.route('/noliveness', methods=['GET'])
def noliveness():
    return jsonify(message="NOT OK"), 418

if __name__ == '__main__':
    # Make Flask listen on all available IP addresses
    app.run(host='0.0.0.0', port=5000, debug=True)