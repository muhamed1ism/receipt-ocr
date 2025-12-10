import uuid
from sqlmodel import SQLModel, Field
from datetime import datetime, timezone


class ReceiptItemBase(SQLModel):
    name: str = Field(max_length=255)
    quantity: float = Field(default=1.0, ge=0.0)
    price: float = Field(ge=0.0)
    total_price: float = Field(ge=0.0)


class ReceiptItem(ReceiptItemBase, table=True):
    id: uuid.UUID = Field(primary_key=True)
    receipt_id: uuid.UUID = Field(
        foreign_key="receipt.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemPublic(ReceiptItemBase):
    id: uuid.UUID
    receipt_id: uuid.UUID


class ReceiptItemsPublic(SQLModel):
    data: list[ReceiptItemPublic]
    count: int


class ReceiptItemUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    quantity: float | None = Field(default=None, ge=0.0)
    price: float | None = Field(default=None, ge=0.0)
    total_price: float | None = Field(default=None, ge=0.0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
