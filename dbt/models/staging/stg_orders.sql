select
    order_id,
    customer_id,
    order_status,
    order_datetime,
    payment_method,
    total_amount,
    discount_amount,
    shipping_fee,
    created_at,
    updated_at,
    loaded_at
from raw.orders
