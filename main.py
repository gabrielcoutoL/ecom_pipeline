import logging
from typing import Callable

import pandas as pd
import pandera.pandas as pa

from schemas.customers import SilverCustomers
from schemas.order_items import SilverOrderItems
from schemas.orders import SilverOrders
from schemas.payments import SilverPayments
from schemas.products import SilverProducts
from schemas.sellers import SilverSellers
from src.extract import extract_all
from src.load import ler_parquet, salvar_parquet
from src.transform import (
    transform_customers,
    transform_order_items,
    transform_orders,
    transform_payments,
    transform_products,
    transform_sellers,
)

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

logging.getLogger("botocore").setLevel(logging.WARNING)
logging.getLogger("boto3").setLevel(logging.WARNING)
logging.getLogger("awswrangler").setLevel(logging.WARNING)

# ---------------------------------------------------------------------------
# CONFIGURAÇÃO
# ---------------------------------------------------------------------------

ENDPOINTS: dict[str, dict] = {
    "customers": {"path": "customers", "page_size": 2000},
    "sellers": {"path": "sellers", "page_size": 2000},
    "products": {"path": "products", "page_size": 2000},
    "orders": {"path": "orders", "page_size": 2000},
    "order_items": {"path": "order_items", "page_size": 2000},
    "payments": {"path": "payments", "page_size": 2000},
}

PATH_BRONZE = "s3://lake-ecom-bronze-gclauar"
PATH_SILVER = "s3://lake-ecom-silver-gclauar"

DB_BRONZE = "db_ecom_bronze"
DB_SILVER = "db_ecom_silver"

SCHEMAS = {
    "customers": SilverCustomers,
    "sellers": SilverSellers,
    "products": SilverProducts,
    "orders": SilverOrders,
    "order_items": SilverOrderItems,
    "payments": SilverPayments,
}


# ---------------------------------------------------------------------------
# BRONZE
# ---------------------------------------------------------------------------


def run_bronze() -> None:
    """Extrai da API e grava o dado cru na bronze, sem transformar."""
    for name, df in extract_all(endpoints=ENDPOINTS):
        salvar_parquet(
            df=df,
            bucket_path=f"{PATH_BRONZE}/{name}/",
            partition_cols=["data_extracao"],
            mode="overwrite_partitions",
            database=DB_BRONZE,
            table_name=name,
        )
        logging.info("Bronze %s: %d registros", name, len(df))


# ---------------------------------------------------------------------------
# SILVER
# ---------------------------------------------------------------------------


def processa_silver(
    name: str, transform_fn: Callable[[pd.DataFrame], pd.DataFrame]
) -> pd.DataFrame:
    """Ciclo completo de uma tabela: lê bronze -> transforma -> valida -> grava silver.

    Fail-fast na validação: se o schema reprovar, é bug na transform — o pipeline
    para e loga o resumo das falhas, em vez de gravar dado inconsistente.
    """
    df_bronze = ler_parquet(bucket_path=f"{PATH_BRONZE}/{name}/")
    logging.info("Lido da bronze %s: %d registros", name, len(df_bronze))

    df_silver = transform_fn(df_bronze)

    try:
        SCHEMAS[name].validate(df_silver, lazy=True)
    except pa.errors.SchemaErrors as err:
        resumo = err.failure_cases.groupby(["column", "check"]).size()
        logging.error("Validação REPROVOU %s:\n%s", name, resumo)
        raise

    salvar_parquet(
        df=df_silver,
        bucket_path=f"{PATH_SILVER}/{name}/",
        partition_cols=["data_extracao"],
        mode="overwrite_partitions",
        database=DB_SILVER,
        table_name=name,
    )
    logging.info("Silver %s: %d registros", name, len(df_silver))

    return df_silver


def run_silver() -> None:
    """Processa a silver respeitando a ordem de dependência.

    As DIMENSÕES vêm primeiro porque os FATOS precisam delas para validar
    integridade referencial (FK órfã).
    """
    # --- dimensões ---
    df_customers = processa_silver("customers", transform_customers)
    processa_silver("sellers", transform_sellers)
    processa_silver("products", transform_products)

    # --- fatos ---
    processa_silver("orders", lambda df: transform_orders(df, df_customers))
    processa_silver("order_items", transform_order_items)
    processa_silver("payments", transform_payments)


# ---------------------------------------------------------------------------

if __name__ == "__main__":
    run_bronze()
    run_silver()
