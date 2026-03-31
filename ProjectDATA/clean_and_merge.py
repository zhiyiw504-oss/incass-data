import os
import pandas as pd
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(BASE_DIR, "merged_data.db")

# --- Read the two data files ---
orders = pd.read_csv(os.path.join(DATA_DIR, "order.txt"))
customers = pd.read_csv(os.path.join(DATA_DIR, "customer.txt"))

# --- Clean the duplicates ---
orders.drop_duplicates(inplace=True)
customers.drop_duplicates(inplace=True)

# --- Convert all amount values to CNY ---
rates = {"USD": 6.9, "EUR": 7.5, "CNY": 1.0, "JPY": 0.05}
orders["amount_cny"] = orders["amount"] * orders["currency"].map(rates)

# --- Connect order data and customer data on 'customer_id' ---
merged = pd.merge(orders, customers, on="customer_id")

# --- Write the merged data to an SQLite database ---
conn = sqlite3.connect(DB_PATH)
merged.to_sql("merged_orders", conn, if_exists="replace", index=False)

# --- Create summary table: average amount_cny by region ---
summary = merged.groupby("region")["amount_cny"].mean().reset_index()
summary.columns = ["region", "avg_amount_cny"]
summary.to_sql("region_summary", conn, if_exists="replace", index=False)

conn.close()

print("Done! Merged data and summary table saved to:", DB_PATH)
