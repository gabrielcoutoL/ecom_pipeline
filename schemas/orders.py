import pandas as pd
import pandera.pandas as pa
from pandera.typing import DateTime, Series


def agora_utc() -> pd.Timestamp:
    return pd.Timestamp.now("UTC").tz_localize(None)


class SilverOrders(pa.DataFrameModel):
    order_id: Series[str] = pa.Field(nullable=False, unique=True)

    customer_id: Series[str] = pa.Field(nullable=False)

    order_status: Series[str] = pa.Field(
        nullable=False,
        isin=[
            "Created",
            "Approved",
            "Invoiced",
            "Shipped",
            "Delivered",
            "Canceled",
            "Desconhecido",
        ],
    )

    purchase_ts: Series[DateTime] = pa.Field(nullable=True)

    data_extracao: Series[str] = pa.Field(nullable=False)

    @pa.dataframe_check
    def data_nao_futura(cls, df: pd.DataFrame) -> Series[bool]:
        return df["purchase_ts"].isna() | (df["purchase_ts"] <= agora_utc())

    class Config:
        strict = True
        coerce = False
