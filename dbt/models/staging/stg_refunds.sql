select
    refund_id,
    order_id,
    order_item_id,
    refund_datetime,
    refund_amount,
    refund_reason,
    created_at,
    updated_at,
    loaded_at
from raw.refunds
