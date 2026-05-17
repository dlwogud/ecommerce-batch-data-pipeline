import os
import subprocess
from pathlib import Path


SOURCE_DB_HOST = os.getenv("SOURCE_DB_HOST", "source-db")
SOURCE_DB_PORT = os.getenv("SOURCE_DB_PORT", "5432")
SOURCE_DB_USER = os.getenv("SOURCE_DB_USER", "source_user")
SOURCE_DB_PASSWORD = os.getenv("SOURCE_DB_PASSWORD", "source_password")
SOURCE_DB_NAME = os.getenv("SOURCE_DB_NAME", "ecommerce_source")

WAREHOUSE_DB_HOST = os.getenv("WAREHOUSE_DB_HOST", "warehouse-db")
WAREHOUSE_DB_PORT = os.getenv("WAREHOUSE_DB_PORT", "5432")
WAREHOUSE_DB_USER = os.getenv("WAREHOUSE_DB_USER", "warehouse_user")
WAREHOUSE_DB_PASSWORD = os.getenv("WAREHOUSE_DB_PASSWORD", "warehouse_password")
WAREHOUSE_DB_NAME = os.getenv("WAREHOUSE_DB_NAME", "ecommerce_warehouse")

RAW_EXPORT_DIR = Path(os.getenv("RAW_EXPORT_DIR", "/opt/airflow/project/data/warehouse/raw"))
WAREHOUSE_RAW_DIR = Path(os.getenv("WAREHOUSE_RAW_DIR", "/data/warehouse/raw"))

TABLES = ["customers", "products", "orders", "order_items", "refunds"]

TABLE_COLUMNS = {
    "customers": [
        "customer_id",
        "customer_name",
        "email",
        "gender",
        "age_group",
        "region",
        "customer_grade",
        "signup_date",
        "created_at",
        "updated_at",
    ],
    "products": [
        "product_id",
        "product_name",
        "category",
        "brand",
        "price",
        "cost",
        "is_active",
        "created_at",
        "updated_at",
    ],
    "orders": [
        "order_id",
        "customer_id",
        "order_status",
        "order_datetime",
        "payment_method",
        "total_amount",
        "discount_amount",
        "shipping_fee",
        "created_at",
        "updated_at",
    ],
    "order_items": [
        "order_item_id",
        "order_id",
        "product_id",
        "quantity",
        "unit_price",
        "discount_amount",
        "item_total_amount",
        "created_at",
        "updated_at",
    ],
    "refunds": [
        "refund_id",
        "order_id",
        "order_item_id",
        "refund_datetime",
        "refund_amount",
        "refund_reason",
        "created_at",
        "updated_at",
    ],
}


def run_psql(
    sql: str,
    host: str,
    port: str,
    user: str,
    password: str,
    database: str,
) -> None:
    command = [
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        host,
        "-p",
        port,
        "-U",
        user,
        "-d",
        database,
        "-c",
        sql,
    ]
    env = {**os.environ, "PGPASSWORD": password}
    subprocess.run(command, check=True, env=env)


def run_source_sql(sql: str) -> None:
    run_psql(sql, SOURCE_DB_HOST, SOURCE_DB_PORT, SOURCE_DB_USER, SOURCE_DB_PASSWORD, SOURCE_DB_NAME)


def run_warehouse_sql(sql: str) -> None:
    run_psql(
        sql,
        WAREHOUSE_DB_HOST,
        WAREHOUSE_DB_PORT,
        WAREHOUSE_DB_USER,
        WAREHOUSE_DB_PASSWORD,
        WAREHOUSE_DB_NAME,
    )


def export_source_table(table_name: str) -> None:
    RAW_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_path = RAW_EXPORT_DIR / f"{table_name}.csv"

    command = [
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        SOURCE_DB_HOST,
        "-p",
        SOURCE_DB_PORT,
        "-U",
        SOURCE_DB_USER,
        "-d",
        SOURCE_DB_NAME,
        "-c",
        f"COPY {table_name} TO STDOUT WITH (FORMAT csv, HEADER true);",
    ]
    env = {**os.environ, "PGPASSWORD": SOURCE_DB_PASSWORD}

    with export_path.open("w", encoding="utf-8") as file:
        subprocess.run(command, check=True, env=env, stdout=file)


def truncate_raw_tables() -> None:
    run_warehouse_sql(
        """
        TRUNCATE TABLE
            raw.refunds,
            raw.order_items,
            raw.orders,
            raw.products,
            raw.customers;
        """
    )


def load_raw_table(table_name: str) -> None:
    csv_path = RAW_EXPORT_DIR / f"{table_name}.csv"
    columns = ", ".join(TABLE_COLUMNS[table_name])
    run_warehouse_sql(
        f"""
        COPY raw.{table_name} ({columns})
        FROM '{WAREHOUSE_RAW_DIR / csv_path.name}'
        WITH (FORMAT csv, HEADER true);
        """
    )


def print_raw_row_counts() -> None:
    for table_name in TABLES:
        run_warehouse_sql(
            f"SELECT 'raw.{table_name}' AS table_name, COUNT(*) AS row_count FROM raw.{table_name};"
        )


def main() -> None:
    for table_name in TABLES:
        export_source_table(table_name)

    truncate_raw_tables()

    for table_name in TABLES:
        load_raw_table(table_name)

    print_raw_row_counts()


if __name__ == "__main__":
    main()
