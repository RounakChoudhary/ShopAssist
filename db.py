import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

PG_USER = os.getenv("PG_USER")
PG_PASSWORD = os.getenv("PG_PASSWORD")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_PORT = os.getenv("PG_PORT", "5432")
PG_DB = os.getenv("PG_DB")

if not all([PG_USER, PG_PASSWORD, PG_DB]):
    print("[DEV ERROR] Setup Failed: PG_USER / PG_PASSWORD / PG_DB missing in environment variables.")
    raise RuntimeError("Postgres credentials are not fully set.")


def get_connection():
    return psycopg2.connect(
        dbname=PG_DB, user=PG_USER, password=PG_PASSWORD, host=PG_HOST, port=PG_PORT
    )