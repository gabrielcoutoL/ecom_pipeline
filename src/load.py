import awswrangler as wr
import pandas as pd


def salvar_parquet(
    df: pd.DataFrame,
    table_name: str,
    database: str,
    bucket_path: str,
    partition_cols=None,
    mode: str = "overwrite_partitions",
):
    wr.s3.to_parquet(
        df=df,
        path=bucket_path,
        dataset=True,
        partition_cols=partition_cols,
        mode=mode,
        database=database,
        table=table_name,
        athena_partition_projection_settings={
            "projection_enabled": True,
            "projection_types": {"data_extracao": "date"},
            "projection_ranges": {"data_extracao": "2026-01-01,NOW"},
            "projection_formats": {"data_extracao": "yyyy-MM-dd"},
        },
    )


def ler_parquet(bucket_path: str) -> pd.DataFrame:

    df = wr.s3.read_parquet(path=bucket_path, dataset=True)

    return df
