{{
    config(
        materialized='table',
        format='parquet'
    )
}}

with pedidos as (

    select * from {{ ref('fct_orders') }}

)

select
    dt_pedido,
    count(*)                                                        as pedidos_total,
    count(*) filter (where order_status <> 'Canceled')              as pedidos_validos,
    count(*) filter (where order_status = 'Canceled')               as pedidos_cancelados,
    sum(qtd_itens) filter (where order_status <> 'Canceled')        as itens_vendidos,
    count(distinct customer_id) filter (where order_status <> 'Canceled')
    sum(valor_produtos) filter (where order_status <> 'Canceled')   as receita_produtos,
    sum(valor_frete)    filter (where order_status <> 'Canceled')   as receita_frete,
    sum(valor_pedido)   filter (where order_status <> 'Canceled')   as receita_total,
    sum(payment_value)  filter (where order_status <> 'Canceled')   as valor_pago,
    avg(valor_pedido)   filter (where order_status <> 'Canceled')   as ticket_medio,
    cast(count(*) filter (where order_status = 'Canceled') as double)
      / nullif(count(*), 0)                                         as taxa_cancelamento

from pedidos
group by dt_pedido