import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.enums import CurrencyEnum


class ProductPriceHistoryBase(SQLModel):
    price: float = Field(ge=0.0)
    currency: CurrencyEnum = Field(default=CurrencyEnum.BAM)
    recorded_at: datetime = Field(default=None)


class ProductPriceHistory(ProductPriceHistoryBase, table=True):
    id: uuid.UUID = Field(primary_key=True)
    receipt_item_id: uuid.UUID = Field(
        foreign_key="receipt_item.id", nullable=False, ondelete="CASCADE"
    )
    product_id: uuid.UUID = Field(
        foreign_key="product.id", nullable=False, ondelete="CASCADE"
    )
    branch_id: uuid.UUID = Field(
        foreign_key="branch.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


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
