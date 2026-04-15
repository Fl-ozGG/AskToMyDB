# script: query.py
import sqlite3
import pandas as pd


conn = sqlite3.connect("ecommerce.db")

query = "SELECT * FROM ventas LIMIT 5"
df = pd.read_sql(query, conn)

conn.close()
print(df)
