import uuid
from datetime import datetime

from sqlmodel import SQLModel, Field

from app.enums import CurrencyEnum
from app.models import ProductPriceHistoryBase


class ProductPriceHistoryCreate(ProductPriceHistoryBase):
    receipt_item_id: uuid.UUID
    product_id: uuid.UUID
    branch_id: uuid.UUID


class ProductPriceHistoryPublic(ProductPriceHistoryBase):
    id: uuid.UUID


class ProductsPriceHistoryPublic(SQLModel):
    data: list[ProductPriceHistoryPublic]
    count: int


class ProductPriceHistoryUpdate(SQLModel):
    price: float | None = Field(ge=0.0)
    currency: CurrencyEnum | None
    recorded_at: datetime | None = Field(default=None)
