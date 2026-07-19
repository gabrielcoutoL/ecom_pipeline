select
    order_id,
    customer_id,
    order_status,
    purchase_ts,
    cast(purchase_ts as date) as dt_pedido
from {{ source('silver', 'orders') }}