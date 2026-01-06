import uuid
from collections.abc import Sequence
from datetime import datetime, timezone

from sqlmodel import Field, SQLModel

from app.enums import CurrencyEnum
from app.models import ReceiptBase
from app.schemas.branch import BranchReceiptIn
from app.schemas.receipt_details import ReceiptDetailsReceiptIn
from app.schemas.receipt_item import (
    ReceiptItemCreate,
    ReceiptItemPublic,
)
from app.schemas.store import StoreReceiptIn


class ReceiptCreate(ReceiptBase):
    store: StoreReceiptIn
    branch: BranchReceiptIn
    details: ReceiptDetailsReceiptIn
    items: list[ReceiptItemCreate]


class ReceiptPublic(ReceiptBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ReceiptPublicWithItems(ReceiptPublic):
    items: list[ReceiptItemPublic] = []


class ReceiptsPublicWithItems(SQLModel):
    data: Sequence[ReceiptPublicWithItems]
    count: int


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
