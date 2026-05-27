CREATE SCHEMA IF NOT EXISTS metadata;

CREATE TABLE IF NOT EXISTS metadata.batch_runs (
    batch_id VARCHAR(80) PRIMARY KEY,
    dag_id VARCHAR(255) NOT NULL,
    run_id VARCHAR(255) NOT NULL,
    load_type VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL,
    watermark_start TIMESTAMP NOT NULL,
    watermark_end TIMESTAMP NOT NULL,
    started_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    finished_at TIMESTAMP,
    source_row_count INTEGER NOT NULL DEFAULT 0,
    target_row_count INTEGER NOT NULL DEFAULT 0,
    error_message TEXT,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT batch_runs_status_check
        CHECK (status IN ('running', 'success', 'failed')),
    CONSTRAINT batch_runs_load_type_check
        CHECK (load_type IN ('full', 'incremental'))
);

CREATE TABLE IF NOT EXISTS metadata.batch_table_counts (
    batch_id VARCHAR(80) NOT NULL,
    table_name VARCHAR(100) NOT NULL,
    source_row_count INTEGER NOT NULL,
    target_row_count INTEGER NOT NULL,
    status VARCHAR(30) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT batch_table_counts_pk
        PRIMARY KEY (batch_id, table_name),
    CONSTRAINT batch_table_counts_batch_id_fk
        FOREIGN KEY (batch_id) REFERENCES metadata.batch_runs (batch_id),
    CONSTRAINT batch_table_counts_status_check
        CHECK (status IN ('success', 'failed'))
);

CREATE UNIQUE INDEX IF NOT EXISTS raw_customers_customer_id_uq
    ON raw.customers (customer_id);

CREATE UNIQUE INDEX IF NOT EXISTS raw_products_product_id_uq
    ON raw.products (product_id);

CREATE UNIQUE INDEX IF NOT EXISTS raw_orders_order_id_uq
    ON raw.orders (order_id);

CREATE UNIQUE INDEX IF NOT EXISTS raw_order_items_order_item_id_uq
    ON raw.order_items (order_item_id);

CREATE UNIQUE INDEX IF NOT EXISTS raw_refunds_refund_id_uq
    ON raw.refunds (refund_id);
