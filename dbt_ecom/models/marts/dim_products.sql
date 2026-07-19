select
    product_id,
    category,
    product_name,
    base_price,
    weight_g
from {{ ref('stg_products') }}