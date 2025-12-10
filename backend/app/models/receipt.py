import uuid
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class ReceiptBase(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax: float | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)


class Receipt(ReceiptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    store_id: uuid.UUID = Field(
        foreign_key="store.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptPublic(ReceiptBase):
    id: uuid.UUID
    user_id: uuid.UUID
    store_id: uuid.UUID


class ReceiptsPublic(SQLModel):
    data: list[ReceiptPublic]
    count: int


class ReceiptUpdate(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax: float | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
