import uuid
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .receipt import Receipt


class ReceiptItemBase(SQLModel):
    name: str = Field(max_length=255)
    quantity: float = Field(default=1.0, ge=0.0)
    price: float = Field(ge=0.0)
    total_price: float = Field(ge=0.0)


class ReceiptItem(ReceiptItemBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    receipt_id: uuid.UUID = Field(
        foreign_key="receipt.id", nullable=False, ondelete="CASCADE"
    )
    product_id: uuid.UUID = Field(
        foreign_key="product.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    receipt: "Receipt" = Relationship(back_populates="items")
