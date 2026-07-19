select
    seller_id,
    seller_name,
    city,
    state
from {{ ref('stg_sellers') }}