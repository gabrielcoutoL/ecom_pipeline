import pandas as pd
import pandera.pandas as pa
from pandera.typing import DateTime, Series


class SilverCustomers(pa.DataFrameModel):
    customer_id: Series[str] = pa.Field(nullable=False, unique=True)

    customer_name: Series[str] = pa.Field(nullable=False)

    email: Series[str] = pa.Field(nullable=False)

    city: Series[str] = pa.Field(nullable=False)

    state: Series[str] = pa.Field(nullable=False, str_matches=r"^[A-Z]{2}$")

    created_at: Series[DateTime] = pa.Field(nullable=True)

    data_extracao: Series[DateTime] = pa.Field(nullable=False)

    @pa.dataframe_check
    def data_nao_futura(cls, df: pd.DataFrame) -> Series[bool]:
        return df["created_at"].isna() | (df["created_at"] <= pd.Timestamp.now())
