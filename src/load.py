import awswrangler as wr
import pandas as pd


def salvar_parquet(
    df: pd.DataFrame,
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
    )
