select
    customer_id,
    customer_name,
    email,
    city,
    state,
    created_at
from {{ ref('stg_customers') }}

union all

--UNKNOWN MEMBERS
select
    'Desconhecido'            as customer_id,
    'Cliente Desconhecido'    as customer_name,
    null                      as email,
    null                      as city,
    null                      as state,
    null                      as created_at