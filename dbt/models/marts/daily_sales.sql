with orders_daily as (
    select
        order_datetime::date as sales_date,
        count(*) as order_count,
        sum(total_amount) as gross_sales
    from {{ ref('stg_orders') }}
    group by 1
),

refunds_daily as (
    select
        refund_datetime::date as sales_date,
        count(*) as refund_count,
        sum(refund_amount) as refund_amount
    from {{ ref('stg_refunds') }}
    group by 1
)

select
    coalesce(orders_daily.sales_date, refunds_daily.sales_date) as sales_date,
    coalesce(orders_daily.order_count, 0) as order_count,
    coalesce(orders_daily.gross_sales, 0) as gross_sales,
    coalesce(refunds_daily.refund_count, 0) as refund_count,
    coalesce(refunds_daily.refund_amount, 0) as refund_amount,
    coalesce(orders_daily.gross_sales, 0) - coalesce(refunds_daily.refund_amount, 0) as net_sales,
    case
        when coalesce(orders_daily.order_count, 0) = 0 then 0
        else coalesce(orders_daily.gross_sales, 0)::numeric / orders_daily.order_count
    end as average_order_amount
from orders_daily
full outer join refunds_daily
    on orders_daily.sales_date = refunds_daily.sales_date
