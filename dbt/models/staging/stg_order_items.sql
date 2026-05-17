select
    order_item_id,
    order_id,
    product_id,
    quantity,
    unit_price,
    discount_amount,
    item_total_amount,
    created_at,
    updated_at,
    loaded_at
from raw.order_items
