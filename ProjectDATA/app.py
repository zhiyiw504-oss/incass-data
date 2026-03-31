import sqlite3
import os
from flask import Flask, jsonify, render_template

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "merged_data.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/orders")
def orders():
    conn = get_db()
    rows = conn.execute(
        "SELECT order_id, customer_id, customer_name, region, amount, currency, amount_cny FROM merged_orders"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/summary")
def summary():
    conn = get_db()
    rows = conn.execute(
        "SELECT region, avg_amount_cny FROM region_summary"
    ).fetchall()
    conn.close()
    return jsonify([dict(r) for r in rows])


@app.route("/api/db_mtime")
def db_mtime():
    return jsonify({"mtime": os.path.getmtime(DB_PATH)})


if __name__ == "__main__":
    app.run(debug=True, port=5000)
