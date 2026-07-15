import csv
import os
import json
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("PG_HOST"),
    "port": int(os.getenv("PG_PORT", "5432")),
    "dbname": os.getenv("PG_DB"),
    "user": os.getenv("PG_USER"),
    "password": os.getenv("PG_PASSWORD"),
}

CSV_PATH = "data/ecommerce_dataset.csv"

conn = psycopg2.connect(**DB_CONFIG)
cur = conn.cursor()

with open(CSV_PATH, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:

        cur.execute(
            """
            INSERT INTO products
            (
                product_name,
                category,
                price,
                stock_quantity,
                rating,
                num_reviews,
                seller_name,
                best_rank,
                attributes
            )
            VALUES
            (
                %s,%s,%s,%s,%s,%s,%s,%s,%s::jsonb
            )
            """,
            (
                row["product_name"],
                row["category"],
                float(row["price"]),
                int(row["stock_quantity"]),
                float(row["rating"]),
                int(row["num_reviews"]),
                row["seller_name"],
                int(row["best_rank"]),
                json.dumps(json.loads(row["attributes"]))
            )
        )

conn.commit()

print("Data imported successfully!")

cur.close()
conn.close()