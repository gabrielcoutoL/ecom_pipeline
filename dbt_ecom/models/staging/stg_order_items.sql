select
    order_item_id,
    order_id,
    product_id,
    seller_id,
    price,
    freight_value,
    quantity
from {{ source('silver', 'order_items') }}