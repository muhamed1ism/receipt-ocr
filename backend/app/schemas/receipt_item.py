import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.models import ReceiptItemBase


class ReceiptItemCreate(ReceiptItemBase):
    pass


class ReceiptItemReceiptIn(ReceiptItemBase):
    pass


class ReceiptItemPublic(ReceiptItemBase):
    id: uuid.UUID
    # receipt_id: uuid.UUID


class ReceiptItemsPublic(SQLModel):
    data: list[ReceiptItemPublic] = []
    count: int


class ReceiptItemUpdate(SQLModel):
    name: str | None = Field(default=None, max_length=255)
    quantity: float | None = Field(default=None, ge=0.0)
    price: float | None = Field(default=None, ge=0.0)
    total_price: float | None = Field(default=None, ge=0.0)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
