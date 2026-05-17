select
    sales_date,
    gross_sales,
    refund_amount,
    net_sales
from {{ ref('daily_sales') }}
where net_sales != gross_sales - refund_amount
