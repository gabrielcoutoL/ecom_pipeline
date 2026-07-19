select
    customer_id,
    customer_name,
    email,
    city,
    state,
    created_at
from {{ source('silver', 'customers') }}