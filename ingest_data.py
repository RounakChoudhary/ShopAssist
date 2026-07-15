import os
import numpy as np
import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import JSONB

load_dotenv()

# DB CONNECTION 
PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")

if not all([PG_USER, PG_PASSWORD, PG_DB]):
    raise RuntimeError("Missing PG_USER / PG_PASSWORD / PG_DB in .env")

engine = create_engine(
    f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}"
)


# LOAD CSV

CSV_PATH = os.path.join(os.path.dirname(__file__), "data", "ecommerce_dataset.csv")
df = pd.read_csv(CSV_PATH)

# RENAME COLUMNS TO MATCH YOUR TABLE SCHEMA

RENAME_MAP = {
    "Product ID": "source_product_id",   # kept only for reference, not inserted as PK
    "Product Name": "product_name",
    "Category": "category",
    "Price (USD)": "price",
    "Stock Quantity": "stock_quantity",
    "Rating": "rating",
    "Number of Reviews": "num_reviews",
    "Seller Name": "seller_name",
}
df = df.rename(columns=RENAME_MAP)

REQUIRED_COLUMNS = [
    "product_name", "category", "price",
    "stock_quantity", "rating", "num_reviews", "seller_name",
]
missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
if missing:
    raise ValueError(
        f"Missing expected columns after rename: {missing}. "
        f"Check RENAME_MAP against your CSV's actual headers."
    )

# Drop the source ID — Postgres will assign its own via SERIAL

df = df.drop(columns=["source_product_id"], errors="ignore")


# BASIC CLEANING

df["price"] = pd.to_numeric(df["price"], errors="coerce")
df["stock_quantity"] = pd.to_numeric(df["stock_quantity"], errors="coerce").fillna(0).astype(int)
df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0)
df["num_reviews"] = pd.to_numeric(df["num_reviews"], errors="coerce").fillna(0).astype(int)

before = len(df)
df = df.dropna(subset=["product_name", "category", "price"])
dropped = before - len(df)
if dropped:
    print(f"Dropped {dropped} rows missing product_name/category/price.")


# best_rank ( formula for now is rating * log(1 + num_reviews) ) - this is simple heuristic for ranking products.

df["best_rank"] = df["rating"] * np.log1p(df["num_reviews"])


# ATTRIBUTES (JSONB) — this dataset has no per-category attributes,
# so we just create on empty JSON object for each row.

df["attributes"] = [{} for _ in range(len(df))]

# Keep only columns that exist in the products table, in a sane order

FINAL_COLUMNS = [
    "product_name", "category", "price", "stock_quantity",
    "rating", "num_reviews", "seller_name", "best_rank", "attributes",
]
df = df[FINAL_COLUMNS]

# INSERT INTO POSTGRES

df.to_sql(
    "products",
    engine,
    if_exists="append",
    index=False,
    dtype={"attributes": JSONB},
)
