import pandera.pandas as pa
from pandera.typing import Series


class SilverSellers(pa.DataFrameModel):
    seller_id: Series[str] = pa.Field(nullable=False, unique=True)

    seller_name: Series[str] = pa.Field(nullable=False)

    city: Series[str] = pa.Field(nullable=False)

    state: Series[str] = pa.Field(nullable=False, str_matches=r"^[A-Z]{2}$")

    data_extracao: Series[str] = pa.Field(nullable=False)

    class Config:
        strict = True
        coerce = False
