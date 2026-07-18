import pandera.pandas as pa
from pandera.typing import DateTime, Int64, Series


class SilverPayments(pa.DataFrameModel):
    payment_id: Series[str] = pa.Field(nullable=False, unique=True)

    order_id: Series[str] = pa.Field(nullable=False)

    payment_type: Series[str] = pa.Field(
        nullable=False,
        isin=["Boleto", "Voucher", "Credit_Card", "Debit_Card", "Desconhecido"],
    )

    installments: Series[Int64] = pa.Field(nullable=True, ge=1)

    payment_value: Series[float] = pa.Field(nullable=True, gt=0)

    data_extracao: Series[DateTime] = pa.Field(nullable=False)

    class Config:
        strict = True
        coerce = False
