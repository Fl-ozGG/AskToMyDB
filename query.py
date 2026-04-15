# script: query.py
import sqlite3
import pandas as pd


conn = sqlite3.connect("ecommerce.db")

query = """
SELECT COUNT(DISTINCT CustomerID) AS clientes_unicos
FROM ventas;
"""


df = pd.read_sql(query, conn)

conn.close()
print(df)
