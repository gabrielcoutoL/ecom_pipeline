select
    payment_id,
    order_id,
    payment_type,
    installments,
    payment_value
from {{ source('silver', 'payments') }}