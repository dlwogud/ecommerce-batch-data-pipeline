import subprocess


SOURCE_DB_CONTAINER = "ecommerce-source-db"
SOURCE_DB_USER = "source_user"
SOURCE_DB_NAME = "ecommerce_source"
SOURCE_DATA_DIR = "/data/source"

LOAD_STEPS = [
    ("customers", "customers.csv"),
    ("products", "products.csv"),
    ("orders", "orders.csv"),
    ("order_items", "order_items.csv"),
    ("refunds", "refunds.csv"),
]


def run_psql(sql: str) -> None:
    command = [
        "docker",
        "exec",
        SOURCE_DB_CONTAINER,
        "psql",
        "-v",
        "ON_ERROR_STOP=1",
        "-U",
        SOURCE_DB_USER,
        "-d",
        SOURCE_DB_NAME,
        "-c",
        sql,
    ]
    subprocess.run(command, check=True)


def truncate_tables() -> None:
    run_psql(
        """
        TRUNCATE TABLE
            refunds,
            order_items,
            orders,
            products,
            customers
        RESTART IDENTITY CASCADE;
        """
    )


def load_table(table_name: str, file_name: str) -> None:
    csv_path = f"{SOURCE_DATA_DIR}/{file_name}"
    run_psql(
        f"""
        COPY {table_name}
        FROM '{csv_path}'
        WITH (FORMAT csv, HEADER true);
        """
    )


def print_row_counts() -> None:
    for table_name, _ in LOAD_STEPS:
        run_psql(f"SELECT '{table_name}' AS table_name, COUNT(*) AS row_count FROM {table_name};")


def main() -> None:
    truncate_tables()

    for table_name, file_name in LOAD_STEPS:
        load_table(table_name, file_name)

    print_row_counts()


if __name__ == "__main__":
    main()
