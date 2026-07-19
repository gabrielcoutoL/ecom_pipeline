select
    product_id,
    category,
    product_name,
    base_price,
    weight_g
from {{ source('silver', 'products') }}