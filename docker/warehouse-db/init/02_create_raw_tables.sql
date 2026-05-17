CREATE TABLE raw.customers (
    customer_id VARCHAR(20),
    customer_name VARCHAR(100),
    email VARCHAR(255),
    gender VARCHAR(20),
    age_group VARCHAR(20),
    region VARCHAR(50),
    customer_grade VARCHAR(20),
    signup_date DATE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.products (
    product_id VARCHAR(20),
    product_name VARCHAR(255),
    category VARCHAR(50),
    brand VARCHAR(100),
    price INTEGER,
    cost INTEGER,
    is_active BOOLEAN,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.orders (
    order_id VARCHAR(20),
    customer_id VARCHAR(20),
    order_status VARCHAR(30),
    order_datetime TIMESTAMP,
    payment_method VARCHAR(30),
    total_amount INTEGER,
    discount_amount INTEGER,
    shipping_fee INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.order_items (
    order_item_id VARCHAR(20),
    order_id VARCHAR(20),
    product_id VARCHAR(20),
    quantity INTEGER,
    unit_price INTEGER,
    discount_amount INTEGER,
    item_total_amount INTEGER,
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE raw.refunds (
    refund_id VARCHAR(20),
    order_id VARCHAR(20),
    order_item_id VARCHAR(20),
    refund_datetime TIMESTAMP,
    refund_amount INTEGER,
    refund_reason VARCHAR(50),
    created_at TIMESTAMP,
    updated_at TIMESTAMP,
    loaded_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
