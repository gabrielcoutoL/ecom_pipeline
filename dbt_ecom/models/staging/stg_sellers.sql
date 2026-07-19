select
    seller_id,
    seller_name,
    city,
    state
from {{ source('silver', 'sellers') }}