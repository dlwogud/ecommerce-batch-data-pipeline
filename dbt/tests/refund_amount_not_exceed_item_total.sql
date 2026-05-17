select
    refunds.refund_id,
    refunds.order_item_id,
    refunds.refund_amount,
    order_items.item_total_amount
from {{ ref('stg_refunds') }} as refunds
inner join {{ ref('stg_order_items') }} as order_items
    on refunds.order_item_id = order_items.order_item_id
where refunds.refund_amount > order_items.item_total_amount
