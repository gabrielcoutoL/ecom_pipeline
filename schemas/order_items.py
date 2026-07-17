import pandera.pandas as pa
from pandera.typing import DateTime, Int64, Series


class SilverOrderItems(pa.DataFrameModel):
    order_item_id: Series[str] = pa.Field(nullable=False, unique=True)

    order_id: Series[str] = pa.Field(nullable=False)

    product_id: Series[str] = pa.Field(nullable=False)

    seller_id: Series[str] = pa.Field(nullable=False)

    price: Series[float] = pa.Field(nullable=True, gt=0)

    freight_value: Series[float] = pa.Field(nullable=True, ge=0)

    quantity: Series[Int64] = pa.Field(nullable=True, gt=0)

    data_extracao: Series[DateTime] = pa.Field(nullable=False)
