import uuid
from datetime import datetime, timezone

from sqlmodel import Field, Relationship, SQLModel

from app.enums import CurrencyEnum
from app.models import ReceiptItem, StoreReceiptIn, BranchReceiptIn, ReceiptItemReceiptIn, ReceiptItemCreate


class ReceiptBase(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax_amount: float | None = Field(default=None)
    total_amount: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)
    currency: CurrencyEnum = Field(default=CurrencyEnum.BAM)


class Receipt(ReceiptBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(
        foreign_key="user.id", nullable=False, ondelete="CASCADE"
    )
    branch_id: uuid.UUID = Field(
        foreign_key="branch.id", nullable=False, ondelete="CASCADE"
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    items: list["ReceiptItem"] = Relationship(back_populates="receipt")


class ReceiptCreate(ReceiptBase):
    store: StoreReceiptIn
    branch: BranchReceiptIn
    items: list[ReceiptItemCreate]


class ReceiptPublic(ReceiptBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    items: list["ReceiptItem"] = []


class ReceiptsPublic(SQLModel):
    data: list[ReceiptPublic]
    count: int


class ReceiptUpdate(SQLModel):
    date_time: datetime | None = Field(default=None)
    tax: float | None = Field(default=None)
    total_price: float | None = Field(default=None)
    payment_method: str | None = Field(default=None, max_length=50)
    currency: CurrencyEnum | None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
