import psycopg2
import psycopg2.extras
from db import get_connection

SORT_COLUMNS = {
    "best_rank": "best_rank DESC",
    "price_asc": "price ASC",
    "price_desc": "price DESC",
    "rating": "rating DESC",
}
DEFAULT_SORT = "best_rank"
MAX_LIMIT = 50
DEFAULT_LIMIT = 10


def build_query(filters: dict):
    """
    Consumes the exact "filters" shape produced by INTENT_CLASSIFIER_PROMPT:
    {
        "category": "clothing" | None,
        "price_lt": 200 | None,
        "price_gt": None,
        "unit": "rupees" | None,     # not a DB column — ignored here, used by router.py for the disclaimer note only
        "attributes": {"waterproof": True} | {},
        "sort": "best_rank" | "price_asc" | "price_desc" | "rating",
        "limit": 10
    }
    Returns (sql, values) — always parameterized, never string-formats user input.
    """
    where_clauses = []
    values = []

    if filters.get("category"):
        where_clauses.append("category = %s")
        values.append(filters["category"])

    if filters.get("price_lt") is not None:
        where_clauses.append("price < %s")
        values.append(filters["price_lt"])

    if filters.get("price_gt") is not None:
        where_clauses.append("price > %s")
        values.append(filters["price_gt"])

    attributes = filters.get("attributes") or {}
    if attributes:
        where_clauses.append("attributes @> %s::jsonb")
        values.append(psycopg2.extras.Json(attributes))

    where_sql = " AND ".join(where_clauses) if where_clauses else "TRUE"
    order_sql = SORT_COLUMNS.get(filters.get("sort", DEFAULT_SORT), SORT_COLUMNS[DEFAULT_SORT])

    limit = filters.get("limit", DEFAULT_LIMIT)
    try:
        limit = int(limit)
    except (TypeError, ValueError):
        limit = DEFAULT_LIMIT
    limit = max(1, min(limit, MAX_LIMIT))

    sql = f"""
        SELECT product_id, product_name, category, price, stock_quantity,
               rating, num_reviews, seller_name, best_rank, attributes
        FROM products
        WHERE {where_sql}
        ORDER BY {order_sql}
        LIMIT %s
    """
    values.append(limit)
    return sql, values


def run_query(filters: dict) -> list:
    sql, values = build_query(filters)
    conn = get_connection()
    try:
        with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, values)
            return [dict(row) for row in cur.fetchall()]
    finally:
        conn.close()


if __name__ == "__main__":
    # quick standalone test — run `python query_builder.py` to sanity-check
    # against the real DB before wiring this into router.py
    test_filters = {"category": "electronics", "price_lt": 500, "sort": "best_rank", "limit": 5}
    results = run_query(test_filters)
    for row in results:
        print(row["product_name"], row["price"], row["best_rank"])