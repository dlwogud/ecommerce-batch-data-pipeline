import os
import subprocess
from datetime import datetime
from hashlib import md5
from pathlib import Path
from typing import Optional


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

DEFAULT_WATERMARK_START = "1900-01-01 00:00:00"
LOAD_TYPE = "incremental"

TABLES = ["customers", "products", "orders", "order_items", "refunds"]
PRIMARY_KEYS = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "order_items": "order_item_id",
    "refunds": "refund_id",
}

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


def sql_literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


def run_psql(
    sql: str,
    host: str,
    port: str,
    user: str,
    password: str,
    database: str,
    capture_output: bool = False,
) -> str:
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
    result = subprocess.run(
        command,
        check=True,
        env=env,
        text=True,
        capture_output=capture_output,
    )
    return result.stdout.strip() if capture_output else ""


def run_source_sql(sql: str, capture_output: bool = False) -> str:
    return run_psql(
        sql,
        SOURCE_DB_HOST,
        SOURCE_DB_PORT,
        SOURCE_DB_USER,
        SOURCE_DB_PASSWORD,
        SOURCE_DB_NAME,
        capture_output=capture_output,
    )


def run_warehouse_sql(sql: str, capture_output: bool = False) -> str:
    return run_psql(
        sql,
        WAREHOUSE_DB_HOST,
        WAREHOUSE_DB_PORT,
        WAREHOUSE_DB_USER,
        WAREHOUSE_DB_PASSWORD,
        WAREHOUSE_DB_NAME,
        capture_output=capture_output,
    )


def fetch_warehouse_scalar(sql: str) -> str:
    command = [
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-h",
        WAREHOUSE_DB_HOST,
        "-p",
        WAREHOUSE_DB_PORT,
        "-U",
        WAREHOUSE_DB_USER,
        "-d",
        WAREHOUSE_DB_NAME,
        "-t",
        "-A",
        "-c",
        sql,
    ]
    env = {**os.environ, "PGPASSWORD": WAREHOUSE_DB_PASSWORD}
    result = subprocess.run(command, check=True, env=env, text=True, capture_output=True)
    return result.stdout.strip()


def fetch_source_scalar(sql: str) -> str:
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
        "-t",
        "-A",
        "-c",
        sql,
    ]
    env = {**os.environ, "PGPASSWORD": SOURCE_DB_PASSWORD}
    result = subprocess.run(command, check=True, env=env, text=True, capture_output=True)
    return result.stdout.strip()


def get_batch_context() -> tuple[str, str, str, str, str]:
    dag_id = os.getenv("AIRFLOW_CTX_DAG_ID", "manual_batch")
    run_id = os.getenv("AIRFLOW_CTX_DAG_RUN_ID", f"manual__{datetime.utcnow().isoformat(timespec='seconds')}")
    safe_run_id = "".join(character if character.isalnum() else "_" for character in run_id)
    run_hash = md5(run_id.encode("utf-8")).hexdigest()[:8]
    batch_id = f"{dag_id}__{safe_run_id[:45]}__{run_hash}"[:80]
    watermark_start = fetch_warehouse_scalar(
        f"""
        SELECT COALESCE(
            MAX(watermark_end)::text,
            {sql_literal(DEFAULT_WATERMARK_START)}
        )
        FROM metadata.batch_runs
        WHERE dag_id = {sql_literal(dag_id)}
          AND load_type = {sql_literal(LOAD_TYPE)}
          AND status = 'success';
        """
    )
    watermark_end = fetch_source_scalar("SELECT CURRENT_TIMESTAMP::timestamp(0)::text;")
    return batch_id, dag_id, run_id, watermark_start, watermark_end


def start_batch(
    batch_id: str,
    dag_id: str,
    run_id: str,
    watermark_start: str,
    watermark_end: str,
) -> None:
    run_warehouse_sql(
        f"""
        INSERT INTO metadata.batch_runs (
            batch_id,
            dag_id,
            run_id,
            load_type,
            status,
            watermark_start,
            watermark_end,
            started_at,
            updated_at
        )
        VALUES (
            {sql_literal(batch_id)},
            {sql_literal(dag_id)},
            {sql_literal(run_id)},
            {sql_literal(LOAD_TYPE)},
            'running',
            {sql_literal(watermark_start)}::timestamp,
            {sql_literal(watermark_end)}::timestamp,
            CURRENT_TIMESTAMP,
            CURRENT_TIMESTAMP
        )
        ON CONFLICT (batch_id) DO UPDATE
        SET status = 'running',
            watermark_start = EXCLUDED.watermark_start,
            watermark_end = EXCLUDED.watermark_end,
            source_row_count = 0,
            target_row_count = 0,
            error_message = NULL,
            started_at = CURRENT_TIMESTAMP,
            finished_at = NULL,
            updated_at = CURRENT_TIMESTAMP;
        """
    )
    run_warehouse_sql(
        f"DELETE FROM metadata.batch_table_counts WHERE batch_id = {sql_literal(batch_id)};"
    )


