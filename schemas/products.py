import pandera.pandas as pa
from pandera.typing import DateTime, Int64, Series


class SilverProducts(pa.DataFrameModel):
    product_id: Series[str] = pa.Field(nullable=False, unique=True)

    category: Series[str] = pa.Field(
        nullable=False,
        isin=[
            "Moveis",
            "Casa",
            "Eletronicos",
            "Beleza",
            "Moda",
            "Brinquedos",
            "Livros",
            "Esporte",
            "Desconhecido",
        ],
    )

    product_name: Series[str] = pa.Field(nullable=False)

    base_price: Series[float] = pa.Field(nullable=True, gt=0)

    weight_g: Series[Int64] = pa.Field(nullable=False, gt=0)

    data_extracao: Series[DateTime] = pa.Field(nullable=False)

    class Config:
        strict = True
        coerce = False
