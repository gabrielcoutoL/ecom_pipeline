{{
    config(
        materialized='table',
        format='parquet'
    )
}}

with itens as (

    select
        order_item_id,
        order_id,
        product_id,
        seller_id,
        price,
        freight_value,
        quantity
    from {{ ref('stg_order_items') }}
    where price is not null
      and quantity is not null

),

pedidos as (

    select
        order_id,
        customer_id,
        order_status,
        dt_pedido
    from {{ ref('stg_orders') }}
    where purchase_ts is not null

)

select
    i.order_item_id,
    i.order_id,
    p.customer_id,
    i.product_id,
    i.seller_id,
    p.order_status,
    p.dt_pedido,
    i.price,
    i.freight_value,
    i.quantity,
    i.price * i.quantity                                as valor_item,
    i.price * i.quantity + coalesce(i.freight_value, 0) as valor_item_com_frete

from itens i
inner join pedidos p on i.order_id = p.order_id