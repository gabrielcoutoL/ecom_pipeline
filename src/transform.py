import logging

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# FUNÇÕES COMUNS
# ---------------------------------------------------------------------------


def anula_data_futura(df: pd.DataFrame, col: str) -> pd.DataFrame:
    d = df.copy()
    fora = d[col] > pd.Timestamp.now()
    d.loc[fora, col] = pd.NaT
    logger.info("%s: anulando %d datas futuras.", col, fora.sum())
    return d


def anula_valores_invalidos(
    df: pd.DataFrame, col: str, permite_zero: bool = True
) -> pd.DataFrame:
    """Anula (NA) valores negativos. Se permite_zero=False, anula <= 0."""
    d = df.copy()
    if permite_zero:
        invalidos = d[col] < 0
    else:
        invalidos = d[col] <= 0
    d.loc[invalidos, col] = pd.NA
    logger.info("%s: anulando %d valores inválidos.", col, invalidos.sum())
    return d


def valida_fk_orfas(
    df_direita: pd.DataFrame, df_esquerda: pd.DataFrame, col: str
) -> pd.DataFrame:
    d = df_direita.copy()
    ids_validos = set(df_esquerda[col])
    mask = d[col].isin(ids_validos)
    logger.info("%s: %d FKs órfãs setadas para Desconhecido.", col, (~mask).sum())
    d.loc[~mask, col] = "Desconhecido"
    return d


# ---------------------------------------------------------------------------
# TRANSFORMAÇÕES DOS DATAFRAMES
# ---------------------------------------------------------------------------


def transform_customers(df_customers: pd.DataFrame) -> pd.DataFrame:
    return (
        df_customers.dropna(subset="customer_id")
        .drop_duplicates(subset="customer_id")
        .astype(
            {
                "customer_id": str,
                "customer_name": str,
                "email": str,
                "city": str,
                "state": str,
                "created_at": "datetime64[ns]",
                "data_extracao": "datetime64[ns]",
            }
        )
        .assign(
            customer_name=lambda d: d["customer_name"].str.strip().str.title(),
            city=lambda d: d["city"].str.strip().str.upper(),
            state=lambda d: d["state"].str.strip().str.upper(),
        )
        .fillna({"customer_name": "Desconhecido"})
        .pipe(anula_data_futura, col="created_at")
        .reset_index(drop=True)
    )


def transform_order_items(df_order_items: pd.DataFrame) -> pd.DataFrame:
    return (
        df_order_items.dropna(subset="order_item_id")
        .drop_duplicates(subset="order_item_id")
        .astype(
            {
                "order_item_id": str,
                "order_id": str,
                "product_id": str,
                "seller_id": str,
                "price": float,
                "freight_value": float,
                "quantity": "Int64",
                "data_extracao": "datetime64[ns]",
            }
        )
        .pipe(anula_valores_invalidos, col="price", permite_zero=False)
        .pipe(anula_valores_invalidos, col="freight_value")
        .assign(quantity=lambda d: d["quantity"].where(d["quantity"] > 0, pd.NA))
        .reset_index(drop=True)
    )


def transform_orders(
    df_orders: pd.DataFrame, df_customers: pd.DataFrame
) -> pd.DataFrame:
    return (
        df_orders.dropna(subset="order_id")
        .drop_duplicates(subset="order_id")
        .astype(
            {
                "order_id": str,
                "customer_id": str,
                "order_status": "category",
                "purchase_ts": "datetime64[ns]",
                "data_extracao": "datetime64[ns]",
            }
        )
        .assign(order_status=lambda d: d["order_status"].str.strip().str.title())
        .pipe(valida_fk_orfas, df_esquerda=df_customers, col="customer_id")
        .reset_index(drop=True)
    )


def transform_payments(df_payments: pd.DataFrame) -> pd.DataFrame:
    return (
        df_payments.dropna(subset="payment_id")
        .drop_duplicates(subset="payment_id")
        .astype(
            {
                "payment_id": str,
                "order_id": str,
                "payment_type": "category",
                "installments": "Int64",
                "payment_value": float,
                "data_extracao": "datetime64[ns]",
            }
        )
        .replace({"payment_type": {"??": "Desconhecido"}})
        .pipe(anula_valores_invalidos, col="payment_value", permite_zero=False)
        .reset_index(drop=True)
    )


def transform_products(df_products: pd.DataFrame) -> pd.DataFrame:
    return (
        df_products.dropna(subset="product_id")
        .drop_duplicates(subset="product_id")
        .astype(
            {
                "product_id": str,
                "category": "category",
                "product_name": str,
                "base_price": float,
                "weight_g": "Int64",
                "data_extracao": "datetime64[ns]",
            }
        )
        .assign(
            category=lambda d: d["category"].str.strip().str.title(),
            product_name=lambda d: d["product_name"].str.strip().str.title(),
        )
        .fillna({"category": "Desconhecido"})
        .pipe(anula_valores_invalidos, col="base_price", permite_zero=False)
        .reset_index(drop=True)
    )


def transform_sellers(df_sellers: pd.DataFrame) -> pd.DataFrame:
    return (
        df_sellers.dropna(subset="seller_id")
        .drop_duplicates(subset="seller_id")
        .astype(
            {
                "seller_id": str,
                "seller_name": str,
                "city": str,
                "state": str,
                "data_extracao": "datetime64[ns]",
            }
        )
        .assign(
            seller_name=lambda d: d["seller_name"].str.strip().str.title(),
            city=lambda d: d["city"].str.strip().str.upper(),
            state=lambda d: d["state"].str.strip().str.upper(),
        )
        .reset_index(drop=True)
    )
