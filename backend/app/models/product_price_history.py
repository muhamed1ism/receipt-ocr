import uuid
from datetime import datetime, timezone

from sqlmodel import Column, DateTime, Field

from app.enums import CurrencyEnum

from .base import BaseModel


class ProductPriceHistoryBase(BaseModel):
    price: float = Field(ge=0.0)
    currency: CurrencyEnum = Field(default=CurrencyEnum.BAM)
    recorded_at: datetime = Field(
        sa_column=Column(DateTime(timezone=True), nullable=False)
    )


class ProductPriceHistory(ProductPriceHistoryBase, table=True):
    id: uuid.UUID = Field(primary_key=True)
    receipt_item_id: uuid.UUID = Field(
        foreign_key="receiptitem.id", nullable=False, ondelete="CASCADE"
    )
    product_id: uuid.UUID = Field(
        foreign_key="product.id", nullable=False, ondelete="CASCADE"
    )
    branch_id: uuid.UUID = Field(
        foreign_key="branch.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
