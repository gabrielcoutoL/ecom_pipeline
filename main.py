import logging

from src.extract import extract_all
from src.load import salvar_parquet

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

ENDPOINTS: dict[str, dict] = {
    "customers": {"path": "customers", "page_size": 2000},
    "sellers": {"path": "sellers", "page_size": 2000},
    "products": {"path": "products", "page_size": 2000},
    "orders": {"path": "orders", "page_size": 2000},
    "order_items": {"path": "order_items", "page_size": 2000},
    "payments": {"path": "payments", "page_size": 2000},
}
PATH_BRONZE = "s3://lake-ecom-bronze-gclauar"


def run_bronze():

    for name, df in extract_all(endpoints=ENDPOINTS):
        salvar_parquet(
            df=df,
            bucket_path=f"{PATH_BRONZE}/{name}/",
            partition_cols=["data_extracao"],
            mode="overwrite_partitions",
            database="db_ecom_lake",
            table_name=name,
        )

        logging.info("Tabela %s salva: %d registros", name, len(df))


if __name__ == "__main__":
    run_bronze()
