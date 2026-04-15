# script: setup_db.py
import kagglehub
import pandas as pd
import sqlite3

path = kagglehub.dataset_download("carrie1/ecommerce-data")
csv_path = f"{path}/data.csv"

df = pd.read_csv(csv_path, encoding="ISO-8859-1")

conn = sqlite3.connect("ecommerce.db")
df.to_sql("ventas", conn, if_exists="replace", index=False)
conn.close()

print("DB creada")