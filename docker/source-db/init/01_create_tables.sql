CREATE TABLE customers (
    customer_id VARCHAR(20) PRIMARY KEY,
    customer_name VARCHAR(100) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    gender VARCHAR(20) NOT NULL,
    age_group VARCHAR(20) NOT NULL,
    region VARCHAR(50) NOT NULL,
    customer_grade VARCHAR(20) NOT NULL,
    signup_date DATE NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT customers_grade_check
        CHECK (customer_grade IN ('bronze', 'silver', 'gold', 'vip'))
);

CREATE TABLE products (
    product_id VARCHAR(20) PRIMARY KEY,
    product_name VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    brand VARCHAR(100) NOT NULL,
    price INTEGER NOT NULL,
    cost INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT products_price_check CHECK (price >= 0),
    CONSTRAINT products_cost_check CHECK (cost >= 0)
);

CREATE TABLE orders (
    order_id VARCHAR(20) PRIMARY KEY,
    customer_id VARCHAR(20) NOT NULL,
    order_status VARCHAR(30) NOT NULL,
    order_datetime TIMESTAMP NOT NULL,
    payment_method VARCHAR(30) NOT NULL,
    total_amount INTEGER NOT NULL,
    discount_amount INTEGER NOT NULL,
    shipping_fee INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT orders_customer_id_fk
        FOREIGN KEY (customer_id) REFERENCES customers (customer_id),
    CONSTRAINT orders_status_check
        CHECK (order_status IN ('completed', 'partially_refunded', 'refunded')),
    CONSTRAINT orders_payment_method_check
        CHECK (payment_method IN ('card', 'kakao_pay', 'naver_pay', 'bank_transfer')),
    CONSTRAINT orders_total_amount_check CHECK (total_amount >= 0),
    CONSTRAINT orders_discount_amount_check CHECK (discount_amount >= 0),
    CONSTRAINT orders_shipping_fee_check CHECK (shipping_fee >= 0)
);

CREATE TABLE order_items (
    order_item_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    product_id VARCHAR(20) NOT NULL,
    quantity INTEGER NOT NULL,
    unit_price INTEGER NOT NULL,
    discount_amount INTEGER NOT NULL,
    item_total_amount INTEGER NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT order_items_order_id_fk
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT order_items_product_id_fk
        FOREIGN KEY (product_id) REFERENCES products (product_id),
    CONSTRAINT order_items_quantity_check CHECK (quantity > 0),
    CONSTRAINT order_items_unit_price_check CHECK (unit_price >= 0),
    CONSTRAINT order_items_discount_amount_check CHECK (discount_amount >= 0),
    CONSTRAINT order_items_total_amount_check CHECK (item_total_amount >= 0)
);

CREATE TABLE refunds (
    refund_id VARCHAR(20) PRIMARY KEY,
    order_id VARCHAR(20) NOT NULL,
    order_item_id VARCHAR(20) NOT NULL UNIQUE,
    refund_datetime TIMESTAMP NOT NULL,
    refund_amount INTEGER NOT NULL,
    refund_reason VARCHAR(50) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    CONSTRAINT refunds_order_id_fk
        FOREIGN KEY (order_id) REFERENCES orders (order_id),
    CONSTRAINT refunds_order_item_id_fk
        FOREIGN KEY (order_item_id) REFERENCES order_items (order_item_id),
    CONSTRAINT refunds_amount_check CHECK (refund_amount > 0),
    CONSTRAINT refunds_reason_check
        CHECK (refund_reason IN ('size_issue', 'defective', 'change_of_mind', 'delayed_delivery', 'wrong_item'))
);
