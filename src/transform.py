import logging

import pandas as pd

logger = logging.getLogger(__name__)

# FUNÇÕES COMUNS


def anula_data_futura(df: pd.DataFrame, col: str) -> pd.DataFrame:
    d = df.copy()

    fora = d[col] > pd.Timestamp.now()

    d.loc[fora, col] = pd.NaT

    logger.info("%s coluna anulando %d valores.", col, sum(fora))

    return d


def anula_valores_negativos(df: pd.DataFrame, col: str) -> pd.DataFrame:
    d = df.copy()

    negativos = d[col] < 0

    d.loc[negativos, col] = pd.NA

    logger.info("%s coluna anulando %d valores.", col, sum(negativos))

    return d


def valida_fk_orfas(df_direita: pd.DataFrame, df_esquerda: pd.DataFrame, col: str):
    d = df_direita.copy()

    ids_validos = set(df_esquerda[col])

    mask = d[col].isin(ids_validos)

    logger.info("%d valores setados para desconhecido", (~mask).sum())

    d.loc[~mask, col] = "Desconhecido"

    return d


# TRANSFORMAÇÕES DOS DATAFRAMES
def transform_customers(df_customers: pd.DataFrame) -> pd.DataFrame:

    return (
        df_customers.dropna(subset="customer_id")
        .drop_duplicates(subset="customer_id")
        .assign(
            customer_name=lambda d: d["customer_name"].str.strip().str.title(),
            city=lambda d: d["city"].str.strip().str.upper(),
            state=lambda d: d["state"].str.strip().str.upper(),
        )
        .fillna({"customer_name": "Desconhecido"})
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
        .pipe(anula_valores_negativos, col="price")
        .pipe(anula_valores_negativos, col="freight_value")
        .replace({"quantity": {0: pd.NA}})
        .reset_index(drop=True)
    )


def transform_orders(
    df_orders: pd.DataFrame, df_customers: pd.DataFrame
) -> pd.DataFrame:

    return (
        df_orders.dropna(subset="order_id")
        .drop_duplicates(subset="order_id")
        .pipe(valida_fk_orfas, df_esquerda=df_customers, col="customer_id")
        .assign(order_status=lambda d: d["order_status"].str.strip().str.title())
        .astype(
            {
                "order_id": str,
                "customer_id": str,
                "order_status": str,
                "purchase_ts": "datetime64[ns]",
                "data_extracao": "datetime64[ns]",
            }
        )
        .reset_index(drop=True)
    )