def finish_batch(batch_id: str, status: str, error_message: Optional[str] = None) -> None:
    escaped_error_message = "NULL" if error_message is None else sql_literal(error_message[:2000])
    run_warehouse_sql(
        f"""
        UPDATE metadata.batch_runs
        SET status = {sql_literal(status)},
            finished_at = CURRENT_TIMESTAMP,
            source_row_count = COALESCE((
                SELECT SUM(source_row_count)
                FROM metadata.batch_table_counts
                WHERE batch_id = {sql_literal(batch_id)}
            ), 0),
            target_row_count = COALESCE((
                SELECT SUM(target_row_count)
                FROM metadata.batch_table_counts
                WHERE batch_id = {sql_literal(batch_id)}
            ), 0),
            error_message = {escaped_error_message},
            updated_at = CURRENT_TIMESTAMP
        WHERE batch_id = {sql_literal(batch_id)};
        """
    )


def export_source_table(table_name: str, watermark_start: str, watermark_end: str) -> None:
    RAW_EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    export_path = RAW_EXPORT_DIR / f"{table_name}.csv"
    columns = ", ".join(TABLE_COLUMNS[table_name])

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
        f"""
        COPY (
            SELECT {columns}
            FROM {table_name}
            WHERE updated_at > {sql_literal(watermark_start)}::timestamp
              AND updated_at <= {sql_literal(watermark_end)}::timestamp
            ORDER BY {PRIMARY_KEYS[table_name]}
        ) TO STDOUT WITH (FORMAT csv, HEADER true);
        """,
    ]
    env = {**os.environ, "PGPASSWORD": SOURCE_DB_PASSWORD}

    with export_path.open("w", encoding="utf-8") as file:
        subprocess.run(command, check=True, env=env, stdout=file)


def source_row_count(table_name: str, watermark_start: str, watermark_end: str) -> int:
    count = fetch_source_scalar(
        f"""
        SELECT COUNT(*)
        FROM {table_name}
        WHERE updated_at > {sql_literal(watermark_start)}::timestamp
          AND updated_at <= {sql_literal(watermark_end)}::timestamp;
        """
    )
    return int(count or 0)


def load_incremental_table(table_name: str) -> int:
    load_table_name = f"_load_{table_name}"
    csv_path = WAREHOUSE_RAW_DIR / f"{table_name}.csv"
    columns = ", ".join(TABLE_COLUMNS[table_name])
    insert_columns = ", ".join([*TABLE_COLUMNS[table_name], "loaded_at"])
    primary_key = PRIMARY_KEYS[table_name]

    run_warehouse_sql(f"DROP TABLE IF EXISTS raw.{load_table_name};")
    run_warehouse_sql(f"CREATE TABLE raw.{load_table_name} (LIKE raw.{table_name} INCLUDING DEFAULTS);")
    run_warehouse_sql(
        f"""
        COPY raw.{load_table_name} ({columns})
        FROM '{csv_path}'
        WITH (FORMAT csv, HEADER true);
        """
    )

    loaded_count = int(fetch_warehouse_scalar(f"SELECT COUNT(*) FROM raw.{load_table_name};") or 0)

    run_warehouse_sql(
        f"""
        DELETE FROM raw.{table_name} AS target
        USING raw.{load_table_name} AS source
        WHERE target.{primary_key} = source.{primary_key};
        """
    )
    run_warehouse_sql(
        f"""
        INSERT INTO raw.{table_name} ({insert_columns})
        SELECT {insert_columns}
        FROM raw.{load_table_name};
        """
    )
    run_warehouse_sql(f"DROP TABLE raw.{load_table_name};")

    return loaded_count


def record_table_count(
    batch_id: str,
    table_name: str,
    source_count: int,
    target_count: int,
) -> None:
    status = "success" if source_count == target_count else "failed"
    run_warehouse_sql(
        f"""
        INSERT INTO metadata.batch_table_counts (
            batch_id,
            table_name,
            source_row_count,
            target_row_count,
            status
        )
        VALUES (
            {sql_literal(batch_id)},
            {sql_literal(table_name)},
            {source_count},
            {target_count},
            {sql_literal(status)}
        );
        """
    )

    if source_count != target_count:
        raise ValueError(
            f"Row count mismatch for {table_name}: "
            f"source={source_count}, target={target_count}"
        )


def main() -> None:
    batch_id, dag_id, run_id, watermark_start, watermark_end = get_batch_context()
    start_batch(batch_id, dag_id, run_id, watermark_start, watermark_end)
    print(f"batch_id: {batch_id}")
    print(f"watermark_start: {watermark_start}")
    print(f"watermark_end: {watermark_end}")

    try:
        for table_name in TABLES:
            source_count = source_row_count(table_name, watermark_start, watermark_end)
            export_source_table(table_name, watermark_start, watermark_end)
            target_count = load_incremental_table(table_name)
            record_table_count(batch_id, table_name, source_count, target_count)
            print(f"{table_name}: source={source_count}, target={target_count}")

        finish_batch(batch_id, "success")
    except Exception as error:
        finish_batch(batch_id, "failed", str(error))
        raise


if __name__ == "__main__":
    main()
