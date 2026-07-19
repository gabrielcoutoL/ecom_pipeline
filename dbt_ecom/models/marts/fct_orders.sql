{{
    config(
        materialized='table',
        format='parquet'
    )
}}

with itens_agregados as (

    select
        order_id,
        count(*)                                 as qtd_itens,
        sum(price * quantity)                    as valor_produtos,
        sum(coalesce(freight_value, 0))          as valor_frete
    from {{ ref('stg_order_items') }}
    where price is not null
      and quantity is not null
    group by order_id

),

pedidos as (

    select
        order_id,
        customer_id,
        order_status,
        purchase_ts,
        dt_pedido
    from {{ ref('stg_orders') }}
    where purchase_ts is not null

),

pagamentos as (

    select
        order_id,
        payment_type,
        installments,
        payment_value
    from {{ ref('stg_payments') }}

)

select
    p.order_id,
    p.customer_id,
    p.order_status,
    p.purchase_ts,
    p.dt_pedido,
    coalesce(i.qtd_itens, 0)        as qtd_itens,
    coalesce(i.valor_produtos, 0)   as valor_produtos,
    coalesce(i.valor_frete, 0)      as valor_frete,
    coalesce(i.valor_produtos, 0)
      + coalesce(i.valor_frete, 0)  as valor_pedido,
    pg.payment_type,
    pg.installments,
    pg.payment_value

from pedidos p
left join itens_agregados i on p.order_id = i.order_id
left join pagamentos pg     on p.order_id = pg.order_id