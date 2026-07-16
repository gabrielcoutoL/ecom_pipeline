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

    d.loc[negativos, col] = pd.NaT

    logger.info("%s coluna anulando %d valores.", col, sum(negativos))

    return d


# TRANSFORMAÇÕES DOS DATAFRAMES
def transform_customers(df: pd.DataFrame) -> pd.DataFrame:

    return (
        df.dropna(subset="customer_id")
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


def transform_order_items(df: pd.DataFrame) -> pd.DataFrame:

    return (
        df.dropna(subset="order_item_id")
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
